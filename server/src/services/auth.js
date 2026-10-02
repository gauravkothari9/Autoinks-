import crypto from 'node:crypto';
import { promisify } from 'node:util';
import { config } from '../config.js';
import { Session } from '../models/Session.js';
import { User } from '../models/User.js';
import { hasPaidAccess } from './plans.js';

const scrypt = promisify(crypto.scrypt);
const COOKIE = config.sessionCookie;
const SESSION_DAYS = 30;
const KEYLEN = 64;

// --- passwords (scrypt, per-user salt) --------------------------------------
export async function hashPassword(password) {
  const salt = crypto.randomBytes(16);
  const key = await scrypt(password, salt, KEYLEN, { N: 16384, r: 8, p: 1 });
  return `scrypt$${salt.toString('base64')}$${key.toString('base64')}`;
}

export async function verifyPassword(password, stored) {
  const [scheme, saltB64, keyB64] = String(stored).split('$');
  if (scheme !== 'scrypt' || !saltB64 || !keyB64) return false;
  const expected = Buffer.from(keyB64, 'base64');
  const key = await scrypt(password, Buffer.from(saltB64, 'base64'), expected.length, { N: 16384, r: 8, p: 1 });
  return crypto.timingSafeEqual(key, expected);
}

// --- sessions ----------------------------------------------------------------
const sha256 = (s) => crypto.createHash('sha256').update(s).digest('hex');

function readCookie(req, name) {
  for (const part of (req.headers.cookie || '').split(';')) {
    const [k, ...v] = part.trim().split('=');
    if (k === name) return decodeURIComponent(v.join('='));
  }
  return null;
}

function cookieHeader(value, maxAgeSec) {
  return [
    `${COOKIE}=${encodeURIComponent(value)}`, 'Path=/', 'HttpOnly', 'SameSite=Lax', `Max-Age=${maxAgeSec}`,
    ...(config.secureCookies ? ['Secure'] : []),
  ].join('; ');
}

export async function startSession(res, userId) {
  const token = crypto.randomBytes(32).toString('base64url');
  await Session.create({ tokenHash: sha256(token), userId, expiresAt: new Date(Date.now() + SESSION_DAYS * 86400000) });
  res.setHeader('Set-Cookie', cookieHeader(token, SESSION_DAYS * 86400));
}

export async function endSession(req, res) {
  const token = readCookie(req, COOKIE);
  if (token) await Session.deleteOne({ tokenHash: sha256(token) });
  res.setHeader('Set-Cookie', cookieHeader('', 0));
}

export async function endAllSessions(userId) {
  await Session.deleteMany({ userId });
}

/** Attaches req.user when a valid session cookie is present. Never rejects. */
export async function loadUser(req, _res, next) {
  try {
    const token = readCookie(req, COOKIE);
    if (token) {
      const session = await Session.findOne({ tokenHash: sha256(token), expiresAt: { $gt: new Date() } });
      if (session) req.user = await User.findById(session.userId);
    }
    next();
  } catch (err) {
    next(err);
  }
}

export function requireAuth(req, res, next) {
  if (!req.user) return res.status(401).json({ error: 'Please log in', code: 'auth' });
  next();
}

export function requireAdmin(req, res, next) {
  if (req.user?.role !== 'admin') return res.status(403).json({ error: 'Admins only' });
  next();
}

export function requirePlan(req, res, next) {
  if (!hasPaidAccess(req.user)) {
    return res.status(402).json({ error: 'This needs an active Autoinks plan', code: 'plan' });
  }
  next();
}

// --- brute-force protection for login/signup ------------------------------------------
const attempts = new Map(); // key -> { count, resetAt }
export function rateLimit(keyFn, { max = 10, windowMs = 15 * 60 * 1000 } = {}) {
  return (req, res, next) => {
    const key = keyFn(req);
    const now = Date.now();
    const entry = attempts.get(key);
    if (!entry || entry.resetAt < now) attempts.set(key, { count: 1, resetAt: now + windowMs });
    else if (++entry.count > max) {
      res.setHeader('Retry-After', Math.ceil((entry.resetAt - now) / 1000));
      return res.status(429).json({ error: 'Too many attempts. Try again in a few minutes.' });
    }
    next();
  };
}
setInterval(() => {
  const now = Date.now();
  for (const [k, v] of attempts) if (v.resetAt < now) attempts.delete(k);
}, 10 * 60 * 1000).unref();
