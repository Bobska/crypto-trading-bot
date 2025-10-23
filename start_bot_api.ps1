# Start Trading Bot API Server
# This provides the REST API and WebSocket endpoint for bot communication

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🚀 Starting Trading Bot API Server" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

# Clear any existing Django settings environment variable
$env:DJANGO_SETTINGS_MODULE = $null
Write-Host "✅ Cleared DJANGO_SETTINGS_MODULE environment variable" -ForegroundColor Yellow

# Navigate to trading bot directory
Set-Location "c:\dev-projects\crypto-trading-bot"

Write-Host ""
Write-Host "API Server: http://localhost:8002" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8002/docs" -ForegroundColor Cyan
Write-Host "WebSocket: ws://localhost:8002/ws" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Start Bot API
python bot_api.py
