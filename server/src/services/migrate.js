import mongoose from 'mongoose';
import { Job } from '../models/Job.js';
import { Schedule } from '../models/Schedule.js';

/** Schema changes from the single-user version. Safe to run on every start. */
export async function migrate() {
  const settings = mongoose.connection.db.collection('settings');
  const indexes = await settings.indexes().catch(() => []);
  if (indexes.some((i) => i.name === 'key_1')) await settings.dropIndex('key_1'); // old singleton key
  // Drawings got 2x slower: accounts still on the old 20s default move to the new 40s default, once.
  await settings.updateMany({ drawPace: { $exists: false }, drawSeconds: { $in: [20, null] } }, { $set: { drawSeconds: 40 } });
  await settings.updateMany({ drawPace: { $exists: false } }, { $set: { drawPace: 2 } });
}

/** Give Shorts, schedules and settings created before accounts existed to the first (admin) user. */
export async function claimOrphanData(userId) {
  await Job.updateMany({ kind: 'video', userId: null }, { $set: { userId } });
  await Schedule.collection.updateMany({ userId: { $exists: false } }, { $set: { userId } });
  await mongoose.connection.db.collection('settings')
    .updateOne({ userId: { $exists: false } }, { $set: { userId }, $unset: { key: '', autoUpload: '', music: '' } });
}
