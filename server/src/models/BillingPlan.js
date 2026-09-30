import mongoose from 'mongoose';

// Razorpay plan ids created on demand, one per plan/interval/price combination.
const billingPlanSchema = new mongoose.Schema({
  key: { type: String, required: true, unique: true }, // e.g. "pro:monthly:120000:rzp_test_x"
  razorpayPlanId: { type: String, required: true },
});

export const BillingPlan = mongoose.model('BillingPlan', billingPlanSchema);
