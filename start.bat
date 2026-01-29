@echo off
chcp 65001 >nul

rem AI文件管理工具启动脚本
rem 版本: 1.0.0
rem 功能: 检查Python环境、安装依赖、启动主程序

echo ========================================
echo         AI文件管理工具启动器
echo ========================================
echo.

rem 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境
    echo 请先安装Python 3.8或更高版本
    echo.
    echo 可以从以下网址下载:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo 找到Python环境

rem 检查依赖是否需要安装
if not exist ".installed" (
    echo 首次运行，正在安装依赖...
    echo.

    rem 安装依赖
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 错误: 依赖安装失败
        echo 请检查网络连接或手动安装依赖
        echo.
        pause
        exit /b 1
    )

    rem 创建安装标记文件
    echo 依赖安装成功 > .installed
    echo.
)

echo 依赖检查完成

rem 启动主程序 (默认启动GUI界面)
echo 正在启动AI文件管理工具...
echo.
echo 提示: 按 Ctrl+C 退出程序
echo.
python -c "from src.gui import run_gui; run_gui()"

rem 检查程序退出状态
if %errorlevel% neq 0 (
    echo.
    echo 错误: 程序启动失败
    echo 请检查错误信息并尝试解决
    echo.
    pause
    exit /b 1
)

echo.
echo 程序已退出
pause
