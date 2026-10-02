# Push code changes to the live Autoinks server and restart it.
#   powershell -ExecutionPolicy Bypass -File deploy\update.ps1 [-PublicUrl https://your-site.vercel.app]
# Autoinks has its own EC2 box (created by deploy\aws-provision.mjs), app in ~/autoinks.
# Keeps the server's own .env and media (videos, music) untouched. The first run copies server/.env over.
param(
    [string]$PublicUrl = 'https://autoinks.vercel.app'   # the site users open (Vercel); used for the Google redirect
)
$ErrorActionPreference = 'Stop'
$Server = 'ubuntu@13.232.17.220'
$HostName = 'autoinks.13-232-17-220.sslip.io'   # API address (Vercel proxies to it)
$Key = "$env:USERPROFILE\.ssh\autoinks.pem"
$opt = @('-i', $Key, '-o', 'ConnectTimeout=20', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=accept-new')
$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
try {
    $r = & ssh @opt $Server 'echo ok' 2>$null
    if ($r -ne 'ok') {
        $ip = (Invoke-WebRequest 'https://checkip.amazonaws.com' -UseBasicParsing -TimeoutSec 10).Content.Trim()
        throw "Cannot SSH to $Server. If your home IP changed (now $ip), re-run node deploy\aws-provision.mjs (it adds the new IP to the firewall)."
    }
    & ssh @opt $Server 'mkdir -p ~/autoinks/server'
    & ssh @opt $Server 'test -f ~/autoinks/server/.env'
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'First deploy: copying server/.env' -ForegroundColor Yellow
        & scp @opt 'server/.env' "${Server}:~/autoinks/server/.env"
    }
    $out = 'autoinks-update.tar.gz'
    tar -czf $out --exclude=node_modules --exclude=.venv --exclude=client/dist --exclude=__pycache__ `
        --exclude='server/.env' --exclude='server/.env.*' engine server deploy pyproject.toml uv.lock README.md
    & scp @opt $out "${Server}:~/"
    Remove-Item $out -Force
    & ssh @opt $Server "tar -xzf ~/$out -C ~/autoinks && rm ~/$out && cd ~/autoinks && sudo bash deploy/setup.sh $HostName $PublicUrl"
    if ($LASTEXITCODE -ne 0) { throw 'Remote setup failed (see output above)' }
    Write-Host "`nAPI updated: https://$HostName (frontend deploys from GitHub via Vercel)" -ForegroundColor Green
} finally {
    Pop-Location
}
