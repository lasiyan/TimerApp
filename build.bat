@echo off
chcp 65001 >nul
echo =======================================
echo   TimerApp - .exe 빌드 스크립트
echo =======================================
echo.

set ROOT=%~dp0
if "%ROOT:~-1%"=="\" set ROOT=%ROOT:~0,-1%

echo [1/3] 의존성 설치 확인 중...
pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo [오류] pip 실행 실패. Python이 설치되어 있는지 확인해주세요.
    pause
    exit /b 1
)

echo [2/3] .exe 파일 생성 중... (잠시 기다려주세요)
set ICON_OPT=--icon=NONE
set VERSION_OPT=
if exist "%ROOT%\version_info.txt" set VERSION_OPT=--version-file="%ROOT%\version_info.txt"
set ADD_DATA=
if exist "%ROOT%\res\icon.ico" (
    set ICON_OPT=--icon="%ROOT%\res\icon.ico"
    set ADD_DATA=%ADD_DATA% --add-data "%ROOT%\res\icon.ico;res"
)
if exist "%ROOT%\res\Pretendard-Regular.ttf" set ADD_DATA=%ADD_DATA% --add-data "%ROOT%\res\Pretendard-Regular.ttf;res"

set UPX_OPT=--noupx
set UPX_DIR=
where upx >nul 2>&1
if %errorlevel% equ 0 (
    for /f "delims=" %%i in ('where upx') do set UPX_EXE=%%i
    for %%i in ("%UPX_EXE%") do set UPX_DIR=%%~dpi
    set UPX_DIR=%UPX_DIR:~0,-1%
    set UPX_OPT=--upx-dir="%UPX_DIR%"
    echo    UPX 발견 [PATH]: 압축 적용
) else if exist "C:\Program Files\UPX-5.1.1\upx.exe" (
    set UPX_OPT=--upx-dir="C:\Program Files\UPX-5.1.1"
    echo    UPX 발견 [고정경로]: 압축 적용
) else (
    echo    UPX 미설치: 압축 없이 빌드
)

py -m PyInstaller --onefile --windowed --name "TimerApp" %ICON_OPT% %VERSION_OPT% ^
    --distpath . --workpath build --specpath build ^
    --exclude-module email --exclude-module html --exclude-module http ^
    --exclude-module urllib --exclude-module xml --exclude-module xmlrpc ^
    --exclude-module unittest --exclude-module pydoc --exclude-module doctest ^
    --exclude-module difflib --exclude-module ftplib --exclude-module imaplib ^
    --exclude-module mailbox --exclude-module smtplib --exclude-module poplib ^
    --exclude-module multiprocessing --exclude-module asyncio ^
    --exclude-module concurrent --exclude-module curses ^
    %UPX_OPT% %ADD_DATA% main.py
if %errorlevel% neq 0 (
    echo [오류] 빌드 실패. 위 오류 메시지를 확인해주세요.
    pause
    exit /b 1
)

echo.
echo [3/3] 완료!
echo.
echo   ✅ TimerApp.exe 파일이 현재 폴더에 생성되었습니다.
echo   빌드 중간 파일은 build\ 폴더에 저장됩니다.
echo.
