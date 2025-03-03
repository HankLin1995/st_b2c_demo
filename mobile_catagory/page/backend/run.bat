@echo off
echo 正在啟動濠鮮嚴選API後端服務...
echo.
echo 使用Docker Compose啟動服務...
docker-compose up -d
echo.
echo 服務已啟動！
echo API運行在: http://localhost:8000
echo API文檔: http://localhost:8000/docs
echo.
echo 按任意鍵查看日誌，按Ctrl+C退出日誌查看...
pause > nul
docker-compose logs -f
