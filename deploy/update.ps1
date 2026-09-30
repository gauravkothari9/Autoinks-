# Push code changes to the live Stick Reels server and restart it.
#   powershell -ExecutionPolicy Bypass -File deploy\update.ps1
# Keeps the server's own .env and media (videos, music) untouched.
$ErrorActionPreference = 'Stop'
$Server = 'ubuntu@43.205.166.13'
$HostName = '43-205-166-13.sslip.io'   # API address (Vercel proxies to it)
$PublicUrl = 'https://stick-reels.vercel.app'   # the site users open
$Key = "$env:USERPROFILE\.ssh\stick-reels.pem"
$opt = @('-i', $Key, '-o', 'ConnectTimeout=20', '-o', 'BatchMode=yes')
$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
try {
    $r = & ssh @opt $Server 'echo ok' 2>$null
    if ($r -ne 'ok') {
        $ip = (Invoke-WebRequest 'https://checkip.amazonaws.com' -UseBasicParsing -TimeoutSec 10).Content.Trim()
        throw "Cannot SSH to $Server. If your home IP changed (now $ip), re-run: node deploy\aws-provision.mjs (it adds the new IP to the firewall)."
    }
    $out = 'stick-reels-update.tar.gz'
    tar -czf $out --exclude=node_modules --exclude=.venv --exclude=client/dist --exclude=__pycache__ `
        --exclude=server/.env --exclude=server/.env.local-backup engine server deploy pyproject.toml uv.lock README.md
    & scp @opt $out "${Server}:~/"
    Remove-Item $out -Force
    & ssh @opt $Server "tar -xzf ~/$out -C ~/stick-reels && rm ~/$out && cd ~/stick-reels && sudo bash deploy/setup.sh $HostName $PublicUrl"
    if ($LASTEXITCODE -ne 0) { throw 'Remote setup failed (see output above)' }
    Write-Host "`nAPI updated: https://$HostName (frontend deploys from GitHub via Vercel)" -ForegroundColor Green
} finally {
    Pop-Location
}
