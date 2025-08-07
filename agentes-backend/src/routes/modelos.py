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
    """Detectar modelos de Ollama"""
    try:
        # Intentar conectar a Ollama
        response = requests.get('http://localhost:11434/api/tags', timeout=10)
        if response.status_code == 200:
            data = response.json()
            modelos = []
            
            # Procesar todos los modelos encontrados
            for modelo in data.get('models', []):
                nombre_modelo = modelo['name']
                tamano_bytes = modelo.get('size', 0)
                
                # Convertir tamaño a formato legible
                if tamano_bytes > 1024**3:  # GB
                    tamano_str = f"{tamano_bytes / (1024**3):.1f} GB"
                elif tamano_bytes > 1024**2:  # MB
                    tamano_str = f"{tamano_bytes / (1024**2):.1f} MB"
                else:
                    tamano_str = f"{tamano_bytes} bytes"
                
                modelos.append({
                    'id': f"ollama:{nombre_modelo}",
                    'nombre': nombre_modelo,
                    'servicio': 'Ollama',
                    'tamano': tamano_str,
                    'tamano_bytes': tamano_bytes,
                    'modificado': modelo.get('modified_at'),
                    'activo': True,
                    'local': True,
                    'disponible': True,
                    'familia': modelo.get('details', {}).get('family', 'unknown'),
                    'formato': modelo.get('details', {}).get('format', 'unknown')
                })
            
            print(f"✅ Ollama detectado: {len(modelos)} modelos encontrados")
            return {
                'conectado': True,
                'modelos': modelos,
                'puerto': 11434,
                'total_modelos': len(modelos),
                'estado': 'Conectado y funcionando'
            }
    except requests.exceptions.ConnectionError:
        print("❌ Ollama no está ejecutándose en puerto 11434")
    except requests.exceptions.Timeout:
        print("⏱️ Timeout conectando a Ollama")
    except Exception as e:
        print(f"❌ Error detectando Ollama: {e}")
    
    return {
        'conectado': False,
        'modelos': [],
        'puerto': 11434,
        'total_modelos': 0,
        'estado': 'No disponible - Verificar que Ollama esté ejecutándose'
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

