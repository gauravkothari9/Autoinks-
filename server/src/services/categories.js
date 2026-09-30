import fs from 'node:fs';
import path from 'node:path';
import { ROOT } from '../config.js';

// Single source of truth shared with the Python engine.
export const categories = JSON.parse(fs.readFileSync(path.join(ROOT, 'engine', 'categories.json'), 'utf8'));

export const categoryById = Object.fromEntries(categories.map((c) => [c.id, c]));

export function randomCategory() {
  return categories[Math.floor(Math.random() * categories.length)].id;
}
