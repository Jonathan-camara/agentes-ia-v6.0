# 📥 Guía de Instalación - Agentes IA v6.0

## 🖥️ **Para TODOS los Sistemas Operativos**

### 📋 **Requisitos Previos**
- **Python 3.11+** (https://python.org/downloads)
- **Node.js 20+** (https://nodejs.org/downloads)
- **Git** (https://git-scm.com/downloads)

---

## 🪟 **WINDOWS**

### **Paso 1: Descargar el repositorio**
```cmd
# Opción A: Con Git (recomendado)
git clone https://github.com/Jonathan-camara/agentes-ia-v6.0.git
cd agentes-ia-v6.0

# Opción B: Descargar ZIP
# Ve a: https://github.com/Jonathan-camara/agentes-ia-v6.0
# Click en "Code" > "Download ZIP"
# Extrae el archivo y abre la carpeta en terminal
```

### **Paso 2: Instalación automática**
```cmd
# Ejecutar script de instalación
install.bat

# O manualmente:
cd agentes-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

cd ..\agentes-ia-interface
npm install
npm run build
xcopy /E /I /Y dist\* ..\agentes-backend\src\static\
```

### **Paso 3: Configurar APIs (opcional)**
```cmd
copy .env.example .env
# Editar .env con tu editor favorito y agregar API keys
```

### **Paso 4: Iniciar el sistema**
```cmd
cd agentes-backend
venv\Scripts\activate
python src\main.py
```

### **Paso 5: Abrir en navegador**
- Ve a: http://localhost:5000

---

## 🐧 **LINUX (Ubuntu/Debian)**

### **Paso 1: Instalar dependencias**
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python, Node.js y Git
sudo apt install python3 python3-pip python3-venv nodejs npm git -y

# Verificar versiones
python3 --version  # Debe ser 3.11+
node --version      # Debe ser 20+
```

### **Paso 2: Descargar el repositorio**
```bash
# Opción A: Con Git (recomendado)
git clone https://github.com/Jonathan-camara/agentes-ia-v6.0.git
cd agentes-ia-v6.0

# Opción B: Con wget
wget https://github.com/Jonathan-camara/agentes-ia-v6.0/archive/main.zip
unzip main.zip
cd agentes-ia-v6.0-main
```

### **Paso 3: Instalación automática**
```bash
# Dar permisos y ejecutar
chmod +x install.sh
./install.sh

# O manualmente:
cd agentes-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ../agentes-ia-interface
npm install
npm run build
cp -r dist/* ../agentes-backend/src/static/
```

### **Paso 4: Configurar APIs (opcional)**
```bash
cp .env.example .env
nano .env  # O usar tu editor favorito
```

### **Paso 5: Iniciar el sistema**
```bash
cd agentes-backend
source venv/bin/activate
python src/main.py
```

### **Paso 6: Abrir en navegador**
- Ve a: http://localhost:5000

---

## 🍎 **macOS**

### **Paso 1: Instalar dependencias**
```bash
# Instalar Homebrew (si no lo tienes)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python, Node.js y Git
brew install python@3.11 node git

# Verificar versiones
python3 --version  # Debe ser 3.11+
node --version      # Debe ser 20+
```

### **Paso 2: Descargar el repositorio**
```bash
# Opción A: Con Git (recomendado)
git clone https://github.com/Jonathan-camara/agentes-ia-v6.0.git
cd agentes-ia-v6.0

# Opción B: Con curl
curl -L https://github.com/Jonathan-camara/agentes-ia-v6.0/archive/main.zip -o agentes-ia-v6.0.zip
unzip agentes-ia-v6.0.zip
cd agentes-ia-v6.0-main
```

### **Paso 3: Instalación automática**
```bash
# Dar permisos y ejecutar
chmod +x install.sh
./install.sh

# O manualmente:
cd agentes-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd ../agentes-ia-interface
npm install
npm run build
cp -r dist/* ../agentes-backend/src/static/
```

### **Paso 4: Configurar APIs (opcional)**
```bash
cp .env.example .env
nano .env  # O usar tu editor favorito
```

### **Paso 5: Iniciar el sistema**
```bash
cd agentes-backend
source venv/bin/activate
python src/main.py
```

### **Paso 6: Abrir en navegador**
- Ve a: http://localhost:5000

---

## 🔧 **Configuración de APIs**

### **APIs Soportadas:**
```bash
# OpenAI (GPT-4, GPT-3.5)
OPENAI_API_KEY=sk-tu-api-key-aqui

# Anthropic (Claude-3)
ANTHROPIC_API_KEY=sk-ant-tu-api-key-aqui

# Google AI (Gemini)
GOOGLE_API_KEY=tu-google-api-key-aqui

# Telegram (Opcional)
TELEGRAM_BOT_TOKEN=tu-bot-token-aqui
```

### **Dónde obtener API keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Google AI**: https://makersuite.google.com/app/apikey
- **Telegram**: https://t.me/BotFather

---

## 🏠 **Servicios Locales (Opcional)**

### **Ollama** (Modelos locales)
```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Descargar desde: https://ollama.ai/download

# Instalar modelos
ollama pull llama2
ollama pull mistral
ollama pull codellama
```

### **LM Studio**
- Descargar desde: https://lmstudio.ai/
- Instalar y descargar modelos desde la interfaz

### **LocalAI**
```bash
# Con Docker
docker run -p 8080:8080 --name local-ai -ti localai/localai:latest
```

---

## 🚀 **Uso del Sistema**

### **Acceso:**
- **URL**: http://localhost:5000
- **Panel Principal**: Estadísticas y acciones rápidas
- **Agentes**: Crear y gestionar agentes IA
- **Salas 3D**: Chat interactivo con agentes
- **Modelos IA**: Detectar y gestionar modelos
- **Configuración**: APIs y bases de datos

### **Funcionalidades:**
- ✅ **Gestión completa de agentes**
- ✅ **Salas 3D interactivas**
- ✅ **Chat en tiempo real**
- ✅ **Detección automática de modelos**
- ✅ **Integración con APIs remotas**
- ✅ **Base de datos persistente**

---

## 🆘 **Solución de Problemas**

### **Error: Python no encontrado**
```bash
# Windows
# Instalar desde: https://python.org/downloads
# Marcar "Add Python to PATH"

# Linux
sudo apt install python3 python3-pip

# macOS
brew install python@3.11
```

### **Error: Node.js no encontrado**
```bash
# Windows/macOS
# Descargar desde: https://nodejs.org

# Linux
sudo apt install nodejs npm
```

### **Error: Puerto 5000 ocupado**
```bash
# Cambiar puerto en src/main.py
app.run(host='0.0.0.0', port=5001, debug=True)
```

### **Error: Permisos en Linux/Mac**
```bash
chmod +x install.sh
sudo chown -R $USER:$USER agentes-ia-v6.0/
```

---

## 📞 **Soporte**

Si tienes problemas:
1. Verifica que Python 3.11+ y Node.js 20+ estén instalados
2. Revisa que todos los archivos se descargaron correctamente
3. Asegúrate de estar en la carpeta correcta
4. Verifica que el puerto 5000 esté libre

**¡El sistema está 100% funcional y listo para usar!** 🎉

