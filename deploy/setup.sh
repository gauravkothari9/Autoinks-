#!/usr/bin/env bash
# Stick Reels setup for a fresh Ubuntu 24.04 server (AWS EC2).
#
#   sudo bash deploy/setup.sh <api-hostname> [public-site-url]
#   e.g. sudo bash deploy/setup.sh stick-reels.43-205-166-13.sslip.io https://stick-reels.vercel.app
#
# Shares the EC2 box with TurtleReels: Stick Reels listens on port 5001 and adds its own Caddy site
# file (/etc/caddy/sites/stick-reels.caddy) instead of replacing the Caddyfile.
#
# Installs Node 22, uv + Python, a virtual display (Xvfb) for turtle graphics, and Caddy for
# automatic HTTPS; runs the API as a systemd service. The web frontend is hosted on Vercel, which
# proxies /api and /media here. Safe to run again after updates.
set -euo pipefail

HOST="${1:?Usage: sudo bash deploy/setup.sh <hostname, e.g. 43-205-166-13.sslip.io>}"
PUBLIC_URL="${2:-https://$HOST}"   # where users open the site (Vercel); used for the Google redirect
PUBLIC_URL="${PUBLIC_URL%/}"
[[ $EUID -eq 0 ]] || { echo "Run with sudo"; exit 1; }
APP_USER="${SUDO_USER:-ubuntu}"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_DIR="$(getent passwd "$APP_USER" | cut -d: -f6)"
UV="$HOME_DIR/.local/bin/uv"
ENV_FILE="$APP_DIR/server/.env"
as_app() { sudo -u "$APP_USER" -H bash -lc "$1"; }

[[ -f "$ENV_FILE" ]] || { echo "Missing $ENV_FILE (copy your .env from the PC)"; exit 1; }

echo "==> System packages"
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  curl ca-certificates gnupg debian-keyring debian-archive-keyring apt-transport-https \
  xvfb xauth fonts-dejavu-core libx11-6 libxext6 libxrender1 libxft2 libxss1 libfontconfig1

echo "==> Swap (rendering needs headroom on 2 GB instances)"
if ! swapon --show | grep -q /swapfile; then
  fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
  grep -q '^/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo "==> Node.js 22"
if ! node -v 2>/dev/null | grep -q '^v22'; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
  apt-get install -y nodejs
fi

echo "==> Caddy (HTTPS)"
if ! command -v caddy >/dev/null; then
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor --yes -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
  apt-get update -y && apt-get install -y caddy
fi

echo "==> uv and the Python engine"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
[[ -x "$UV" ]] || as_app 'curl -LsSf https://astral.sh/uv/install.sh | sh'
as_app "cd '$APP_DIR' && '$UV' sync"

echo "==> Node packages (API only; the frontend is on Vercel)"
as_app "cd '$APP_DIR/server' && npm ci --omit=dev"

echo "==> Production settings in server/.env"
set_env() {
  if grep -q "^$1=" "$ENV_FILE"; then sed -i "s#^$1=.*#$1=$2#" "$ENV_FILE"; else echo "$1=$2" >> "$ENV_FILE"; fi
}
set_env PORT 5001                 # TurtleReels uses 5000 on the same box
set_env HOST 127.0.0.1
set_env CLIENT_URL ""
set_env SECURE_COOKIES true
set_env GOOGLE_REDIRECT_URI "$PUBLIC_URL/api/youtube/callback"
set_env TRUST_PROXY_HOPS 2        # Vercel -> Caddy -> app
set_env UV_BIN "$UV"
chown "$APP_USER:$APP_USER" "$ENV_FILE" && chmod 600 "$ENV_FILE"

echo "==> Smoke test: render a tiny Short on the virtual display"
as_app "cd '$APP_DIR' && xvfb-run -a '$UV' run python -m engine.render --category sword_duel --out /tmp/sr-smoke.mp4 \
  --width 270 --height 480 --fps 12 --draw-seconds 2 --hold-seconds 0.2" | tail -n 1
rm -f /tmp/sr-smoke.mp4 /tmp/sr-smoke.jpg

echo "==> systemd service"
cat > /etc/systemd/system/stick-reels.service <<EOF
[Unit]
Description=Stick Reels
After=network-online.target
Wants=network-online.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR/server
Environment=NODE_ENV=production
Environment=PATH=$HOME_DIR/.local/bin:/usr/local/bin:/usr/bin:/bin
# Python turtle needs a display; xvfb-run gives the app a virtual one.
ExecStart=/usr/bin/xvfb-run -a -s "-screen 0 1280x1024x24" /usr/bin/node --env-file-if-exists=.env src/index.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable stick-reels >/dev/null
systemctl restart stick-reels

echo "==> Caddy site for https://$HOST"
# Each app on this box owns one file in /etc/caddy/sites; the Caddyfile only imports them.
mkdir -p /etc/caddy/sites
cat > /etc/caddy/sites/stick-reels.caddy <<EOF
$HOST {
	encode gzip
	request_body {
		max_size 50MB
	}
	reverse_proxy 127.0.0.1:5001
}
EOF
touch /etc/caddy/Caddyfile
grep -q '^import sites/\*.caddy' /etc/caddy/Caddyfile || printf '\nimport sites/*.caddy\n' >> /etc/caddy/Caddyfile
caddy validate --adapter caddyfile --config /etc/caddy/Caddyfile >/dev/null
systemctl reload caddy 2>/dev/null || systemctl restart caddy

sleep 3
if systemctl is-active --quiet stick-reels; then
  echo
  echo "Stick Reels API is running: https://$HOST"
  echo "Logs:    sudo journalctl -u stick-reels -f"
  echo "Restart: sudo systemctl restart stick-reels"
else
  echo "The service did not start. See: sudo journalctl -u stick-reels -n 50"
  exit 1
fi
