# Deploy Stick Reels to AWS (no domain needed)

## Not deployed yet

Stick Reels has no server of its own yet. The table below describes the server of the **original TurtleReels
project** this copy was made from. Don't point Stick Reels at it: it would overwrite that live site. Create a
new server with `node deploy\aws-provision.mjs` (it now uses the `stick-reels` names), then update
`deploy/update.ps1` (`$Server`, `$HostName`, `$PublicUrl`) and `client/vercel.json` with the new addresses.

### Original TurtleReels server (for reference)

| | |
|---|---|
| Instance | `i-0bd1dd65395010657`: t3.small, Ubuntu 24.04, **ap-south-1 (Mumbai)**, tag `app=turtlereels` |
| Fixed IP | `43.205.166.13` (Elastic IP) |
| API address | https://43-205-166-13.sslip.io: API only, HTTPS by Caddy + Let's Encrypt. `sslip.io` names resolve to the IP they contain, so no DNS account is needed. |
| Frontend | Vercel, deployed from GitHub (the `client/` folder). `client/vercel.json` forwards `/api` and `/media` to the API address. See `client/README.md`. |
| Public site | https://turtlereels.vercel.app (Vercel project `turtlereels`, GitHub `gauravkothari9/TurtleReels`) |
| Google redirect URI | `https://turtlereels.vercel.app/api/youtube/callback`. The server sets it from the second argument of `setup.sh`, which `update.ps1` passes as `$PublicUrl`. |
| SSH | `ssh -i "$env:USERPROFILE\.ssh\turtlereels.pem" ubuntu@43.205.166.13` |
| Firewall | `turtlereels-sg`: SSH from the admin PC's IP only; 80/443 open |
| Push code changes | `powershell -ExecutionPolicy Bypass -File deploy\update.ps1` |
| SSH times out after your IP changes | `node deploy\aws-provision.mjs` (adds your new IP; it reuses everything else) |

This server is separate from the incraftify.com server (`incraftify-web`, us-east-1). Neither affects the other.

The rest of this guide covers setting up from scratch by hand. `deploy/aws-provision.mjs` automates steps 1–5.

This guide gives you `https://<name>.duckdns.org`: a free hostname with automatic HTTPS. Once it runs, it keeps rendering and uploading scheduled Shorts while your PC is off.

## 1. Launch the server (AWS console, about 5 minutes)

1. Sign in at https://console.aws.amazon.com and pick the **Asia Pacific (Mumbai) ap-south-1** region (top right).
2. Go to **EC2 → Launch instance**:
   - **Name:** `stick-reels`
   - **Image:** **Ubuntu Server 24.04 LTS** (64-bit x86)
   - **Instance type:** **t3.small** (2 GB RAM). This is the minimum; rendering is heavy. Choose t3.medium if you expect many users.
   - **Key pair:** click **Create new key pair**, choose RSA and `.pem`, and save the file to e.g. `C:\Users\Owner\.ssh\stick-reels.pem`.
   - **Network settings:** allow **SSH** (set it to *My IP*), **HTTPS** and **HTTP** from the internet.
   - **Storage:** 30 GB gp3.
   - Click **Launch instance**.
3. Give it a fixed address: go to **EC2 → Elastic IPs → Allocate**, then **Actions → Associate** it with the `stick-reels` instance. Note this IP; the steps below call it `YOUR_IP`.

   A t3.small with 30 GB of storage costs roughly $17–20/month on demand in Mumbai. Check the current prices on the AWS pricing page.

## 2. Get a free hostname (DuckDNS, 2 minutes)

1. Open https://www.duckdns.org and sign in with Google or GitHub.
2. Type a subdomain, e.g. `stick-reels`, and click **add domain**.
3. In the **current ip** box, enter `YOUR_IP` and click **update ip**.

Your hostname is now `stick-reels.duckdns.org`. The steps below call it `YOUR_HOST`.

## 3. Let the server reach MongoDB Atlas

Go to Atlas → **Network Access** → **Add IP Address**, enter `YOUR_IP`, and click Confirm.

## 4. Upload the app (from your PC)

In PowerShell, from the project folder:

```powershell
powershell -ExecutionPolicy Bypass -File deploy\pack.ps1
scp -i C:\Users\Owner\.ssh\stick-reels.pem stick-reels-deploy.tar.gz ubuntu@YOUR_IP:~
```

If ssh complains that the key is "too open", run this once:
`icacls C:\Users\Owner\.ssh\stick-reels.pem /inheritance:r /grant:r "$($env:USERNAME):R"`

## 5. Install and start (on the server)

```powershell
ssh -i C:\Users\Owner\.ssh\stick-reels.pem ubuntu@YOUR_IP
```
Then, on the server:
```bash
mkdir -p ~/stick-reels && tar -xzf ~/stick-reels-deploy.tar.gz -C ~/stick-reels && rm ~/stick-reels-deploy.tar.gz
cd ~/stick-reels && sudo bash deploy/setup.sh YOUR_HOST
```
The setup takes about 5–10 minutes. It ends with **Stick Reels is running: https://YOUR_HOST**.

Delete `stick-reels-deploy.tar.gz` from your PC afterwards, because it contains your secrets.

## 6. Point Google and Razorpay at the new address

- **Google Cloud Console → APIs & Services → Credentials →** your OAuth client:
  - Add `https://YOUR_HOST/api/youtube/callback` under *Authorized redirect URIs*. Keep the localhost one for local testing.
  - If Google asks for an authorized domain on the **OAuth consent screen**, add `YOUR_HOST`.
- Open `https://YOUR_HOST`, log in, and go to **Profile → Connect YouTube** again. The connection you made on localhost used the old address.
- **Razorpay → Webhooks:** set the URL to `https://YOUR_HOST/api/billing/webhook` and choose the `subscription.*` events.
  - Put the same secret in `RAZORPAY_WEBHOOK_SECRET` in `~/stick-reels/server/.env`.
  - Then run `sudo systemctl restart stick-reels`.

## Updating later

On your PC, run `deploy\pack.ps1` and `scp` the file again. Then on the server:
```bash
cd ~/stick-reels && tar -xzf ~/stick-reels-deploy.tar.gz --exclude=server/.env --exclude=media && sudo bash deploy/setup.sh YOUR_HOST
```
The two `--exclude` flags keep the server's own `.env` and its videos.

## Useful commands (on the server)

| What | Command |
|---|---|
| Live logs | `sudo journalctl -u stick-reels -f` |
| Restart the app | `sudo systemctl restart stick-reels` |
| App status | `systemctl status stick-reels` |
| HTTPS / Caddy logs | `sudo journalctl -u caddy -n 50` |
| Edit settings | `nano ~/stick-reels/server/.env`, then restart |

## Notes

- **Stop running Stick Reels on your PC** once the server is live. Both copies share the same Atlas database, so both would run the schedules and could upload the same slot twice.
- **Videos live on the server's disk** in `~/stick-reels/media`. For backups, take an EBS snapshot (EC2 → Volumes → Create snapshot).
- **DuckDNS** is free and fine for launch. When you buy a domain later, point it at `YOUR_IP` and re-run `setup.sh` with the new name. Then update the Google and Razorpay URLs again.
