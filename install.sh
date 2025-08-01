#!/bin/bash

echo "🚀 Instalando Agentes IA v6.0 - Sistema Completo"
echo "================================================"
echo "Desarrollado por JONATHAN CAMARA"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instálalo primero."
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado. Por favor instálalo primero."
    exit 1
fi

echo "✅ Python y Node.js detectados"
echo ""

# Instalar dependencias del backend
echo "📦 Instalando dependencias del backend..."
cd agentes-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Backend configurado"
echo ""

# Instalar dependencias del frontend
echo "📦 Instalando dependencias del frontend..."
cd ../agentes-ia-interface
npm install
echo "✅ Frontend configurado"
echo ""

# Construir frontend
echo "🔨 Construyendo frontend..."
npm run build
echo "✅ Frontend construido"
echo ""

# Copiar build al backend
echo "📁 Copiando archivos al backend..."
cp -r dist/* ../agentes-backend/src/static/
echo "✅ Archivos copiados"
echo ""

echo "🎉 ¡Instalación completada!"
echo ""
echo "🚀 Para iniciar el sistema:"
echo "   cd agentes-backend"
echo "   source venv/bin/activate"
echo "   python src/main.py"
echo ""
echo "🌐 Luego abre: http://localhost:5000"
echo ""
echo "📚 Funcionalidades disponibles:"
echo "   ✅ Gestión completa de agentes IA"
echo "   ✅ Salas 3D interactivas"
echo "   ✅ Chat en tiempo real"
echo "   ✅ Detección de modelos locales"
echo "   ✅ Integración con APIs remotas"
echo "   ✅ Base de datos persistente"
echo ""
echo "🔧 Para configurar APIs:"
echo "   export OPENAI_API_KEY='tu-api-key'"
echo "   export ANTHROPIC_API_KEY='tu-api-key'"
echo "   export GOOGLE_API_KEY='tu-api-key'"
echo ""
echo "¡Todo es REAL y funcional! 🎯"

