@echo off
REM ==================== BUILD SCRIPT FOR WINDOWS ====================
REM Script para construir y ejecutar el contenedor Docker en Windows

echo.
echo ==================== EMOTION DETECTOR - DOCKER BUILD ====================
echo.

REM Verificar que existe .env
if not exist .env (
    echo [ERROR] No se encontro el archivo .env
    echo Copia .env.example a .env y configura tus variables
    exit /b 1
)

echo [1/3] Deteniendo contenedores existentes...
docker-compose down 2>nul

echo.
echo [2/3] Construyendo imagen Docker...
docker-compose build --no-cache

if %errorlevel% neq 0 (
    echo [ERROR] Fallo la construccion de la imagen
    exit /b 1
)

echo.
echo [3/3] Iniciando contenedor...
docker-compose up -d

if %errorlevel% neq 0 (
    echo [ERROR] Fallo al iniciar el contenedor
    exit /b 1
)

echo.
echo ==================== LISTO ====================
echo.
echo Dashboard disponible en: http://localhost:8000
echo API docs en: http://localhost:8000/docs
echo.
echo Ver logs en tiempo real:
echo   docker-compose logs -f
echo.
echo Detener contenedor:
echo   docker-compose down
echo.
echo ==============================================

pause