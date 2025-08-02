#!/bin/bash

echo "🚀 Subiendo Agentes IA v6.0 a GitHub PRIVADO"
echo "============================================="
echo "Usuario: Jonathan-camara"
echo "Repositorio: agentes-ia-v6.0 (PRIVADO)"
echo ""

echo "📋 PASO 1: Crear repositorio en GitHub"
echo "--------------------------------------"
echo "1. Ve a: https://github.com/new"
echo "2. Repository name: agentes-ia-v6.0"
echo "3. Description: Sistema completo de agentes IA con salas 3D - FUNCIONALIDADES REALES"
echo "4. ✅ Selecciona 'Private' (IMPORTANTE)"
echo "5. ❌ NO marques 'Add a README file'"
echo "6. ❌ NO marques 'Add .gitignore'"
echo "7. ❌ NO marques 'Choose a license'"
echo "8. Click 'Create repository'"
echo ""

echo "📤 PASO 2: Subir código"
echo "------------------------"
echo "Una vez creado el repositorio, ejecuta:"
echo ""
echo "git push -u origin main"
echo ""

echo "🔍 PASO 3: Verificar"
echo "--------------------"
echo "Ve a: https://github.com/Jonathan-camara/agentes-ia-v6.0"
echo "Deberías ver todos los archivos subidos"
echo ""

echo "📁 Archivos que se subirán:"
echo "- README.md (documentación completa)"
echo "- FEATURES.md (lista de funcionalidades REALES)"
echo "- DEPLOY.md (instrucciones de despliegue)"
echo "- install.sh / install.bat (instalación automática)"
echo "- .env.example (configuración de APIs)"
echo "- agentes-backend/ (backend Flask completo)"
echo "- agentes-ia-interface/ (frontend React moderno)"
echo ""

echo "✅ El repositorio está configurado para:"
echo "   Usuario: Jonathan-camara"
echo "   Repo: agentes-ia-v6.0"
echo "   Visibilidad: PRIVADO"
echo ""

echo "🎯 ¿Listo para subir? Presiona Enter después de crear el repo..."
read -p ""

echo "🚀 Subiendo a GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 ¡ÉXITO! Repositorio subido correctamente"
    echo ""
    echo "🔗 Tu repositorio privado está en:"
    echo "   https://github.com/Jonathan-camara/agentes-ia-v6.0"
    echo ""
    echo "📋 Próximos pasos:"
    echo "1. Configura las API keys en .env"
    echo "2. Ejecuta ./install.sh para instalar"
    echo "3. Inicia con: python agentes-backend/src/main.py"
    echo "4. Abre: http://localhost:5000"
    echo ""
    echo "¡Todo es REAL y funcional! 🎯"
else
    echo ""
    echo "❌ Error al subir. Verifica que hayas creado el repositorio en GitHub."
    echo "   URL: https://github.com/new"
    echo "   Nombre: agentes-ia-v6.0"
    echo "   Tipo: PRIVADO"
fi

