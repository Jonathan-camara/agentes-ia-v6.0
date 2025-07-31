from flask import Blueprint, request, jsonify
import requests
import json
import os
from datetime import datetime
from src.models.agente import db, Agente, Conversacion

agentes_bp = Blueprint('agentes', __name__)

# Configuración de APIs
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

@agentes_bp.route('/agentes', methods=['GET'])
def obtener_agentes():
    """Obtener todos los agentes de la base de datos"""
    try:
        agentes = Agente.query.all()
        return jsonify([agente.to_dict() for agente in agentes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agentes_bp.route('/agentes', methods=['POST'])
def crear_agente():
    """Crear un nuevo agente en la base de datos"""
    try:
        data = request.get_json()
        
        # Validar token de Telegram si está habilitado
        if data.get('telegram') and data.get('telegramToken'):
            if not verificar_telegram_bot(data['telegramToken']):
                return jsonify({'error': 'Token de Telegram inválido'}), 400
        
        agente = Agente()
        agente.from_dict(data)
        
        db.session.add(agente)
        db.session.commit()
        
        return jsonify(agente.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agentes_bp.route('/agentes/<int:agente_id>', methods=['PUT'])
def actualizar_agente(agente_id):
    """Actualizar un agente existente"""
    try:
        agente = Agente.query.get_or_404(agente_id)
        data = request.get_json()
        
        # Validar token de Telegram si está habilitado
        if data.get('telegram') and data.get('telegramToken'):
            if not verificar_telegram_bot(data['telegramToken']):
                return jsonify({'error': 'Token de Telegram inválido'}), 400
        
        agente.from_dict(data)
        db.session.commit()
        
        return jsonify(agente.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agentes_bp.route('/agentes/<int:agente_id>', methods=['DELETE'])
def eliminar_agente(agente_id):
    """Eliminar un agente"""
    try:
        agente = Agente.query.get_or_404(agente_id)
        db.session.delete(agente)
        db.session.commit()
        
        return jsonify({'mensaje': 'Agente eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agentes_bp.route('/agentes/<int:agente_id>/activar', methods=['POST'])
def activar_agente(agente_id):
    """Activar un agente"""
    try:
        agente = Agente.query.get_or_404(agente_id)
        
        # Verificar conexión con modelo
        if not verificar_modelo_disponible(agente.modelo):
            return jsonify({'error': f'Modelo {agente.modelo} no disponible'}), 400
        
        agente.estado = 'activo'
        db.session.commit()
        
        # Iniciar polling de Telegram si está configurado
        if agente.telegram and agente.telegram_token:
            iniciar_polling_telegram(agente)
        
        return jsonify(agente.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agentes_bp.route('/agentes/<int:agente_id>/desactivar', methods=['POST'])
def desactivar_agente(agente_id):
    """Desactivar un agente"""
    try:
        agente = Agente.query.get_or_404(agente_id)
        agente.estado = 'inactivo'
        db.session.commit()
        
        # Detener polling de Telegram
        detener_polling_telegram(agente_id)
        
        return jsonify(agente.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agentes_bp.route('/agentes/<int:agente_id>/chat', methods=['POST'])
def chat_con_agente(agente_id):
    """Enviar mensaje a un agente y obtener respuesta"""
    try:
        agente = Agente.query.get_or_404(agente_id)
        data = request.get_json()
        mensaje = data.get('mensaje', '')
        
        if not mensaje.strip():
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        # Generar respuesta usando el modelo del agente
        respuesta = generar_respuesta_ia(mensaje, agente)
        
        # Guardar conversación en base de datos
        conversacion = Conversacion(
            agente_id=agente.id,
            sala_id=data.get('salaId'),
            usuario=data.get('usuario', 'Usuario'),
            mensaje_usuario=mensaje,
            respuesta_agente=respuesta,
            canal='web'
        )
        
        db.session.add(conversacion)
        
        # Actualizar contador de conversaciones
        agente.conversaciones += 1
        db.session.commit()
        
        return jsonify({
            'respuesta': respuesta,
            'conversacion': conversacion.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def verificar_telegram_bot(token):
    """Verificar si un token de Telegram es válido"""
    try:
        response = requests.get(f'https://api.telegram.org/bot{token}/getMe', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('ok', False)
        return False
    except:
        return False

def verificar_modelo_disponible(modelo):
    """Verificar si un modelo está disponible"""
    try:
        if modelo.startswith('ollama:'):
            # Verificar Ollama
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                data = response.json()
                modelo_nombre = modelo.replace('ollama:', '')
                return any(m['name'].startswith(modelo_nombre) for m in data.get('models', []))
        
        elif modelo.startswith('lmstudio:'):
            # Verificar LM Studio
            response = requests.get('http://localhost:1234/v1/models', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return len(data.get('data', [])) > 0
        
        elif modelo in ['gpt-4', 'gpt-3.5-turbo']:
            # Verificar OpenAI
            return OPENAI_API_KEY is not None
        
        elif modelo.startswith('claude'):
            # Verificar Anthropic
            return ANTHROPIC_API_KEY is not None
        
        return False
    except:
        return False

def generar_respuesta_ia(mensaje, agente):
    """Generar respuesta usando el modelo de IA del agente"""
    try:
        modelo = agente.modelo
        
        if modelo.startswith('ollama:'):
            return generar_respuesta_ollama(mensaje, agente)
        elif modelo.startswith('lmstudio:'):
            return generar_respuesta_lmstudio(mensaje, agente)
        elif modelo in ['gpt-4', 'gpt-3.5-turbo']:
            return generar_respuesta_openai(mensaje, agente)
        elif modelo.startswith('claude'):
            return generar_respuesta_claude(mensaje, agente)
        else:
            return "Lo siento, mi modelo de IA no está disponible en este momento."
    
    except Exception as e:
        return f"Error generando respuesta: {str(e)}"

def generar_respuesta_ollama(mensaje, agente):
    """Generar respuesta usando Ollama"""
    try:
        modelo_nombre = agente.modelo.replace('ollama:', '')
        
        response = requests.post('http://localhost:11434/api/generate', 
            json={
                'model': modelo_nombre,
                'prompt': f"{agente.prompt}\n\nUsuario: {mensaje}\nAsistente:",
                'stream': False,
                'options': {
                    'temperature': agente.temperatura,
                    'num_predict': agente.max_tokens
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', 'Sin respuesta')
        else:
            return "Error conectando con Ollama"
    
    except Exception as e:
        return f"Error Ollama: {str(e)}"

def generar_respuesta_lmstudio(mensaje, agente):
    """Generar respuesta usando LM Studio"""
    try:
        response = requests.post('http://localhost:1234/v1/chat/completions',
            json={
                'messages': [
                    {'role': 'system', 'content': agente.prompt},
                    {'role': 'user', 'content': mensaje}
                ],
                'temperature': agente.temperatura,
                'max_tokens': agente.max_tokens
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return "Error conectando con LM Studio"
    
    except Exception as e:
        return f"Error LM Studio: {str(e)}"

def generar_respuesta_openai(mensaje, agente):
    """Generar respuesta usando OpenAI"""
    try:
        if not OPENAI_API_KEY:
            return "API Key de OpenAI no configurada"
        
        response = requests.post('https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': agente.modelo,
                'messages': [
                    {'role': 'system', 'content': agente.prompt},
                    {'role': 'user', 'content': mensaje}
                ],
                'temperature': agente.temperatura,
                'max_tokens': agente.max_tokens
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f"Error OpenAI: {response.status_code}"
    
    except Exception as e:
        return f"Error OpenAI: {str(e)}"

def generar_respuesta_claude(mensaje, agente):
    """Generar respuesta usando Claude"""
    try:
        if not ANTHROPIC_API_KEY:
            return "API Key de Anthropic no configurada"
        
        response = requests.post('https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': ANTHROPIC_API_KEY,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            },
            json={
                'model': agente.modelo,
                'max_tokens': agente.max_tokens,
                'messages': [
                    {'role': 'user', 'content': f"{agente.prompt}\n\n{mensaje}"}
                ]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['content'][0]['text']
        else:
            return f"Error Claude: {response.status_code}"
    
    except Exception as e:
        return f"Error Claude: {str(e)}"

# Variables globales para polling de Telegram
telegram_polling = {}

def iniciar_polling_telegram(agente):
    """Iniciar polling de Telegram para un agente"""
    # Implementar polling real aquí
    pass

def detener_polling_telegram(agente_id):
    """Detener polling de Telegram para un agente"""
    # Implementar detención de polling aquí
    pass

