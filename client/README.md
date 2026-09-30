# Stick Reels web app

The React (Vite) frontend of Stick Reels. It is hosted on **Vercel**, deployed from GitHub. The API runs on AWS; Vercel forwards `/api/*` and `/media/*` to it (see `vercel.json`), so the browser only ever talks to your Vercel address and login cookies work normally.

## Deploy (GitHub → Vercel)

1. Push this `client` folder to a GitHub repository. `node_modules` and `dist` are ignored.
2. On https://vercel.com, click **Add New… → Project**, import the repository, and click **Deploy**. Framework, build command (`npm run build`) and output folder (`dist`) are read from `vercel.json`, so there's nothing to fill in.
3. Note your address, e.g. `https://stick-reels.vercel.app`. In **Google Cloud → Credentials → OAuth client**, add this under *Authorized redirect URIs*:
   `https://<your-app>.vercel.app/api/youtube/callback`
4. Open the site, log in, and go to **Profile → Connect YouTube**.

Every push to the main branch redeploys automatically.

## If the API server's address changes

Edit the two `destination` URLs in `vercel.json` (currently `https://43-205-166-13.sslip.io`) and push.

## Local development

```bash
npm install
npm run dev        # http://localhost:5173. /api and /media go to http://localhost:5000 (vite.config.js)
```
