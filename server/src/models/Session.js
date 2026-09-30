import mongoose from 'mongoose';

// Only a SHA-256 of the cookie token is stored, so a database leak can't be replayed as a login.
const sessionSchema = new mongoose.Schema({
  tokenHash: { type: String, required: true, unique: true },
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, index: true },
  expiresAt: { type: Date, required: true },
});
sessionSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 }); // MongoDB deletes expired sessions

export const Session = mongoose.model('Session', sessionSchema);
