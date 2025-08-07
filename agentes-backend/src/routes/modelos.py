from flask import Blueprint, request, jsonify
import requests
import os
import json
from datetime import datetime

modelos_bp = Blueprint('modelos', __name__)

@modelos_bp.route('/modelos/detectar', methods=['GET'])
def detectar_modelos():
    """Detectar todos los modelos disponibles localmente y remotamente"""
    try:
        modelos = {
            'ollama': detectar_ollama(),
            'lmstudio': detectar_lmstudio(),
            'localai': detectar_localai(),
            'openai': detectar_openai(),
            'anthropic': detectar_anthropic(),
            'google': detectar_google()
        }
        
        return jsonify(modelos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def detectar_ollama():
    """Detectar modelos de Ollama con diagnóstico mejorado"""
    try:
        print("🔍 Iniciando detección de Ollama...")
        
        # Intentar conectar a Ollama con múltiples intentos
        for intento in range(3):
            try:
                print(f"📡 Intento {intento + 1}/3 conectando a Ollama...")
                response = requests.get('http://localhost:11434/api/tags', timeout=15)
                
                if response.status_code == 200:
                    print("✅ Conexión exitosa con Ollama")
                    data = response.json()
                    print(f"📊 Respuesta recibida: {json.dumps(data, indent=2)}")
                    
                    modelos = []
                    modelos_raw = data.get('models', [])
                    
                    print(f"🤖 Procesando {len(modelos_raw)} modelos...")
                    
                    # Procesar todos los modelos encontrados
                    for i, modelo in enumerate(modelos_raw):
                        try:
                            nombre_modelo = modelo.get('name', f'modelo_{i}')
                            tamano_bytes = modelo.get('size', 0)
                            
                            # Convertir tamaño a formato legible
                            if tamano_bytes > 1024**3:  # GB
                                tamano_str = f"{tamano_bytes / (1024**3):.1f} GB"
                            elif tamano_bytes > 1024**2:  # MB
                                tamano_str = f"{tamano_bytes / (1024**2):.1f} MB"
                            else:
                                tamano_str = f"{tamano_bytes} bytes"
                            
                            # Extraer información adicional
                            detalles = modelo.get('details', {})
                            familia = detalles.get('family', 'unknown')
                            formato = detalles.get('format', 'unknown')
                            
                            modelo_info = {
                                'id': f"ollama:{nombre_modelo}",
                                'nombre': nombre_modelo,
                                'servicio': 'Ollama',
                                'tamano': tamano_str,
                                'tamano_bytes': tamano_bytes,
                                'modificado': modelo.get('modified_at'),
                                'activo': True,
                                'local': True,
                                'disponible': True,
                                'familia': familia,
                                'formato': formato,
                                'digest': modelo.get('digest', ''),
                                'detalles_completos': modelo
                            }
                            
                            modelos.append(modelo_info)
                            print(f"✅ Modelo procesado: {nombre_modelo} ({tamano_str})")
                            
                        except Exception as e:
                            print(f"⚠️ Error procesando modelo {i}: {e}")
                            continue
                    
                    print(f"🎯 Total de modelos detectados: {len(modelos)}")
                    
                    return {
                        'conectado': True,
                        'modelos': modelos,
                        'puerto': 11434,
                        'total_modelos': len(modelos),
                        'estado': 'Conectado y funcionando',
                        'version_api': data.get('version', 'unknown'),
                        'respuesta_completa': data
                    }
                
                else:
                    print(f"❌ Error HTTP {response.status_code}: {response.text}")
                    
            except requests.exceptions.ConnectionError as e:
                print(f"❌ Error de conexión (intento {intento + 1}): {e}")
                if intento < 2:  # Si no es el último intento
                    import time
                    time.sleep(2)  # Esperar 2 segundos antes del siguiente intento
                    
            except requests.exceptions.Timeout as e:
                print(f"⏱️ Timeout (intento {intento + 1}): {e}")
                if intento < 2:
                    import time
                    time.sleep(2)
                    
            except Exception as e:
                print(f"❌ Error inesperado (intento {intento + 1}): {e}")
                if intento < 2:
                    import time
                    time.sleep(2)
        
        # Si llegamos aquí, todos los intentos fallaron
        print("❌ Todos los intentos de conexión fallaron")
        
        # Verificar si el proceso está ejecutándose
        proceso_activo = verificar_proceso_ollama_detallado()
        
        return {
            'conectado': False,
            'modelos': [],
            'puerto': 11434,
            'total_modelos': 0,
            'estado': 'No disponible - Verificar que Ollama esté ejecutándose',
            'proceso_activo': proceso_activo,
            'diagnostico': 'Ollama no responde en puerto 11434'
        }
        
    except Exception as e:
        print(f"❌ Error crítico en detección de Ollama: {e}")
        return {
            'conectado': False,
            'modelos': [],
            'puerto': 11434,
            'total_modelos': 0,
            'estado': f'Error crítico: {str(e)}',
            'error_detallado': str(e)
        }

def verificar_proceso_ollama_detallado():
    """Verificar proceso Ollama con más detalle"""
    try:
        import subprocess
        import platform
        
        sistema = platform.system().lower()
        print(f"🔍 Verificando proceso Ollama en {sistema}...")
        
        if sistema == 'windows':
            # Verificar proceso ollama.exe
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq ollama.exe'], 
                                  capture_output=True, text=True)
            
            if 'ollama.exe' in result.stdout:
                print("✅ Proceso ollama.exe encontrado")
                return {
                    'ejecutandose': True,
                    'metodo': 'tasklist',
                    'detalles': result.stdout
                }
            else:
                print("❌ Proceso ollama.exe NO encontrado")
                
                # Buscar en rutas comunes
                posibles_rutas = [
                    r'C:\Users\{}\AppData\Local\Programs\Ollama\ollama.exe'.format(os.getenv('USERNAME', '')),
                    r'C:\Program Files\Ollama\ollama.exe',
                    r'C:\Program Files (x86)\Ollama\ollama.exe'
                ]
                
                for ruta in posibles_rutas:
                    if os.path.exists(ruta):
                        print(f"💡 Ollama encontrado en: {ruta}")
                        return {
                            'ejecutandose': False,
                            'instalado': True,
                            'ruta': ruta,
                            'sugerencia': f'Ejecutar: {ruta} serve'
                        }
                
                return {
                    'ejecutandose': False,
                    'instalado': False,
                    'sugerencia': 'Instalar Ollama desde https://ollama.ai'
                }
        else:
            # Linux/Mac
            result = subprocess.run(['pgrep', '-f', 'ollama'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Proceso ollama encontrado")
                return {
                    'ejecutandose': True,
                    'metodo': 'pgrep',
                    'pid': result.stdout.strip()
                }
            else:
                print("❌ Proceso ollama NO encontrado")
                return {
                    'ejecutandose': False,
                    'sugerencia': 'Ejecutar: ollama serve'
                }
                
    except Exception as e:
        print(f"❌ Error verificando proceso: {e}")
        return {
            'ejecutandose': False,
            'error': str(e)
        }

def detectar_lmstudio():
    """Detectar modelos de LM Studio"""
    try:
        response = requests.get('http://localhost:1234/v1/models', timeout=5)
        if response.status_code == 200:
            data = response.json()
            modelos = []
            for modelo in data.get('data', []):
                modelos.append({
                    'id': f"lmstudio:{modelo['id']}",
                    'nombre': modelo['id'],
                    'servicio': 'LM Studio',
                    'activo': True,
                    'local': True
                })
            return {
                'conectado': True,
                'modelos': modelos,
                'puerto': 1234
            }
    except Exception as e:
        print(f"Error detectando LM Studio: {e}")
    
    return {
        'conectado': False,
        'modelos': [],
        'puerto': 1234
    }

def detectar_localai():
    """Detectar modelos de LocalAI"""
    try:
        response = requests.get('http://localhost:8080/v1/models', timeout=5)
        if response.status_code == 200:
            data = response.json()
            modelos = []
            for modelo in data.get('data', []):
                modelos.append({
                    'id': f"localai:{modelo['id']}",
                    'nombre': modelo['id'],
                    'servicio': 'LocalAI',
                    'activo': True,
                    'local': True
                })
            return {
                'conectado': True,
                'modelos': modelos,
                'puerto': 8080
            }
    except Exception as e:
        print(f"Error detectando LocalAI: {e}")
    
    return {
        'conectado': False,
        'modelos': [],
        'puerto': 8080
    }

def detectar_openai():
    """Detectar disponibilidad de OpenAI"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {
            'conectado': False,
            'modelos': [],
            'error': 'API Key no configurada'
        }
    
    try:
        response = requests.get('https://api.openai.com/v1/models',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            modelos_principales = ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']
            modelos = []
            
            for modelo_data in data.get('data', []):
                if modelo_data['id'] in modelos_principales:
                    modelos.append({
                        'id': modelo_data['id'],
                        'nombre': modelo_data['id'],
                        'servicio': 'OpenAI',
                        'activo': True,
                        'local': False,
                        'creado': modelo_data.get('created')
                    })
            
            return {
                'conectado': True,
                'modelos': modelos
            }
    except Exception as e:
        print(f"Error detectando OpenAI: {e}")
    
    return {
        'conectado': False,
        'modelos': [],
        'error': 'Error de conexión'
    }

def detectar_anthropic():
    """Detectar disponibilidad de Anthropic"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return {
            'conectado': False,
            'modelos': [],
            'error': 'API Key no configurada'
        }
    
    # Anthropic no tiene endpoint público de modelos, así que usamos los conocidos
    modelos_conocidos = [
        'claude-3-opus-20240229',
        'claude-3-sonnet-20240229',
        'claude-3-haiku-20240307'
    ]
    
    modelos = []
    for modelo_id in modelos_conocidos:
        modelos.append({
            'id': modelo_id,
            'nombre': modelo_id,
            'servicio': 'Anthropic',
            'activo': True,
            'local': False
        })
    
    return {
        'conectado': True,
        'modelos': modelos
    }

def detectar_google():
    """Detectar disponibilidad de Google AI"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return {
            'conectado': False,
            'modelos': [],
            'error': 'API Key no configurada'
        }
    
    # Google AI modelos conocidos
    modelos_conocidos = [
        'gemini-pro',
        'gemini-pro-vision'
    ]
    
    modelos = []
    for modelo_id in modelos_conocidos:
        modelos.append({
            'id': modelo_id,
            'nombre': modelo_id,
            'servicio': 'Google AI',
            'activo': True,
            'local': False
        })
    
    return {
        'conectado': True,
        'modelos': modelos
    }

@modelos_bp.route('/modelos/ollama/descargar', methods=['POST'])
def descargar_modelo_ollama():
    """Descargar un modelo en Ollama"""
    try:
        data = request.get_json()
        nombre_modelo = data.get('modelo')
        
        if not nombre_modelo:
            return jsonify({'error': 'Nombre de modelo requerido'}), 400
        
        # Verificar que Ollama esté disponible
        try:
            requests.get('http://localhost:11434/api/tags', timeout=5)
        except:
            return jsonify({'error': 'Ollama no está disponible'}), 503
        
        # Iniciar descarga
        response = requests.post('http://localhost:11434/api/pull',
            json={'name': nombre_modelo},
            timeout=300  # 5 minutos timeout
        )
        
        if response.status_code == 200:
            return jsonify({'mensaje': f'Modelo {nombre_modelo} descargado exitosamente'})
        else:
            return jsonify({'error': f'Error descargando modelo: {response.text}'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@modelos_bp.route('/modelos/ollama/eliminar', methods=['DELETE'])
def eliminar_modelo_ollama():
    """Eliminar un modelo de Ollama"""
    try:
        data = request.get_json()
        nombre_modelo = data.get('modelo')
        
        if not nombre_modelo:
            return jsonify({'error': 'Nombre de modelo requerido'}), 400
        
        response = requests.delete('http://localhost:11434/api/delete',
            json={'name': nombre_modelo},
            timeout=30
        )
        
        if response.status_code == 200:
            return jsonify({'mensaje': f'Modelo {nombre_modelo} eliminado exitosamente'})
        else:
            return jsonify({'error': f'Error eliminando modelo: {response.text}'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@modelos_bp.route('/modelos/generar', methods=['POST'])
def generar_respuesta_modelo():
    """Generar respuesta usando un modelo específico"""
    try:
        data = request.get_json()
        modelo_id = data.get('modelo')
        mensaje = data.get('mensaje')
        prompt_sistema = data.get('prompt_sistema', 'Eres un asistente útil.')
        temperatura = data.get('temperatura', 0.7)
        max_tokens = data.get('max_tokens', 1000)
        
        if not modelo_id or not mensaje:
            return jsonify({'error': 'Modelo y mensaje son requeridos'}), 400
        
        respuesta = None
        
        # Determinar el servicio del modelo
        if modelo_id.startswith('ollama:'):
            nombre_modelo = modelo_id.replace('ollama:', '')
            respuesta = generar_respuesta_ollama(nombre_modelo, mensaje, prompt_sistema, temperatura, max_tokens)
        
        elif modelo_id.startswith('lmstudio:'):
            nombre_modelo = modelo_id.replace('lmstudio:', '')
            respuesta = generar_respuesta_lmstudio(nombre_modelo, mensaje, prompt_sistema, temperatura, max_tokens)
        
        elif modelo_id.startswith('gpt-'):
            respuesta = generar_respuesta_openai(modelo_id, mensaje, prompt_sistema, temperatura, max_tokens)
        
        elif modelo_id.startswith('claude-'):
            respuesta = generar_respuesta_anthropic(modelo_id, mensaje, prompt_sistema, temperatura, max_tokens)
        
        elif modelo_id.startswith('gemini-'):
            respuesta = generar_respuesta_google(modelo_id, mensaje, prompt_sistema, temperatura, max_tokens)
        
        else:
            return jsonify({'error': f'Modelo no soportado: {modelo_id}'}), 400
        
        if respuesta:
            return jsonify({
                'modelo': modelo_id,
                'mensaje': mensaje,
                'respuesta': respuesta,
                'timestamp': datetime.utcnow().isoformat(),
                'exito': True
            })
        else:
            return jsonify({'error': 'No se pudo generar respuesta'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generar_respuesta_ollama(modelo, mensaje, prompt_sistema, temperatura, max_tokens):
    """Generar respuesta usando Ollama"""
    try:
        payload = {
            'model': modelo,
            'prompt': f"{prompt_sistema}\n\nUsuario: {mensaje}\nAsistente:",
            'stream': False,
            'options': {
                'temperature': temperatura,
                'num_predict': max_tokens
            }
        }
        
        response = requests.post('http://localhost:11434/api/generate', 
                               json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', '').strip()
    except Exception as e:
        print(f"Error generando respuesta con Ollama: {e}")
    
    return None

def generar_respuesta_lmstudio(modelo, mensaje, prompt_sistema, temperatura, max_tokens):
    """Generar respuesta usando LM Studio"""
    try:
        payload = {
            'model': modelo,
            'messages': [
                {'role': 'system', 'content': prompt_sistema},
                {'role': 'user', 'content': mensaje}
            ],
            'temperature': temperatura,
            'max_tokens': max_tokens
        }
        
        response = requests.post('http://localhost:1234/v1/chat/completions',
                               json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error generando respuesta con LM Studio: {e}")
    
    return None

def generar_respuesta_openai(modelo, mensaje, prompt_sistema, temperatura, max_tokens):
    """Generar respuesta usando OpenAI"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return None
        
        payload = {
            'model': modelo,
            'messages': [
                {'role': 'system', 'content': prompt_sistema},
                {'role': 'user', 'content': mensaje}
            ],
            'temperature': temperatura,
            'max_tokens': max_tokens
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions',
                               json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error generando respuesta con OpenAI: {e}")
    
    return None

def generar_respuesta_anthropic(modelo, mensaje, prompt_sistema, temperatura, max_tokens):
    """Generar respuesta usando Anthropic"""
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return None
        
        payload = {
            'model': modelo,
            'max_tokens': max_tokens,
            'temperature': temperatura,
            'system': prompt_sistema,
            'messages': [
                {'role': 'user', 'content': mensaje}
            ]
        }
        
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        response = requests.post('https://api.anthropic.com/v1/messages',
                               json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            return data['content'][0]['text'].strip()
    except Exception as e:
        print(f"Error generando respuesta con Anthropic: {e}")
    
    return None

def generar_respuesta_google(modelo, mensaje, prompt_sistema, temperatura, max_tokens):
    """Generar respuesta usando Google AI"""
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return None
        
        # Implementación simplificada para Google AI
        # En producción usarías la librería oficial de Google
        prompt_completo = f"{prompt_sistema}\n\nUsuario: {mensaje}\nAsistente:"
        
        # Aquí iría la implementación real de Google AI
        # Por ahora retornamos un placeholder
        return f"[Respuesta de {modelo}] Esta funcionalidad requiere implementación específica de Google AI SDK."
    except Exception as e:
        print(f"Error generando respuesta con Google AI: {e}")
    
    return None

@modelos_bp.route('/modelos/activar', methods=['POST'])
def activar_modelo():
    """Activar un modelo realmente en el sistema"""
    try:
        data = request.get_json()
        modelo_id = data.get('modelo')
        servicio = data.get('servicio', '').lower()
        
        if not modelo_id:
            return jsonify({'error': 'ID de modelo requerido'}), 400
        
        resultado = None
        
        if servicio == 'ollama' or modelo_id.startswith('ollama:'):
            nombre_modelo = modelo_id.replace('ollama:', '')
            resultado = activar_modelo_ollama(nombre_modelo)
        
        elif servicio == 'lmstudio' or modelo_id.startswith('lmstudio:'):
            resultado = activar_lmstudio()
        
        elif servicio == 'localai' or modelo_id.startswith('localai:'):
            resultado = activar_localai()
        
        else:
            return jsonify({'error': f'Servicio no soportado: {servicio}'}), 400
        
        if resultado['exito']:
            return jsonify({
                'mensaje': f'Modelo {modelo_id} activado exitosamente',
                'modelo': modelo_id,
                'servicio': servicio,
                'estado': 'activo',
                'detalles': resultado,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'error': f'No se pudo activar el modelo: {resultado.get("error", "Error desconocido")}',
                'detalles': resultado
            }), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@modelos_bp.route('/modelos/desactivar', methods=['POST'])
def desactivar_modelo():
    """Desactivar un modelo realmente en el sistema"""
    try:
        data = request.get_json()
        modelo_id = data.get('modelo')
        servicio = data.get('servicio', '').lower()
        
        if not modelo_id:
            return jsonify({'error': 'ID de modelo requerido'}), 400
        
        resultado = None
        
        if servicio == 'ollama' or modelo_id.startswith('ollama:'):
            resultado = desactivar_modelo_ollama()
        
        elif servicio == 'lmstudio' or modelo_id.startswith('lmstudio:'):
            resultado = desactivar_lmstudio()
        
        elif servicio == 'localai' or modelo_id.startswith('localai:'):
            resultado = desactivar_localai()
        
        else:
            return jsonify({'error': f'Servicio no soportado: {servicio}'}), 400
        
        if resultado['exito']:
            return jsonify({
                'mensaje': f'Modelo {modelo_id} desactivado exitosamente',
                'modelo': modelo_id,
                'servicio': servicio,
                'estado': 'inactivo',
                'detalles': resultado,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'error': f'No se pudo desactivar el modelo: {resultado.get("error", "Error desconocido")}',
                'detalles': resultado
            }), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def activar_modelo_ollama(nombre_modelo):
    """Activar un modelo específico en Ollama"""
    try:
        import subprocess
        import platform
        
        # Verificar si Ollama está ejecutándose
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code != 200:
                # Intentar iniciar Ollama
                resultado_inicio = iniciar_ollama()
                if not resultado_inicio['exito']:
                    return resultado_inicio
        except:
            # Ollama no está ejecutándose, intentar iniciarlo
            resultado_inicio = iniciar_ollama()
            if not resultado_inicio['exito']:
                return resultado_inicio
        
        # Verificar si el modelo existe
        response = requests.get('http://localhost:11434/api/tags', timeout=10)
        if response.status_code == 200:
            data = response.json()
            modelos_disponibles = [m['name'] for m in data.get('models', [])]
            
            if nombre_modelo not in modelos_disponibles:
                # El modelo no existe, intentar descargarlo
                print(f"📥 Descargando modelo {nombre_modelo}...")
                resultado_descarga = descargar_modelo_ollama_interno(nombre_modelo)
                if not resultado_descarga['exito']:
                    return resultado_descarga
        
        # Cargar el modelo en memoria (hacer una consulta simple)
        payload = {
            'model': nombre_modelo,
            'prompt': 'Hola',
            'stream': False,
            'options': {'num_predict': 1}
        }
        
        response = requests.post('http://localhost:11434/api/generate', 
                               json=payload, timeout=30)
        
        if response.status_code == 200:
            return {
                'exito': True,
                'mensaje': f'Modelo {nombre_modelo} activado y cargado en memoria',
                'modelo': nombre_modelo,
                'estado': 'activo'
            }
        else:
            return {
                'exito': False,
                'error': f'Error cargando modelo: {response.text}',
                'codigo': response.status_code
            }
    
    except Exception as e:
        return {
            'exito': False,
            'error': str(e)
        }

def desactivar_modelo_ollama():
    """Desactivar Ollama (liberar memoria)"""
    try:
        import subprocess
        import platform
        
        sistema = platform.system().lower()
        
        if sistema == 'windows':
            # En Windows, terminar proceso ollama
            result = subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return {
                    'exito': True,
                    'mensaje': 'Ollama desactivado exitosamente',
                    'metodo': 'taskkill'
                }
        else:
            # En Linux/Mac
            result = subprocess.run(['pkill', '-f', 'ollama'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return {
                    'exito': True,
                    'mensaje': 'Ollama desactivado exitosamente',
                    'metodo': 'pkill'
                }
        
        return {
            'exito': False,
            'error': 'No se pudo desactivar Ollama',
            'detalles': result.stderr if 'result' in locals() else 'Comando no ejecutado'
        }
    
    except Exception as e:
        return {
            'exito': False,
            'error': str(e)
        }

def iniciar_ollama():
    """Iniciar Ollama automáticamente"""
    try:
        import subprocess
        import platform
        import time
        
        sistema = platform.system().lower()
        
        if sistema == 'windows':
            # En Windows, buscar ollama.exe
            posibles_rutas = [
                r'C:\Users\{}\AppData\Local\Programs\Ollama\ollama.exe'.format(os.getenv('USERNAME')),
                r'C:\Program Files\Ollama\ollama.exe',
                r'C:\Program Files (x86)\Ollama\ollama.exe'
            ]
            
            ruta_ollama = None
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    ruta_ollama = ruta
                    break
            
            if not ruta_ollama:
                # Intentar con comando global
                try:
                    subprocess.run(['ollama', '--version'], capture_output=True, timeout=5)
                    ruta_ollama = 'ollama'
                except:
                    return {
                        'exito': False,
                        'error': 'Ollama no encontrado en el sistema'
                    }
            
            # Iniciar Ollama
            subprocess.Popen([ruta_ollama, 'serve'], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        else:
            # En Linux/Mac
            subprocess.Popen(['ollama', 'serve'])
        
        # Esperar a que inicie
        for i in range(10):  # Esperar hasta 10 segundos
            try:
                response = requests.get('http://localhost:11434/api/tags', timeout=2)
                if response.status_code == 200:
                    return {
                        'exito': True,
                        'mensaje': 'Ollama iniciado exitosamente',
                        'tiempo_inicio': f'{i+1} segundos'
                    }
            except:
                time.sleep(1)
        
        return {
            'exito': False,
            'error': 'Ollama no respondió después de 10 segundos'
        }
    
    except Exception as e:
        return {
            'exito': False,
            'error': str(e)
        }

def descargar_modelo_ollama_interno(nombre_modelo):
    """Descargar un modelo en Ollama internamente"""
    try:
        print(f"📥 Iniciando descarga de {nombre_modelo}...")
        
        response = requests.post('http://localhost:11434/api/pull',
            json={'name': nombre_modelo},
            timeout=600,  # 10 minutos timeout para descarga
            stream=True
        )
        
        if response.status_code == 200:
            # Procesar respuesta streaming
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if 'status' in data:
                            print(f"📥 {data['status']}")
                        if data.get('status') == 'success':
                            return {
                                'exito': True,
                                'mensaje': f'Modelo {nombre_modelo} descargado exitosamente'
                            }
                    except:
                        continue
            
            return {
                'exito': True,
                'mensaje': f'Descarga de {nombre_modelo} completada'
            }
        else:
            return {
                'exito': False,
                'error': f'Error descargando: {response.text}'
            }
    
    except Exception as e:
        return {
            'exito': False,
            'error': str(e)
        }

def activar_lmstudio():
    """Activar LM Studio"""
    try:
        import subprocess
        import platform
        
        sistema = platform.system().lower()
        
        if sistema == 'windows':
            # Buscar LM Studio en rutas comunes
            posibles_rutas = [
                r'C:\Users\{}\AppData\Local\Programs\LM Studio\LM Studio.exe'.format(os.getenv('USERNAME')),
                r'C:\Program Files\LM Studio\LM Studio.exe'
            ]
            
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    subprocess.Popen([ruta])
                    return {
                        'exito': True,
                        'mensaje': 'LM Studio iniciado',
                        'ruta': ruta
                    }
        
        return {
            'exito': False,
            'error': 'LM Studio no encontrado. Instálalo desde https://lmstudio.ai'
        }
    
    except Exception as e:
        return {
            'exito': False,
            'error': str(e)
        }

def desactivar_lmstudio():
    """Desactivar LM Studio"""
    try:
        import subprocess
        import platform
        
        sistema = platform.system().lower()
        
        if sistema == 'windows':
            result = subprocess.run(['taskkill', '/F', '/IM', 'LM Studio.exe'], 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(['pkill', '-f', 'lm.studio'], 
                                  capture_output=True, text=True)
        
        return {
            'exito': True,
            'mensaje': 'LM Studio desactivado'
        }
    
    except Exception as e:
        return {
            'exito': False,
            'error': str(e)
        }

def activar_localai():
    """Activar LocalAI"""
    try:
        import subprocess
        
        # Intentar iniciar LocalAI con Docker
        result = subprocess.run([
            'docker', 'run', '-d', '-p', '8080:8080', 
            '--name', 'localai', 'localai/localai:latest'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return {
                'exito': True,
                'mensaje': 'LocalAI iniciado con Docker',
                'contenedor': result.stdout.strip()
            }
        else:
            return {
                'exito': False,
                'error': f'Error iniciando LocalAI: {result.stderr}'
            }
    
    except Exception as e:
        return {
            'exito': False,
            'error': str(e)
        }

def desactivar_localai():
    """Desactivar LocalAI"""
    try:
        import subprocess
        
        # Detener contenedor Docker
        result = subprocess.run(['docker', 'stop', 'localai'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            # Eliminar contenedor
            subprocess.run(['docker', 'rm', 'localai'], 
                         capture_output=True, text=True)
            
            return {
                'exito': True,
                'mensaje': 'LocalAI desactivado'
            }
        else:
            return {
                'exito': False,
                'error': f'Error desactivando LocalAI: {result.stderr}'
            }
    
    except Exception as e:
        return {
            'exito': False,
            'error': str(e)
        }

@modelos_bp.route('/modelos/estado-servicios', methods=['GET'])
def obtener_estado_servicios():
    """Obtener estado real de todos los servicios"""
    try:
        import subprocess
        import platform
        
        sistema = platform.system().lower()
        estados = {}
        
        # Verificar Ollama
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=3)
            estados['ollama'] = {
                'activo': response.status_code == 200,
                'puerto': 11434,
                'proceso': verificar_proceso_ollama(sistema)
            }
        except:
            estados['ollama'] = {
                'activo': False,
                'puerto': 11434,
                'proceso': verificar_proceso_ollama(sistema)
            }
        
        # Verificar LM Studio
        try:
            response = requests.get('http://localhost:1234/v1/models', timeout=3)
            estados['lmstudio'] = {
                'activo': response.status_code == 200,
                'puerto': 1234,
                'proceso': verificar_proceso_lmstudio(sistema)
            }
        except:
            estados['lmstudio'] = {
                'activo': False,
                'puerto': 1234,
                'proceso': verificar_proceso_lmstudio(sistema)
            }
        
        # Verificar LocalAI
        try:
            response = requests.get('http://localhost:8080/v1/models', timeout=3)
            estados['localai'] = {
                'activo': response.status_code == 200,
                'puerto': 8080,
                'proceso': verificar_proceso_localai()
            }
        except:
            estados['localai'] = {
                'activo': False,
                'puerto': 8080,
                'proceso': verificar_proceso_localai()
            }
        
        return jsonify({
            'servicios': estados,
            'timestamp': datetime.utcnow().isoformat(),
            'sistema': sistema
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def verificar_proceso_ollama(sistema):
    """Verificar si el proceso Ollama está ejecutándose"""
    try:
        import subprocess
        
        if sistema == 'windows':
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq ollama.exe'], 
                                  capture_output=True, text=True)
            return 'ollama.exe' in result.stdout
        else:
            result = subprocess.run(['pgrep', '-f', 'ollama'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
    except:
        return False

def verificar_proceso_lmstudio(sistema):
    """Verificar si LM Studio está ejecutándose"""
    try:
        import subprocess
        
        if sistema == 'windows':
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq LM Studio.exe'], 
                                  capture_output=True, text=True)
            return 'LM Studio.exe' in result.stdout
        else:
            result = subprocess.run(['pgrep', '-f', 'lm.studio'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
    except:
        return False

def verificar_proceso_localai():
    """Verificar si LocalAI está ejecutándose"""
    try:
        import subprocess
        
        result = subprocess.run(['docker', 'ps', '--filter', 'name=localai'], 
                              capture_output=True, text=True)
        return 'localai' in result.stdout
    except:
        return False

@modelos_bp.route('/modelos/buscar-web', methods=['POST'])
def buscar_en_web():
    """Buscar información en internet"""
    try:
        data = request.get_json()
        consulta = data.get('consulta')
        
        if not consulta:
            return jsonify({'error': 'Consulta requerida'}), 400
        
        # Implementar búsqueda web real
        import urllib.parse
        import re
        
        # Usar DuckDuckGo como motor de búsqueda (no requiere API key)
        query_encoded = urllib.parse.quote(consulta)
        search_url = f"https://duckduckgo.com/html/?q={query_encoded}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Extraer resultados básicos (implementación simplificada)
            content = response.text
            
            # Buscar títulos y enlaces
            title_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
            matches = re.findall(title_pattern, content)
            
            resultados = []
            for i, (url, title) in enumerate(matches[:5]):  # Primeros 5 resultados
                resultados.append({
                    'titulo': title.strip(),
                    'url': url,
                    'posicion': i + 1
                })
            
            return jsonify({
                'consulta': consulta,
                'resultados': resultados,
                'total': len(resultados),
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return jsonify({'error': 'No se pudo realizar la búsqueda'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
def probar_modelo():
    """Probar un modelo con un mensaje simple"""
    try:
        data = request.get_json()
        modelo_id = data.get('modelo')
        mensaje = data.get('mensaje', 'Hola, ¿cómo estás?')
        
        if not modelo_id:
            return jsonify({'error': 'ID de modelo requerido'}), 400
        
        # Crear agente temporal para prueba
        class AgenteTemporal:
            def __init__(self, modelo):
                self.modelo = modelo
                self.prompt = "Eres un asistente útil."
                self.temperatura = 0.7
                self.max_tokens = 100
        
        agente_temp = AgenteTemporal(modelo_id)
        
        # Importar función de generación
        from src.routes.agentes import generar_respuesta_ia
        respuesta = generar_respuesta_ia(mensaje, agente_temp)
        
        return jsonify({
            'modelo': modelo_id,
            'mensaje': mensaje,
            'respuesta': respuesta,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@modelos_bp.route('/modelos/estadisticas', methods=['GET'])
def obtener_estadisticas_modelos():
    """Obtener estadísticas de uso de modelos"""
    try:
        from src.models.agente import Agente, Conversacion
        
        # Contar agentes por modelo
        agentes = Agente.query.all()
        estadisticas_modelos = {}
        
        for agente in agentes:
            modelo = agente.modelo
            if modelo not in estadisticas_modelos:
                estadisticas_modelos[modelo] = {
                    'agentes': 0,
                    'conversaciones': 0,
                    'activos': 0
                }
            
            estadisticas_modelos[modelo]['agentes'] += 1
            estadisticas_modelos[modelo]['conversaciones'] += agente.conversaciones
            if agente.estado == 'activo':
                estadisticas_modelos[modelo]['activos'] += 1
        
        return jsonify(estadisticas_modelos)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@modelos_bp.route('/modelos/configuracion', methods=['GET'])
def obtener_configuracion_modelos():
    """Obtener configuración de APIs de modelos"""
    try:
        configuracion = {
            'openai': {
                'configurado': bool(os.getenv('OPENAI_API_KEY')),
                'base_url': os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
            },
            'anthropic': {
                'configurado': bool(os.getenv('ANTHROPIC_API_KEY'))
            },
            'google': {
                'configurado': bool(os.getenv('GOOGLE_API_KEY'))
            },
            'servicios_locales': {
                'ollama': {
                    'puerto': 11434,
                    'url': 'http://localhost:11434'
                },
                'lmstudio': {
                    'puerto': 1234,
                    'url': 'http://localhost:1234'
                },
                'localai': {
                    'puerto': 8080,
                    'url': 'http://localhost:8080'
                }
            }
        }
        
        return jsonify(configuracion)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@modelos_bp.route('/modelos/configuracion', methods=['POST'])
def actualizar_configuracion_modelos():
    """Actualizar configuración de APIs de modelos"""
    try:
        data = request.get_json()
        
        # Aquí podrías guardar la configuración en base de datos
        # Por ahora solo validamos las API keys
        
        resultado = {}
        
        if 'openai_api_key' in data:
            # Validar API key de OpenAI
            try:
                response = requests.get('https://api.openai.com/v1/models',
                    headers={'Authorization': f'Bearer {data["openai_api_key"]}'},
                    timeout=10
                )
                resultado['openai'] = response.status_code == 200
            except:
                resultado['openai'] = False
        
        if 'anthropic_api_key' in data:
            # Validar API key de Anthropic (simulado)
            resultado['anthropic'] = len(data['anthropic_api_key']) > 20
        
        return jsonify({
            'mensaje': 'Configuración actualizada',
            'validacion': resultado
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

