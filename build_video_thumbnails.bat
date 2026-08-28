@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON=%CD%\.venv\Scripts\python.exe"
) else (
    set "PYTHON=py -3"
)

echo Using Python: %PYTHON%
%PYTHON% -m pip install -r requirements-video-thumbnails.txt > video-thumbnail-build.log 2>&1
if errorlevel 1 goto :error

%PYTHON% -m playwright install chromium >> video-thumbnail-build.log 2>&1
if errorlevel 1 goto :error

%PYTHON% download_video_thumbnails.py >> video-thumbnail-build.log 2>&1
if errorlevel 1 goto :error

echo.
echo Video thumbnails have been generated.
echo See video-thumbnail-build.log for details.
pause
exit /b 0

:error
echo.
echo Failed to build video thumbnails.
echo See video-thumbnail-build.log for the exact error.
pause
exit /b 1
