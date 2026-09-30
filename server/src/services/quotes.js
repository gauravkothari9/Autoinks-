import fs from 'node:fs';
import path from 'node:path';
import { ROOT } from '../config.js';
import { Job } from '../models/Job.js';

const QUOTES = JSON.parse(fs.readFileSync(path.join(ROOT, 'engine', 'quotes.json'), 'utf8'));

/** A random quote that none of the most recent Shorts used, so every reel gets a new one. */
export async function pickQuote(userId) {
  const window = Math.min(100, QUOTES.length - 1);
  const recent = await Job.find({ kind: 'video', userId, hook: { $ne: null } })
    .sort({ createdAt: -1 }).limit(window).select('hook').lean();
  const used = new Set(recent.map((j) => j.hook));
  const fresh = QUOTES.filter((q) => !used.has(q));
  const pool = fresh.length ? fresh : QUOTES;
  return pool[Math.floor(Math.random() * pool.length)];
}
