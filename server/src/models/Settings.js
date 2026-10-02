import mongoose from 'mongoose';
import { config } from '../config.js';

// Generated-music moods (engine/music.py MOODS). "auto" matches the mood to the video's style.
export const MUSIC_MOODS = ['calm', 'dreamy', 'upbeat', 'cosmic', 'epic', 'chase', 'sporty', 'funky', 'electro', 'workout', 'zen', 'quirky', 'elegant', 'rock', 'chill'];

// One settings document per user: tags, video defaults, music, and their YouTube connection.
const settingsSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, unique: true },
  userTags: { type: [String], default: [] },
  privacy: { type: String, enum: ['public', 'unlisted', 'private'], default: 'public' },
  drawSeconds: { type: Number, default: 55, min: 8, max: 90 },
  drawPace: { type: Number, default: 4 }, // which drawSeconds default this account has seen (see migrate.js)
  holdSeconds: { type: Number, default: 3, min: 0, max: 5 },
  hookText: { type: Boolean, default: true },
  musicMode: { type: String, enum: ['generated', 'library', 'off'], default: 'generated' },
  musicMood: { type: String, enum: ['auto', 'random', ...MUSIC_MOODS], default: 'auto' },
  categoryId: { type: String, default: '24' }, // YouTube "Entertainment"
  descriptionFooter: { type: String, default: '' },
  youtube: {
    tokens: { type: Object, default: null },
    channelId: String,
    channelTitle: String,
  },
});

export const Settings = mongoose.model('Settings', settingsSchema);

export async function getSettings(userId) {
  if (!userId) throw new Error('getSettings needs a userId');
  return Settings.findOneAndUpdate({ userId }, {}, { upsert: true, returnDocument: 'after', setDefaultsOnInsert: true });
}

export function publicSettings(s, { isAdmin = false, redirectUri } = {}) {
  const { youtube, ...rest } = s.toObject();
  delete rest._id;
  delete rest.__v;
  delete rest.userId;
  delete rest.drawPace;
  const { clientId, clientSecret } = config.google;
  const out = {
    ...rest,
    youtube: {
      configured: Boolean(clientId && clientSecret),
      connected: Boolean(youtube?.tokens),
      channelTitle: youtube?.channelTitle || null,
    },
  };
  if (isAdmin) {
    // Platform OAuth app details are only for the admin. The secret never leaves the server.
    Object.assign(out.youtube, {
      clientId: clientId || null,
      secretHint: clientSecret ? `••••${clientSecret.slice(-4)}` : null,
      redirectUri,
    });
  }
  return out;
}
