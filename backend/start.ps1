# 2026 世界杯 Dashboard — 启动脚本
# 用法: .\start.ps1

Write-Host "========================================" -ForegroundColor Green
Write-Host "  2026 世界杯 AI 预测 Dashboard" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 检查依赖
Write-Host "[1/2] 检查 Python 依赖..." -ForegroundColor Cyan
python -m pip install -r requirements.txt -q 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "请先安装依赖: pip install -r requirements.txt" -ForegroundColor Yellow
}

# 启动服务
Write-Host "[2/2] 启动 FastAPI 服务..." -ForegroundColor Cyan
Write-Host ""
Write-Host "  🏠 本地访问: http://localhost:8000" -ForegroundColor White
Write-Host "  📡 API 文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

# 尝试获取本机 IP
$ip = (Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp 2>$null | Select-Object -First 1).IPAddress
if ($ip) {
    Write-Host "  🌐 局域网分享: http://${ip}:8000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  === 公网分享（三选一） ===" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  A. ngrok (最简单):" -ForegroundColor White
    Write-Host "     1. 去 https://ngrok.com 注册下载" -ForegroundColor Gray
    Write-Host "     2. ngrok http 8000" -ForegroundColor Gray
    Write-Host "     3. 把生成的 https://xxx.ngrok.io 发给别人" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  B. Cloudflare Tunnel (免费+自定义域名):" -ForegroundColor White
    Write-Host "     1. cloudflared tunnel --url http://localhost:8000" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  C. 部署到 Railway/Render (永久在线):" -ForegroundColor White
    Write-Host "     把 backend/ 文件夹推送到 GitHub，在 Railway 导入即可" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "  按 Ctrl+C 停止服务" -ForegroundColor DarkYellow
Write-Host ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
