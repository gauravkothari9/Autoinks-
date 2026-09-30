import fs from 'node:fs';
import { google } from 'googleapis';
import { config } from '../config.js';
import { getSettings } from '../models/Settings.js';

const SCOPES = [
  'https://www.googleapis.com/auth/youtube.upload',
  'https://www.googleapis.com/auth/youtube.readonly',
];

// One Google OAuth app for the whole platform; each user connects their own channel through it.
export const isConfigured = () => Boolean(config.google.clientId && config.google.clientSecret);

/** The public callback URL: fixed by GOOGLE_REDIRECT_URI, or derived from the request (see api.js). */
function oauthClient(redirectUri) {
  return new google.auth.OAuth2(config.google.clientId, config.google.clientSecret, redirectUri);
}

/**
 * `state` ties the Google redirect back to the user who started it (prevents login CSRF).
 * `select_account` always shows Google's account/channel picker, so a user with several channels
 * picks the one to upload to instead of Google silently reusing the signed-in account.
 */
export function authUrl(state, redirectUri) {
  return oauthClient(redirectUri).generateAuthUrl({ access_type: 'offline', prompt: 'select_account consent', scope: SCOPES, state });
}

export async function handleCallback(userId, code, redirectUri) {
  const client = oauthClient(redirectUri);
  const { tokens } = await client.getToken(code);
  client.setCredentials(tokens);
  const { data } = await google.youtube({ version: 'v3', auth: client }).channels.list({ part: ['snippet'], mine: true });
  const channel = data.items?.[0];
  const settings = await getSettings(userId);
  settings.youtube = { tokens, channelId: channel?.id, channelTitle: channel?.snippet?.title || 'YouTube channel' };
  await settings.save();
}

async function authorizedClient(userId) {
  const settings = await getSettings(userId);
  if (!settings.youtube?.tokens) throw new Error('YouTube is not connected');
  const client = oauthClient();
  client.setCredentials(settings.youtube.tokens);
  // Persist refreshed access tokens (Google only sends refresh_token once).
  client.on('tokens', async (fresh) => {
    const s = await getSettings(userId);
    s.youtube.tokens = { ...s.youtube.tokens, ...fresh };
    s.markModified('youtube');
    await s.save();
  });
  return client;
}

/**
 * Upload a Short to the user's channel. With `publishAt` the video is uploaded private and
 * YouTube makes it public at that time on its own (publishAt requires privacyStatus private).
 */
export async function uploadShort({ userId, file, title, description, tags, privacy, publishAt, categoryId, onProgress }) {
  const auth = await authorizedClient(userId);
  const youtube = google.youtube({ version: 'v3', auth });
  const size = fs.statSync(file).size;
  const res = await youtube.videos.insert(
    {
      part: ['snippet', 'status'],
      notifySubscribers: true,
      requestBody: {
        snippet: { title, description, tags, categoryId },
        status: publishAt
          ? { privacyStatus: 'private', publishAt: publishAt.toISOString(), selfDeclaredMadeForKids: false }
          : { privacyStatus: privacy, selfDeclaredMadeForKids: false },
      },
      media: { body: fs.createReadStream(file) },
    },
    { onUploadProgress: (evt) => onProgress?.(Math.min(evt.bytesRead / size, 1)) },
  );
  return res.data.id;
}
