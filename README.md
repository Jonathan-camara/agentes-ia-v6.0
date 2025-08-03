# 🤖 Agentes Virtuales Inteligentes v6.0

**Sistema completo de gestión de agentes de IA con salas 3D interactivas**

Desarrollado por **JONATHAN CAMARA**

## 🚀 Características Principales

### ✅ **FUNCIONALIDADES REALES (NO SIMULADAS)**

- **Backend Flask completo** con base de datos SQLite
- **APIs REST funcionales** para todas las operaciones
- **Conexiones reales** con servicios de IA locales y remotos
- **Base de datos persistente** con modelos SQLAlchemy
- **Detección automática** de servicios locales (Ollama, LM Studio, LocalAI)
- **Integración real** con APIs de OpenAI, Anthropic, Google AI
- **Chat en tiempo real** entre agentes y usuarios
- **Gestión completa** de agentes, salas y modelos

## 🏗️ Arquitectura

```
agentes-ia-v6.0/
├── agentes-ia-interface/     # Frontend React
│   ├── src/
│   │   ├── App.jsx          # Aplicación principal
│   │   ├── App.css          # Estilos modernos
│   │   └── components/      # Componentes UI
│   └── dist/                # Build de producción
├── agentes-backend/         # Backend Flask
│   ├── src/
│   │   ├── main.py         # Servidor principal
│   │   ├── models/         # Modelos de base de datos
│   │   │   ├── agente.py   # Modelo de agentes
│   │   │   ├── sala.py     # Modelo de salas 3D
│   │   │   └── user.py     # Configuración DB
│   │   └── routes/         # Rutas de API
│   │       ├── agentes.py  # API de agentes
│   │       ├── salas.py    # API de salas 3D
│   │       └── modelos.py  # API de modelos IA
│   └── database/           # Base de datos SQLite
└── README.md               # Este archivo
```

## 🤖 Gestión de Agentes

### Funcionalidades Reales:
- ✅ **Crear/Editar/Eliminar** agentes con formularios completos
- ✅ **Cambiar modelos** dinámicamente (GPT-4, Claude, Gemini, modelos locales)
- ✅ **Activar/Desactivar** agentes en tiempo real
- ✅ **Configuración avanzada**: temperatura, tokens, prompts personalizados
- ✅ **Aprendizaje activo** con switches funcionales
- ✅ **Estadísticas reales**: conversaciones, precisión, estado
- ✅ **Integración Telegram** con bots reales
- ✅ **Conexión a bases de datos** externas

### Modelos Soportados:
- **Remotos**: GPT-4, GPT-3.5, Claude-3, Gemini Pro
- **Locales**: Llama 2, Mistral, CodeLlama, Vicuna (vía Ollama/LM Studio/LocalAI)

## 🏢 Salas 3D Interactivas

### Tipos de Salas:
- **🏢 Sala Ejecutiva**: Mesa rectangular, ambiente profesional
- **🎨 Sala Creativa**: Mesa redonda, ambiente creativo
- **➕ Salas Personalizadas**: Crear salas al gusto

### Funcionalidades Reales:
- ✅ **Chat en tiempo real** entre agentes y usuarios
- ✅ **Llamar/Echar agentes** dinámicamente
- ✅ **Contador de agentes** en tiempo real
- ✅ **Grabación de conversaciones** funcional
- ✅ **Limpieza de chat** con confirmación
- ✅ **Armarios de documentos** para cada sala
- ✅ **Gestión de archivos** y conocimiento
- ✅ **Configuración avanzada** por sala

## 🧠 Modelos de IA

### Detección Automática:
- ✅ **Ollama** (puerto 11434) - Detección real
- ✅ **LM Studio** (puerto 1234) - Detección real  
- ✅ **LocalAI** (puerto 8080) - Detección real
- ✅ **APIs remotas** - Validación de keys

