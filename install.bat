@echo off
echo 🚀 Instalando Agentes IA v6.0 - Sistema Completo
echo ================================================
echo Desarrollado por JONATHAN CAMARA
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado. Por favor instálalo primero.
    pause
    exit /b 1
)

REM Verificar Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js no está instalado. Por favor instálalo primero.
    pause
    exit /b 1
)

echo ✅ Python y Node.js detectados
echo.

REM Instalar dependencias del backend
echo 📦 Instalando dependencias del backend...
cd agentes-backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo ✅ Backend configurado
echo.

REM Instalar dependencias del frontend
echo 📦 Instalando dependencias del frontend...
cd ..\agentes-ia-interface
npm install
echo ✅ Frontend configurado
echo.

REM Construir frontend
echo 🔨 Construyendo frontend...
npm run build
echo ✅ Frontend construido
echo.

REM Copiar build al backend
echo 📁 Copiando archivos al backend...
xcopy /E /I /Y dist\* ..\agentes-backend\src\static\
echo ✅ Archivos copiados
echo.

echo 🎉 ¡Instalación completada!
echo.
echo 🚀 Para iniciar el sistema:
echo    cd agentes-backend
echo    venv\Scripts\activate
echo    python src\main.py
echo.
echo 🌐 Luego abre: http://localhost:5000
echo.
echo 📚 Funcionalidades disponibles:
echo    ✅ Gestión completa de agentes IA
echo    ✅ Salas 3D interactivas
echo    ✅ Chat en tiempo real
echo    ✅ Detección de modelos locales
echo    ✅ Integración con APIs remotas
echo    ✅ Base de datos persistente
echo.
echo 🔧 Para configurar APIs:
echo    set OPENAI_API_KEY=tu-api-key
echo    set ANTHROPIC_API_KEY=tu-api-key
echo    set GOOGLE_API_KEY=tu-api-key
echo.
echo ¡Todo es REAL y funcional! 🎯
pause

