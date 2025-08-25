@echo off
REM 🚀 Script de Instalación para Windows - Sistema de Agentes AI

setlocal enabledelayedexpansion

echo 🚀 Script de Instalación para Windows - Sistema de Agentes AI
echo ================================================================
echo.

REM Verificar si Python está instalado
echo [INFO] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado. Por favor, instala Python 3.8+ desde python.org
    echo [INFO] Asegúrate de marcar "Add Python to PATH" durante la instalación
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python %PYTHON_VERSION% encontrado

REM Verificar si pip está disponible
echo [INFO] Verificando pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip no encontrado. Reinstala Python marcando "Add Python to PATH"
    pause
    exit /b 1
)

echo [SUCCESS] pip encontrado

REM Verificar si Git está instalado
echo [INFO] Verificando Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git no encontrado. Por favor, instala Git desde git-scm.com
    pause
    exit /b 1
)

for /f "tokens=3" %%i in ('git --version 2^>^&1') do set GIT_VERSION=%%i
echo [SUCCESS] Git %GIT_VERSION% encontrado

REM Verificar si Poetry está instalado
echo [INFO] Verificando Poetry...
poetry --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Poetry no encontrado. Instalando...
    
    REM Instalar Poetry usando PowerShell
    powershell -Command "& {Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing | Invoke-Expression}"
    
    REM Verificar si se instaló correctamente
    poetry --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Error al instalar Poetry
        echo [INFO] Por favor, instala Poetry manualmente:
        echo [INFO] 1. Abre PowerShell como Administrador
        echo [INFO] 2. Ejecuta: (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content ^| python -
        pause
        exit /b 1
    )
)

for /f "tokens=2" %%i in ('poetry --version 2^>^&1') do set POETRY_VERSION=%%i
echo [SUCCESS] Poetry %POETRY_VERSION% encontrado

REM Clonar repositorio
echo [INFO] Clonando repositorio...
if exist "offsec_challenge" (
    echo [WARNING] Directorio offsec_challenge ya existe
    set /p CONTINUE="¿Deseas continuar con el directorio existente? (y/N): "
    if /i not "!CONTINUE!"=="y" (
        echo [INFO] Por favor, elimina el directorio existente y ejecuta el script nuevamente
        pause
        exit /b 1
    )
) else (
    git clone https://github.com/tu-usuario/offsec_challenge.git
)

cd offsec_challenge\AgentesAI

REM Verificar que pyproject.toml existe
if not exist "pyproject.toml" (
    echo [ERROR] No se encontró pyproject.toml. Verifica que el repositorio se clonó correctamente
    pause
    exit /b 1
)

echo [SUCCESS] Repositorio clonado correctamente

REM Instalar dependencias
echo [INFO] Instalando dependencias...
poetry install

if %errorlevel% neq 0 (
    echo [ERROR] Error al instalar dependencias
    pause
    exit /b 1
)

echo [SUCCESS] Dependencias instaladas correctamente

REM Configurar variables de entorno
echo [INFO] Configurando variables de entorno...
if exist ".env.example" (
    if not exist ".env" (
        copy ".env.example" ".env" >nul
        echo [SUCCESS] Archivo .env creado desde .env.example
        echo [WARNING] IMPORTANTE: Edita .env y configura tu GEMINI_API_KEY
    ) else (
        echo [WARNING] Archivo .env ya existe
    )
) else (
    echo [WARNING] Archivo .env.example no encontrado
)

REM Verificar instalación
echo [INFO] Verificando instalación...
poetry run python -c "from agentesai.agent.sistema import SistemaAgentes; print('✅ Módulo importado correctamente')" >nul 2>&1

if %errorlevel% neq 0 (
    echo [ERROR] Error al importar módulo
    pause
    exit /b 1
)

echo [SUCCESS] Módulo importado correctamente

REM Ejecutar tests básicos
echo [INFO] Ejecutando tests de verificación...
poetry run pytest tests/ -q --tb=no >nul 2>&1

if %errorlevel% neq 0 (
    echo [WARNING] Algunos tests fallaron, pero la instalación básica está completa
) else (
    echo [SUCCESS] Tests ejecutados correctamente
)

echo [SUCCESS] Instalación verificada correctamente

REM Mostrar próximos pasos
echo.
echo 🎉 ¡Instalación completada exitosamente!
echo.
echo 📋 Próximos pasos:
echo 1. Configura tu API key de Gemini en el archivo .env
echo 2. Ejecuta tu primera consulta:
echo    poetry run python -m agentesai.cli "¿quién soy?"
echo 3. Explora más funcionalidades:
echo    poetry run python demo_completo.py
echo.
echo 📚 Documentación:
echo - README.md: Guía de uso principal
echo - INSTALACION.md: Guía de instalación detallada
echo.
echo 🆘 Soporte:
echo - Revisa la sección de solución de problemas en INSTALACION.md
echo - Abre un issue en el repositorio si encuentras problemas
echo.
pause 