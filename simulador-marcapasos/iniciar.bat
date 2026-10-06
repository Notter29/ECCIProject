@echo off
setlocal
set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"
set "BACKEND_PY=%BACKEND_DIR%\venv\Scripts\python.exe"

echo ================================================================
echo  GALIX PACESTAR - Universidad ECCI
echo ================================================================

echo.
echo [1/4] Preparando entorno Python...
if not exist "%BACKEND_PY%" (
	py -3 -m venv "%BACKEND_DIR%\venv"
	if errorlevel 1 goto :error
)

"%BACKEND_PY%" -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
	echo Instalando dependencias del backend...
	"%BACKEND_PY%" -m pip install -r "%BACKEND_DIR%\requirements.txt"
	if errorlevel 1 goto :error
)

echo.
echo [2/4] Preparando dependencias Angular...
if not exist "%FRONTEND_DIR%\node_modules\@angular\cli\bin\ng.js" (
	call npm.cmd --prefix "%FRONTEND_DIR%" ci
	if errorlevel 1 goto :error
)

echo.
echo [3/4] Iniciando Backend (FastAPI)...
start "Backend - FastAPI" /D "%BACKEND_DIR%" cmd /k ""%BACKEND_PY%" -m uvicorn main:app --reload --port 8000"

timeout /t 2 /nobreak >nul

echo.
echo [4/4] Iniciando Frontend (Angular)...
start "Frontend - Angular" /D "%FRONTEND_DIR%" cmd /k "npm.cmd run start"

echo.
echo ================================================================
echo  API:          http://localhost:8000
echo  DOCUMENTACION: http://localhost:8000/docs
echo  APLICACION:   http://localhost:4200
echo ================================================================
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul
exit /b 0

:error
echo.
echo No fue posible preparar el proyecto. Revisa que Python 3, Node.js y npm esten instalados.
pause
exit /b 1
