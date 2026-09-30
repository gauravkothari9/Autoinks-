import fs from 'node:fs';
import path from 'node:path';
import { ROOT } from '../config.js';

const ENV_PATH = path.join(ROOT, 'server', '.env');

/**
 * Set KEY=value lines in server/.env, keeping every other line (and comments) as-is.
 * Callers must pass values without newlines; this only writes, it does not validate.
 */
export function updateEnvFile(values) {
  const lines = fs.existsSync(ENV_PATH) ? fs.readFileSync(ENV_PATH, 'utf8').split(/\r?\n/) : [];
  const pending = new Map(Object.entries(values));
  const out = lines.map((line) => {
    const key = line.match(/^\s*([A-Z0-9_]+)\s*=/)?.[1];
    if (!key || !pending.has(key)) return line;
    const value = pending.get(key);
    pending.delete(key);
    return `${key}=${value}`;
  });
  for (const [key, value] of pending) out.push(`${key}=${value}`);
  while (out.length && out[out.length - 1] === '') out.pop();
  fs.writeFileSync(ENV_PATH, `${out.join('\n')}\n`);
}
