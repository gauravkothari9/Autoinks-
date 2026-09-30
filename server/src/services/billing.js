import Razorpay from 'razorpay';
import { validatePaymentVerification, validateWebhookSignature } from 'razorpay/dist/utils/razorpay-utils.js';
import { config } from '../config.js';
import { BillingPlan } from '../models/BillingPlan.js';
import { User } from '../models/User.js';
import { INTERVALS, PLANS } from './plans.js';

export const billingConfigured = () => Boolean(config.razorpay.keyId && config.razorpay.keySecret);

let client = null;
function rzp() {
  if (!billingConfigured()) throw Object.assign(new Error('Payments are not set up yet'), { status: 503 });
  client ||= new Razorpay({ key_id: config.razorpay.keyId, key_secret: config.razorpay.keySecret });
  return client;
}

const rzpError = (err) => (err?.status ? err : Object.assign( // our own errors pass through unchanged
  new Error(err?.error?.description || err?.message || 'Razorpay request failed'),
  { status: 502, expose: true }, // payment provider problems are safe (and useful) to show
));
const toDate = (secs) => (secs ? new Date(secs * 1000) : undefined);

/** Razorpay plan id for plan+interval, created in Razorpay the first time it's needed. */
async function razorpayPlanId(plan, interval) {
  const amount = PLANS[plan][interval] * 100; // paise
  const key = `${plan}:${interval}:${amount}:${config.razorpay.keyId}`;
  const cached = await BillingPlan.findOne({ key });
  if (cached) return cached.razorpayPlanId;
  try {
    const created = await rzp().plans.create({
      period: interval,
      interval: 1,
      item: { name: `Stick Reels ${PLANS[plan].name} (${interval})`, amount, currency: 'INR' },
      notes: { plan, interval },
    });
    await BillingPlan.create({ key, razorpayPlanId: created.id });
    return created.id;
  } catch (err) {
    throw rzpError(err);
  }
}

/** Start a subscription; the browser completes payment in Razorpay Checkout. */
export async function createSubscription(user, plan, interval) {
  if (!PLANS[plan] || !INTERVALS.includes(interval)) throw Object.assign(new Error('Unknown plan'), { status: 400 });
  const planId = await razorpayPlanId(plan, interval);
  try {
    const sub = await rzp().subscriptions.create({
      plan_id: planId,
      total_count: interval === 'monthly' ? 120 : 10, // renews for up to 10 years unless cancelled
      customer_notify: 1,
      notes: { userId: String(user._id), plan, interval },
    });
    return {
      subscriptionId: sub.id,
      keyId: config.razorpay.keyId,
      name: 'Stick Reels',
      description: `${PLANS[plan].name} plan · ${interval}`,
      prefill: { name: user.name, email: user.email },
    };
  } catch (err) {
    throw rzpError(err);
  }
}

/**
 * Store a Razorpay subscription's state on its user. A different subscription that becomes
 * active replaces the old one (plan change), and the old one is cancelled in Razorpay.
 */
export async function applySubscription(sub) {
  const user = await User.findById(sub.notes?.userId).catch(() => null)
    || await User.findOne({ 'subscription.razorpayId': sub.id });
  if (!user) return null;
  const current = user.subscription || {};
  const isCurrent = current.razorpayId === sub.id;
  const activating = ['active', 'authenticated'].includes(sub.status);
  if (!isCurrent && !activating) return user; // stale event for a replaced subscription

  if (!isCurrent && current.razorpayId && ['active', 'authenticated', 'pending'].includes(current.status)) {
    await rzp().subscriptions.cancel(current.razorpayId, false).catch(() => {}); // switched plans
  }
  user.subscription = {
    plan: sub.notes?.plan || current.plan,
    interval: sub.notes?.interval || current.interval,
    status: sub.status,
    razorpayId: sub.id,
    currentStart: toDate(sub.current_start) || current.currentStart,
    currentEnd: toDate(sub.current_end) || current.currentEnd,
    cancelAtPeriodEnd: isCurrent ? Boolean(current.cancelAtPeriodEnd) : false,
  };
  await user.save();
  return user;
}

/** Called after Checkout succeeds: check Razorpay's signature, then pull the fresh state. */
export async function verifyCheckout(user, { razorpay_payment_id: paymentId, razorpay_subscription_id: subId, razorpay_signature: signature }) {
  const ok = paymentId && subId && signature && validatePaymentVerification(
    { payment_id: paymentId, subscription_id: subId }, signature, config.razorpay.keySecret,
  );
  if (!ok) throw Object.assign(new Error('Payment could not be verified'), { status: 400 });
  const sub = await rzp().subscriptions.fetch(subId).catch((err) => { throw rzpError(err); });
  if (sub.notes?.userId !== String(user._id)) throw Object.assign(new Error('Subscription belongs to another account'), { status: 403 });
  return applySubscription(sub);
}

export async function refreshSubscription(user) {
  if (!billingConfigured() || !user.subscription?.razorpayId) return user;
  const sub = await rzp().subscriptions.fetch(user.subscription.razorpayId).catch(() => null);
  return sub ? (await applySubscription(sub)) || user : user;
}

/** Cancel at the end of the paid period; access continues until then. */
export async function cancelSubscription(user) {
  const id = user.subscription?.razorpayId;
  if (!id) throw Object.assign(new Error('No active subscription'), { status: 400 });
  const sub = await rzp().subscriptions.cancel(id, true).catch((err) => { throw rzpError(err); });
  user.subscription.cancelAtPeriodEnd = true;
  user.subscription.status = sub.status || user.subscription.status;
  user.markModified('subscription');
  await user.save();
  return user;
}

/** Razorpay webhook: body must be the raw request bytes for the signature check. */
export async function handleWebhook(rawBody, signature) {
  if (!config.razorpay.webhookSecret) throw Object.assign(new Error('Webhook secret not set'), { status: 503 });
  const valid = signature && validateWebhookSignature(rawBody.toString('utf8'), signature, config.razorpay.webhookSecret);
  if (!valid) throw Object.assign(new Error('Invalid signature'), { status: 400 });
  const event = JSON.parse(rawBody.toString('utf8'));
  const sub = event.payload?.subscription?.entity;
  if (event.event?.startsWith('subscription.') && sub) await applySubscription(sub);
  return event.event;
}