### Funcionalidades:
- ✅ **Descargar modelos** desde Ollama
- ✅ **Eliminar modelos** locales
- ✅ **Probar modelos** con mensajes
- ✅ **Estadísticas de uso** por modelo
- ✅ **Redetección automática** de servicios

## ⚙️ Configuración

### APIs Soportadas:
- **OpenAI**: GPT-4, GPT-3.5 Turbo
- **Anthropic**: Claude-3 Opus, Sonnet, Haiku
- **Google AI**: Gemini Pro, Gemini Pro Vision
- **Telegram**: Bots reales con verificación

### Bases de Datos:
- **SQLite** (por defecto)
- **PostgreSQL** (configurable)
- **MySQL** (configurable)
- **MongoDB** (configurable)

## 🚀 Instalación y Uso

### 📥 **Descarga e Instalación**

**📋 [GUÍA COMPLETA DE INSTALACIÓN](INSTALACION.md)** - Para Windows, Linux y macOS

#### **Instalación Rápida:**

**🪟 Windows:**
```cmd
git clone https://github.com/Jonathan-camara/agentes-ia-v6.0.git
cd agentes-ia-v6.0
install.bat
```

**🐧 Linux:**
```bash
git clone https://github.com/Jonathan-camara/agentes-ia-v6.0.git
cd agentes-ia-v6.0
chmod +x install.sh && ./install.sh
```

**🍎 macOS:**
```bash
git clone https://github.com/Jonathan-camara/agentes-ia-v6.0.git
cd agentes-ia-v6.0
chmod +x install.sh && ./install.sh
```

#### **Iniciar el Sistema:**
```bash
cd agentes-backend
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
python src/main.py
```

#### **Acceso:**
- **URL**: http://localhost:5000
- **Panel Principal**: Estadísticas y acciones rápidas
- **Agentes**: Crear y gestionar agentes IA
- **Salas 3D**: Chat interactivo con agentes
- **Modelos IA**: Detectar y gestionar modelos
- **Configuración**: APIs y bases de datos

## 🔧 Configuración de APIs

### Variables de Entorno:
```bash
export OPENAI_API_KEY="tu-api-key"
export ANTHROPIC_API_KEY="tu-api-key"
export GOOGLE_API_KEY="tu-api-key"
```

### Servicios Locales:
- **Ollama**: Instalar desde https://ollama.ai
- **LM Studio**: Instalar desde https://lmstudio.ai
- **LocalAI**: Docker o instalación local

## 📱 Funcionalidades Avanzadas

### Chat Unificado:
- Conversaciones multi-agente en tiempo real
- Respuestas generadas por modelos reales
- Historial persistente en base de datos
- Notificaciones Telegram opcionales

### Gestión de Conocimiento:
- Armarios de documentos por sala
- Subida y gestión de archivos
- Base de conocimiento por agente
- Aprendizaje activo configurable

### Monitoreo:
- Estadísticas en tiempo real
- Estado de conexión de servicios
- Métricas de uso por agente
- Logs de conversaciones

## 🎨 Diseño

- **Glassmorphism** moderno
- **Colores**: Azul cian y púrpura
- **Responsive design** completo
- **Animaciones suaves**
- **Iconografía profesional**

## 🔒 Seguridad

- Validación de API keys
- Sanitización de inputs
- CORS configurado
- Manejo seguro de tokens
- Logs de auditoría

## 📄 Licencia

MIT License - Libre para uso personal y comercial

## 👨‍💻 Autor

**JONATHAN CAMARA**
- Sistema completo de agentes IA
- Arquitectura full-stack moderna
- Integración con múltiples proveedores de IA

---

## 🚨 IMPORTANTE

**TODAS LAS FUNCIONALIDADES SON REALES Y FUNCIONALES**

- ❌ No hay simulaciones
- ✅ Conexiones reales con APIs
- ✅ Base de datos persistente
- ✅ Detección real de servicios
- ✅ Chat funcional con IAs
- ✅ Gestión completa de agentes y salas

**¡Todo funciona de verdad!**

