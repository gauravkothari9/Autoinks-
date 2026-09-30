import mongoose from 'mongoose';

const userSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, trim: true, maxlength: 80 },
    email: { type: String, required: true, unique: true, lowercase: true, trim: true, maxlength: 200 },
    passwordHash: { type: String, required: true },
    role: { type: String, enum: ['user', 'admin'], default: 'user' },
    trialUsed: { type: Boolean, default: false }, // the one free watermarked Short
    subscription: {
      plan: { type: String, enum: ['basic', 'pro', 'max', null], default: null },
      interval: { type: String, enum: ['monthly', 'yearly', null], default: null },
      // Razorpay subscription states: created, authenticated, active, pending, halted, cancelled, completed, expired
      status: { type: String, default: 'none' },
      razorpayId: String,
      currentStart: Date,
      currentEnd: Date,
      cancelAtPeriodEnd: { type: Boolean, default: false },
    },
    oauthState: String, // anti-CSRF value for the YouTube connect flow
  },
  { timestamps: true },
);

userSchema.set('toJSON', {
  transform: (_doc, ret) => {
    ret.id = ret._id;
    delete ret._id;
    delete ret.__v;
    delete ret.passwordHash;
    delete ret.oauthState;
    return ret;
  },
});

export const User = mongoose.model('User', userSchema);
