import mongoose from 'mongoose';
import { Job } from '../models/Job.js';
import { Schedule } from '../models/Schedule.js';

/** Schema changes from the single-user version. Safe to run on every start. */
export async function migrate() {
  const settings = mongoose.connection.db.collection('settings');
  const indexes = await settings.indexes().catch(() => []);
  if (indexes.some((i) => i.name === 'key_1')) await settings.dropIndex('key_1'); // old singleton key
  // Drawings got slower (default 20s, then 40s, now 55s): accounts still on an old default move to 55s, once.
  const before = { $or: [{ drawPace: { $exists: false } }, { drawPace: { $lt: 3 } }] };
  await settings.updateMany({ ...before, drawSeconds: { $in: [20, 40, null] } }, { $set: { drawSeconds: 55 } });
  await settings.updateMany(before, { $set: { drawPace: 3 } });
  // Every account draws at least 55s, once (users can lower it again afterwards).
  await settings.updateMany({ drawPace: 3, drawSeconds: { $lt: 55 } }, { $set: { drawSeconds: 55 } });
  await settings.updateMany({ drawPace: 3 }, { $set: { drawPace: 4 } });
}

/** Give Shorts, schedules and settings created before accounts existed to the first (admin) user. */
export async function claimOrphanData(userId) {
  await Job.updateMany({ kind: 'video', userId: null }, { $set: { userId } });
  await Schedule.collection.updateMany({ userId: { $exists: false } }, { $set: { userId } });
  await mongoose.connection.db.collection('settings')
    .updateOne({ userId: { $exists: false } }, { $set: { userId }, $unset: { key: '', autoUpload: '', music: '' } });
}
