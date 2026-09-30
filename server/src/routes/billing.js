import express, { Router } from 'express';
import { requireAuth } from '../services/auth.js';
import {
  billingConfigured, cancelSubscription, createSubscription, handleWebhook, refreshSubscription, verifyCheckout,
} from '../services/billing.js';
import { publicPlans } from '../services/plans.js';
import { account } from './auth.js';

const router = Router();
const wrap = (fn) => (req, res, next) => fn(req, res, next).catch(next);

router.get('/plans', (_req, res) => {
  res.json({ plans: publicPlans(), currency: 'INR', configured: billingConfigured() });
});

router.post('/subscribe', requireAuth, wrap(async (req, res) => {
  res.json(await createSubscription(req.user, req.body.plan, req.body.interval));
}));

router.post('/verify', requireAuth, wrap(async (req, res) => {
  const user = await verifyCheckout(req.user, req.body || {});
  res.json(await account(user));
}));

router.post('/refresh', requireAuth, wrap(async (req, res) => {
  res.json(await account(await refreshSubscription(req.user)));
}));

router.post('/cancel', requireAuth, wrap(async (req, res) => {
  res.json(await account(await cancelSubscription(req.user)));
}));

export default router;

// Mounted before express.json(): the signature is computed over the exact raw bytes.
export const webhook = [
  express.raw({ type: 'application/json', limit: '1mb' }),
  wrap(async (req, res) => {
    const event = await handleWebhook(req.body, req.get('x-razorpay-signature'));
    res.json({ ok: true, event });
  }),
];
