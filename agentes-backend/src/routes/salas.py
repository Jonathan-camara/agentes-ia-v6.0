from flask import Blueprint, request, jsonify, send_file
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from src.models.sala import db, Sala, Mensaje, Archivo, Armario, ConocimientoSala
from src.models.agente import Agente
from src.routes.agentes import generar_respuesta_ia

salas_bp = Blueprint('salas', __name__)

UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@salas_bp.route('/salas', methods=['GET'])
def obtener_salas():
    """Obtener todas las salas"""
    try:
        salas = Sala.query.all()
        resultado = []
        
        for sala in salas:
            sala_dict = sala.to_dict()
            
            # Agregar mensajes recientes
            mensajes = Mensaje.query.filter_by(sala_id=sala.id).order_by(Mensaje.timestamp.desc()).limit(50).all()
            sala_dict['mensajes'] = [msg.to_dict() for msg in reversed(mensajes)]
            
            # Agregar archivos
            archivos = Archivo.query.filter_by(sala_id=sala.id, armario_id=None).all()
            sala_dict['archivos'] = [archivo.to_dict() for archivo in archivos]
            
            # Agregar armarios con sus archivos
            armarios = Armario.query.filter_by(sala_id=sala.id).all()
            sala_dict['armarios'] = [armario.to_dict() for armario in armarios]
            
            # Agregar conocimiento y aprendizaje
            conocimiento = ConocimientoSala.query.filter_by(sala_id=sala.id).all()
            sala_dict['aprendizaje'] = {
                'habilitado': True,
                'conversacionesGuardadas': len(mensajes),
                'conocimientoBase': [c.to_dict() for c in conocimiento if c.tipo == 'conocimiento'],
                'patrones': [c.to_dict() for c in conocimiento if c.tipo == 'patron']
            }
            
            resultado.append(sala_dict)
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@salas_bp.route('/salas', methods=['POST'])
def crear_sala():
    """Crear una nueva sala"""
    try:
        data = request.get_json()
        
        sala = Sala()
        sala.from_dict(data)
        
        # Configuración por defecto
        configuracion_default = {
            'grabacionAutomatica': False,
            'transcripcionVoz': True,
            'notificacionesTelegram': False,
            'backupAutomatico': True
        }
        sala.configuracion = json.dumps(configuracion_default)
        
        db.session.add(sala)
        db.session.commit()
        
        # Crear armarios por defecto según el tipo de sala
        if data.get('tipo') == 'ejecutiva':
            armarios_default = ['Documentos Financieros', 'Contratos', 'Reportes']
        else:
            armarios_default = ['Diseños', 'Referencias', 'Proyectos']
        
        for nombre_armario in armarios_default:
            armario = Armario(
                sala_id=sala.id,
                nombre=nombre_armario,
                descripcion=f'Armario para {nombre_armario.lower()}'
            )
            db.session.add(armario)
        
        db.session.commit()
        
        return jsonify(sala.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@salas_bp.route('/salas/<int:sala_id>/mensajes', methods=['POST'])
def enviar_mensaje_sala(sala_id):
    """Enviar mensaje a una sala y obtener respuestas de agentes"""
    try:
        sala = Sala.query.get_or_404(sala_id)
        data = request.get_json()
        mensaje_texto = data.get('mensaje', '')
        usuario = data.get('usuario', 'Usuario')
        
        if not mensaje_texto.strip():
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        # Guardar mensaje del usuario
        mensaje_usuario = Mensaje(
            sala_id=sala.id,
            tipo='usuario',
            texto=mensaje_texto,
            metadatos=json.dumps({'usuario': usuario})
        )
        db.session.add(mensaje_usuario)
        
        # Obtener agentes activos en la sala
        agentes_activos = json.loads(sala.agentes_activos) if sala.agentes_activos else []
        respuestas = []
        
        for agente_id in agentes_activos:
            agente = Agente.query.get(agente_id)
            if agente and agente.estado == 'activo':
                # Generar respuesta del agente
                respuesta = generar_respuesta_ia(mensaje_texto, agente)
                
                # Guardar mensaje del agente
                mensaje_agente = Mensaje(
                    sala_id=sala.id,
                    agente_id=agente.id,
                    tipo='agente',
                    texto=respuesta,
                    metadatos=json.dumps({
                        'agente': agente.to_dict(),
                        'modelo': agente.modelo
                    })
                )
                db.session.add(mensaje_agente)
                
                # Actualizar contador de conversaciones
                agente.conversaciones += 1
                
                respuestas.append({
                    'agente': agente.to_dict(),
                    'respuesta': respuesta,
                    'mensaje': mensaje_agente.to_dict()
                })
        
        db.session.commit()
        
        return jsonify({
            'mensajeUsuario': mensaje_usuario.to_dict(),
            'respuestas': respuestas
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@salas_bp.route('/salas/<int:sala_id>/agentes/<int:agente_id>/llamar', methods=['POST'])
def llamar_agente_sala(sala_id, agente_id):
    """Llamar un agente a una sala"""
    try:
        sala = Sala.query.get_or_404(sala_id)
        agente = Agente.query.get_or_404(agente_id)
        
        agentes_activos = json.loads(sala.agentes_activos) if sala.agentes_activos else []
        
        if agente_id not in agentes_activos:
            agentes_activos.append(agente_id)
            sala.agentes_activos = json.dumps(agentes_activos)
            
            # Mensaje de sistema
            mensaje_sistema = Mensaje(
                sala_id=sala.id,
                tipo='sistema',
                texto=f"{agente.avatar} {agente.nombre} se ha unido a la sala"
            )
            db.session.add(mensaje_sistema)
            
            db.session.commit()
        
        return jsonify({'mensaje': f'Agente {agente.nombre} llamado a la sala'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@salas_bp.route('/salas/<int:sala_id>/agentes/<int:agente_id>/echar', methods=['POST'])
def echar_agente_sala(sala_id, agente_id):
    """Echar un agente de una sala"""
    try:
        sala = Sala.query.get_or_404(sala_id)
        agente = Agente.query.get_or_404(agente_id)
        
        agentes_activos = json.loads(sala.agentes_activos) if sala.agentes_activos else []
        
        if agente_id in agentes_activos:
            agentes_activos.remove(agente_id)
            sala.agentes_activos = json.dumps(agentes_activos)
            
            # Mensaje de sistema
            mensaje_sistema = Mensaje(
                sala_id=sala.id,
                tipo='sistema',
                texto=f"{agente.avatar} {agente.nombre} ha salido de la sala"
            )
            db.session.add(mensaje_sistema)
            
            db.session.commit()
        
        return jsonify({'mensaje': f'Agente {agente.nombre} echado de la sala'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@salas_bp.route('/salas/<int:sala_id>/archivos', methods=['POST'])
def subir_archivo_sala(sala_id):
    """Subir archivo a una sala"""
    try:
        sala = Sala.query.get_or_404(sala_id)
        
        if 'archivo' not in request.files:
            return jsonify({'error': 'No se encontró archivo'}), 400
        
        file = request.files['archivo']
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"{sala_id}_{datetime.now().timestamp()}_{filename}")
        file.save(filepath)
        
        # Leer contenido si es archivo de texto
        contenido = None
        try:
            if file.content_type and file.content_type.startswith('text/'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    contenido = f.read()
        except:
            pass
        
        archivo = Archivo(
            sala_id=sala.id,
            nombre=filename,
            tipo=file.content_type,
            tamano=os.path.getsize(filepath),
            ruta_archivo=filepath,
            contenido=contenido
        )
        
        db.session.add(archivo)
        db.session.commit()
        
        return jsonify(archivo.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@salas_bp.route('/salas/<int:sala_id>/armarios', methods=['POST'])
def crear_armario(sala_id):
    """Crear un nuevo armario en una sala"""
    try:
        sala = Sala.query.get_or_404(sala_id)
        data = request.get_json()
        
        armario = Armario(
            sala_id=sala.id,
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion', '')
        )
        
        db.session.add(armario)
        db.session.commit()
        
        return jsonify(armario.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@salas_bp.route('/salas/<int:sala_id>/archivos/<int:archivo_id>/mover/<int:armario_id>', methods=['POST'])
def mover_archivo_armario(sala_id, archivo_id, armario_id):
    """Mover archivo a un armario"""
    try:
        archivo = Archivo.query.filter_by(id=archivo_id, sala_id=sala_id).first_or_404()
        armario = Armario.query.filter_by(id=armario_id, sala_id=sala_id).first_or_404()
        
        archivo.armario_id = armario_id
        db.session.commit()
        
        return jsonify({'mensaje': f'Archivo movido a {armario.nombre}'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@salas_bp.route('/salas/<int:sala_id>/conocimiento', methods=['POST'])
def guardar_conocimiento(sala_id):
    """Guardar conocimiento en una sala"""
    try:
        sala = Sala.query.get_or_404(sala_id)
        data = request.get_json()
        
        conocimiento = ConocimientoSala(
            sala_id=sala.id,
            tipo='conocimiento',
            contenido=data.get('contenido'),
            metadatos=json.dumps(data.get('metadatos', {}))
        )
        
        db.session.add(conocimiento)
        db.session.commit()
        
        return jsonify(conocimiento.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@salas_bp.route('/salas/<int:sala_id>/analizar-patrones', methods=['POST'])
def analizar_patrones_sala(sala_id):
    """Analizar patrones de conversación en una sala"""
    try:
        sala = Sala.query.get_or_404(sala_id)
        
        # Obtener mensajes de la sala
        mensajes = Mensaje.query.filter_by(sala_id=sala.id).all()
        
        # Análisis básico de patrones
        patrones = {
            'totalMensajes': len(mensajes),
            'mensajesUsuario': len([m for m in mensajes if m.tipo == 'usuario']),
            'mensajesAgente': len([m for m in mensajes if m.tipo == 'agente']),
            'agenteMasActivo': None,
            'horasPico': [],
            'palabrasClave': []
        }
        
        # Encontrar agente más activo
        agentes_conteo = {}
        for mensaje in mensajes:
            if mensaje.tipo == 'agente' and mensaje.agente_id:
                agentes_conteo[mensaje.agente_id] = agentes_conteo.get(mensaje.agente_id, 0) + 1
        
        if agentes_conteo:
            agente_id_mas_activo = max(agentes_conteo, key=agentes_conteo.get)
            agente_mas_activo = Agente.query.get(agente_id_mas_activo)
            if agente_mas_activo:
                patrones['agenteMasActivo'] = agente_mas_activo.nombre
        
        # Guardar análisis
        analisis = ConocimientoSala(
            sala_id=sala.id,
            tipo='patron',
            contenido=json.dumps(patrones),
            metadatos=json.dumps({'tipoAnalisis': 'patrones_conversacion'})
        )
        
        db.session.add(analisis)
        db.session.commit()
        
        return jsonify(analisis.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@salas_bp.route('/salas/<int:sala_id>/exportar', methods=['GET'])
def exportar_datos_sala(sala_id):
    """Exportar todos los datos de una sala"""
    try:
        sala = Sala.query.get_or_404(sala_id)
        
        # Recopilar todos los datos
        mensajes = Mensaje.query.filter_by(sala_id=sala.id).all()
        archivos = Archivo.query.filter_by(sala_id=sala.id).all()
        armarios = Armario.query.filter_by(sala_id=sala.id).all()
        conocimiento = ConocimientoSala.query.filter_by(sala_id=sala.id).all()
        
        datos_exportacion = {
            'sala': sala.to_dict(),
            'mensajes': [msg.to_dict() for msg in mensajes],
            'archivos': [arch.to_dict() for arch in archivos],
            'armarios': [arm.to_dict() for arm in armarios],
            'conocimiento': [con.to_dict() for con in conocimiento],
            'fechaExportacion': datetime.utcnow().isoformat()
        }
        
        # Crear archivo temporal
        filename = f"sala_{sala.nombre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(datos_exportacion, f, indent=2, ensure_ascii=False)
        
        return send_file(filepath, as_attachment=True, download_name=filename)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@salas_bp.route('/salas/<int:sala_id>/buscar', methods=['GET'])
def buscar_en_sala(sala_id):
    """Buscar contenido en archivos y mensajes de una sala"""
    try:
        sala = Sala.query.get_or_404(sala_id)
        termino = request.args.get('q', '').lower()
        
        if not termino:
            return jsonify({'resultados': []})
        
        resultados = []
        
        # Buscar en archivos
        archivos = Archivo.query.filter_by(sala_id=sala.id).all()
        for archivo in archivos:
            if (termino in archivo.nombre.lower() or 
                (archivo.contenido and termino in archivo.contenido.lower())):
                resultados.append({
                    'tipo': 'archivo',
                    'item': archivo.to_dict(),
                    'armario': archivo.armario.nombre if archivo.armario else None
                })
        
        # Buscar en mensajes
        mensajes = Mensaje.query.filter_by(sala_id=sala.id).filter(
            Mensaje.texto.ilike(f'%{termino}%')
        ).all()
        
        for mensaje in mensajes:
            resultados.append({
                'tipo': 'mensaje',
                'item': mensaje.to_dict()
            })
        
        return jsonify({'resultados': resultados})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

