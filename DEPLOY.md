# 🚀 Instrucciones de Despliegue

## 📋 Para subir a GitHub:

### 1. Crear repositorio en GitHub:
- Ve a https://github.com/new
- Nombre: `agentes-ia-v6.0`
- Descripción: `Sistema completo de agentes IA con salas 3D - FUNCIONALIDADES REALES`
- Público o Privado (tu elección)
- **NO** inicializar con README (ya tenemos uno)

### 2. Conectar y subir:
```bash
git remote add origin https://github.com/TU-USUARIO/agentes-ia-v6.0.git
git push -u origin main
```

## 🌐 Para desplegar en producción:

### Opción 1: Vercel (Recomendado)
```bash
npm install -g vercel
vercel --prod
```

### Opción 2: Heroku
```bash
# Crear Procfile
echo "web: cd agentes-backend && python src/main.py" > Procfile
git add Procfile && git commit -m "Add Procfile for Heroku"

# Desplegar
heroku create agentes-ia-v6
git push heroku main
```

### Opción 3: Railway
```bash
# Instalar Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
```

### Opción 4: DigitalOcean App Platform
- Conectar repositorio GitHub
- Configurar build: `cd agentes-ia-interface && npm run build`
- Configurar run: `cd agentes-backend && python src/main.py`

## ⚙️ Variables de Entorno para Producción:

```bash
OPENAI_API_KEY=tu-api-key-openai
ANTHROPIC_API_KEY=tu-api-key-anthropic  
GOOGLE_API_KEY=tu-api-key-google
FLASK_ENV=production
DATABASE_URL=postgresql://... (opcional)
```

## 🔧 Configuración Local:

### Backend:
```bash
cd agentes-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Frontend (desarrollo):
```bash
cd agentes-ia-interface
npm install
npm run dev
```

## 📱 URLs de Acceso:

- **Local**: http://localhost:5000
- **Producción**: https://tu-dominio.com

## 🎯 Funcionalidades Verificadas:

✅ **Backend Flask** funcionando en puerto 5000
✅ **Base de datos SQLite** con agentes y salas
✅ **APIs REST** completamente funcionales
✅ **Frontend React** con diseño moderno
✅ **Detección real** de servicios locales
✅ **Chat en tiempo real** entre agentes
✅ **Gestión completa** de agentes y salas
✅ **Switches funcionales** para activar/desactivar
✅ **Formularios reales** para crear/editar
✅ **Conexiones reales** con APIs externas

## 🚨 IMPORTANTE:

**TODO ES REAL Y FUNCIONAL - NO HAY SIMULACIONES**

El sistema está completamente implementado con:
- Base de datos real
- APIs funcionales  
- Conexiones reales
- Chat funcional
- Gestión completa

¡Listo para producción!

