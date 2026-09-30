import { Router } from 'express';
import { User } from '../models/User.js';
import { claimOrphanData } from '../services/migrate.js';
import {
  endAllSessions, endSession, hashPassword, rateLimit, requireAuth, startSession, verifyPassword,
} from '../services/auth.js';
import { billingConfigured } from '../services/billing.js';
import { hasPaidAccess, planOf, usage } from '../services/plans.js';

const router = Router();
const wrap = (fn) => (req, res, next) => fn(req, res, next).catch(next);
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const ipKey = (req) => req.ip || req.socket.remoteAddress || 'unknown';

export async function account(user) {
  return {
    user: user.toJSON(),
    access: hasPaidAccess(user),
    plan: planOf(user)?.id || null,
    usage: await usage(user),
    billing: { configured: billingConfigured() },
  };
}

router.post('/signup', rateLimit((req) => `signup:${ipKey(req)}`, { max: 8 }), wrap(async (req, res) => {
  const name = String(req.body.name || '').trim().slice(0, 80);
  const email = String(req.body.email || '').trim().toLowerCase();
  const password = String(req.body.password || '');
  if (!name) return res.status(400).json({ error: 'Enter your name' });
  if (!EMAIL_RE.test(email) || email.length > 200) return res.status(400).json({ error: 'Enter a valid email address' });
  if (password.length < 8 || password.length > 200) return res.status(400).json({ error: 'Password must be at least 8 characters' });
  if (await User.exists({ email })) return res.status(409).json({ error: 'An account with this email already exists. Log in instead.' });

  // The very first account is the platform owner: admin, and it inherits data made before accounts existed.
  const first = (await User.estimatedDocumentCount()) === 0;
  const user = await User.create({ name, email, passwordHash: await hashPassword(password), role: first ? 'admin' : 'user' });
  if (first) await claimOrphanData(user._id);
  await startSession(res, user._id);
  res.status(201).json(await account(user));
}));

router.post('/login', rateLimit((req) => `login:${ipKey(req)}:${String(req.body?.email || '').toLowerCase()}`), wrap(async (req, res) => {
  const email = String(req.body.email || '').trim().toLowerCase();
  const user = await User.findOne({ email });
  // Same message whether the email or the password is wrong, so accounts can't be probed.
  if (!user || !(await verifyPassword(String(req.body.password || ''), user.passwordHash))) {
    return res.status(401).json({ error: 'Wrong email or password' });
  }
  await startSession(res, user._id);
  res.json(await account(user));
}));

router.post('/logout', wrap(async (req, res) => {
  await endSession(req, res);
  res.json({ ok: true });
}));

router.get('/me', requireAuth, wrap(async (req, res) => {
  res.json(await account(req.user));
}));

router.put('/password', requireAuth, rateLimit((req) => `pw:${req.user.id}`, { max: 5 }), wrap(async (req, res) => {
  const { current, next: nextPw } = req.body || {};
  if (!(await verifyPassword(String(current || ''), req.user.passwordHash))) {
    return res.status(400).json({ error: 'Current password is wrong' });
  }
  if (String(nextPw || '').length < 8) return res.status(400).json({ error: 'New password must be at least 8 characters' });
  req.user.passwordHash = await hashPassword(String(nextPw));
  await req.user.save();
  await endAllSessions(req.user._id); // sign out other devices
  await startSession(res, req.user._id);
  res.json({ ok: true });
}));

export default router;
