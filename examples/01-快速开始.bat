@echo off
chcp 65001 >nul
echo === fanqie-harvest 快速开始 ===
echo.
echo [1] 环境自检
python check.py
echo.
echo [2] 搜索书籍（示例：轮回）
python bookinfo.py search "轮回"
echo.
echo [3] 下一步：用上面返回的 book_id 执行
echo     python fanqie.py info ^<book_id^>
echo     python fanqie.py text ^<book_id^>
echo     python fanqie.py segments ^<book_id^>
pause