# Start Trading Bot Script
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting Crypto Trading Bot" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

$env:DJANGO_SETTINGS_MODULE = $null

$tradingBotPath = "c:\dev-projects\crypto-trading-bot"
$mainScript = Join-Path $tradingBotPath "main.py"

if (Test-Path $mainScript) {
    Set-Location $tradingBotPath
    
    Write-Host ""
    Write-Host "[OK] Found Trading Bot at: $tradingBotPath" -ForegroundColor Green
    Write-Host "[INFO] Starting Trading Bot (Testnet)..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "[INFO] Keep this window open!" -ForegroundColor Cyan
    Write-Host "[INFO] Press Ctrl+C to stop Trading Bot" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Run the trading bot
    python main.py
} else {
    Write-Host "[ERROR] Trading Bot script not found" -ForegroundColor Red
    Write-Host "Expected: $mainScript" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
