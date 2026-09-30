# Bundle Stick Reels for upload to the server.
# Run from anywhere:  powershell -ExecutionPolicy Bypass -File deploy\pack.ps1
# Creates stick-reels-deploy.tar.gz in the project folder. It contains server/.env (your secrets),
# so only copy it to your own server and delete it afterwards.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
try {
    $out = 'stick-reels-deploy.tar.gz'
    if (Test-Path $out) { Remove-Item $out -Force }
    tar -czf $out `
        --exclude=node_modules --exclude=.venv --exclude=client/dist --exclude=__pycache__ `
        --exclude=media/music-samples --exclude=server/.env.local-backup --exclude=$out `
        engine server client media deploy pyproject.toml uv.lock README.md
    $size = [math]::Round((Get-Item $out).Length / 1MB, 1)
    Write-Host "Created $root\$out ($size MB)"
} finally {
    Pop-Location
}
