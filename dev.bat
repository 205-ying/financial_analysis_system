@echo off
setlocal

cd /d "%~dp0"
set "CMD=%~1"
if "%CMD%"=="" set "CMD=help"

if /I "%CMD%"=="help" goto help
if /I "%CMD%"=="install" goto install
if /I "%CMD%"=="install-backend" goto install_backend
if /I "%CMD%"=="install-frontend" goto install_frontend
if /I "%CMD%"=="dev" goto dev
if /I "%CMD%"=="dev-backend" goto dev_backend
if /I "%CMD%"=="dev-frontend" goto dev_frontend
if /I "%CMD%"=="test" goto test
if /I "%CMD%"=="test-backend" goto test_backend
if /I "%CMD%"=="test-frontend" goto test_frontend
if /I "%CMD%"=="lint" goto lint
if /I "%CMD%"=="lint-backend" goto lint_backend
if /I "%CMD%"=="lint-frontend" goto lint_frontend
if /I "%CMD%"=="format" goto format
if /I "%CMD%"=="format-backend" goto format_backend
if /I "%CMD%"=="format-frontend" goto format_frontend
if /I "%CMD%"=="check" goto check
if /I "%CMD%"=="check-backend" goto check_backend
if /I "%CMD%"=="check-frontend" goto check_frontend
if /I "%CMD%"=="migrate" goto migrate
if /I "%CMD%"=="build" goto build
if /I "%CMD%"=="type-check" goto type_check
if /I "%CMD%"=="type-check-backend" goto type_check_backend
if /I "%CMD%"=="type-check-frontend" goto type_check_frontend

echo Unknown command: %CMD%
echo Run "dev.bat help" for available commands.
exit /b 1

:help
echo Financial Analysis System - Windows commands
echo.
echo   dev.bat install          Install all dependencies
echo   dev.bat install-backend  Install backend dependencies
echo   dev.bat install-frontend Install frontend dependencies
echo.
echo   dev.bat dev              Show dev server commands
echo   dev.bat dev-backend      Start backend dev server
echo   dev.bat dev-frontend     Start frontend dev server
echo.
echo   dev.bat test             Run all tests
echo   dev.bat test-backend     Run backend tests
echo   dev.bat test-frontend    Run frontend tests
echo.
echo   dev.bat lint             Run linters
echo   dev.bat format           Format code
echo   dev.bat check            Run project checks
echo   dev.bat migrate          Run database migrations
echo   dev.bat build            Build frontend
echo   dev.bat type-check       Run type checks
exit /b 0

:install
call "%~f0" install-backend
if errorlevel 1 exit /b %ERRORLEVEL%
call "%~f0" install-frontend
exit /b %ERRORLEVEL%

:install_backend
pushd services\\api
pip install -r requirements_dev.txt
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:install_frontend
pushd apps\\web
npm install
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:dev
echo Start services in separate terminals:
echo   dev.bat dev-backend
echo   dev.bat dev-frontend
echo.
echo Or run:
echo   tooling\dev\start.bat
exit /b 0

:dev_backend
pushd services\\api
python dev.py start
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:dev_frontend
pushd apps\\web
npm run dev
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:test
call "%~f0" test-backend
if errorlevel 1 exit /b %ERRORLEVEL%
call "%~f0" test-frontend
exit /b %ERRORLEVEL%

:test_backend
pushd services\\api
python dev.py test
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:test_frontend
pushd apps\\web
npm run test
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:lint
call "%~f0" lint-backend
if errorlevel 1 exit /b %ERRORLEVEL%
call "%~f0" lint-frontend
exit /b %ERRORLEVEL%

:lint_backend
pushd services\\api
python dev.py lint
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:lint_frontend
pushd apps\\web
npm run lint
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:format
call "%~f0" format-backend
if errorlevel 1 exit /b %ERRORLEVEL%
call "%~f0" format-frontend
exit /b %ERRORLEVEL%

:format_backend
pushd services\\api
python dev.py format
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:format_frontend
pushd apps\\web
npm run format
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:check
call "%~f0" check-backend
if errorlevel 1 exit /b %ERRORLEVEL%
call "%~f0" check-frontend
exit /b %ERRORLEVEL%

:check_backend
pushd services\\api
python dev.py all
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:check_frontend
pushd apps\\web
npm run lint && npm run type-check && npm run build
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:migrate
pushd services\\api
python dev.py migrate
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:build
pushd apps\\web
npm run build
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:type_check
call "%~f0" type-check-backend
if errorlevel 1 exit /b %ERRORLEVEL%
call "%~f0" type-check-frontend
exit /b %ERRORLEVEL%

:type_check_backend
pushd services\\api
python dev.py type-check
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%

:type_check_frontend
pushd apps\\web
npm run type-check
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
