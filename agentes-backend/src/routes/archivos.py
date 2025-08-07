from flask import Blueprint, request, jsonify, send_file
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import mimetypes

archivos_bp = Blueprint('archivos', __name__)

# Configuración de directorios
UPLOAD_FOLDER = 'src/uploads'
ARMARIO_FOLDER = 'src/armario'
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 
    'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'json', 'xml', 'md'
}

# Crear directorios si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ARMARIO_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@archivos_bp.route('/archivos/subir', methods=['POST'])
def subir_archivo():
    """Subir archivo al sistema"""
    try:
        if 'archivo' not in request.files:
            return jsonify({'error': 'No se encontró archivo'}), 400
        
        file = request.files['archivo']
        destino = request.form.get('destino', 'general')  # general, armario, agente
        agente_id = request.form.get('agente_id', None)
        
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        if file and allowed_file(file.filename):
            # Generar nombre único
            filename = secure_filename(file.filename)
            unique_id = str(uuid.uuid4())[:8]
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{unique_id}{ext}"
            
            # Determinar directorio de destino
            if destino == 'armario':
                filepath = os.path.join(ARMARIO_FOLDER, unique_filename)
            else:
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            # Guardar archivo
            file.save(filepath)
            
            # Extraer contenido del archivo
            contenido = extraer_contenido_archivo(filepath)
            
            # Guardar metadatos
            metadata = {
                'id': unique_id,
                'nombre_original': filename,
                'nombre_archivo': unique_filename,
                'ruta': filepath,
                'destino': destino,
                'agente_id': agente_id,
                'tamano': os.path.getsize(filepath),
                'tipo_mime': mimetypes.guess_type(filepath)[0],
                'fecha_subida': datetime.utcnow().isoformat(),
                'contenido_extraido': contenido[:1000] if contenido else None  # Primeros 1000 caracteres
            }
            
            # Guardar en índice
            guardar_metadata_archivo(metadata)
            
            return jsonify({
                'mensaje': 'Archivo subido exitosamente',
                'archivo': metadata,
                'contenido_preview': contenido[:200] if contenido else None
            })
        
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@archivos_bp.route('/archivos/listar', methods=['GET'])
def listar_archivos():
    """Listar archivos por destino"""
    try:
        destino = request.args.get('destino', 'general')
        agente_id = request.args.get('agente_id', None)
        
        archivos = cargar_metadata_archivos()
        
        # Filtrar por destino
        if destino:
            archivos = [a for a in archivos if a.get('destino') == destino]
        
        # Filtrar por agente
        if agente_id:
            archivos = [a for a in archivos if a.get('agente_id') == agente_id]
        
        return jsonify({
            'archivos': archivos,
            'total': len(archivos)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@archivos_bp.route('/archivos/armario', methods=['GET'])
def listar_armario():
    """Listar archivos del armario de la sala de juntas"""
    try:
        archivos = cargar_metadata_archivos()
        archivos_armario = [a for a in archivos if a.get('destino') == 'armario']
        
        return jsonify({
            'archivos': archivos_armario,
            'total': len(archivos_armario),
            'mensaje': f'Armario de documentos - {len(archivos_armario)} archivos disponibles'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@archivos_bp.route('/archivos/descargar/<archivo_id>', methods=['GET'])
def descargar_archivo(archivo_id):
    """Descargar archivo por ID"""
    try:
        archivos = cargar_metadata_archivos()
        archivo = next((a for a in archivos if a['id'] == archivo_id), None)
        
        if not archivo:
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        if not os.path.exists(archivo['ruta']):
            return jsonify({'error': 'Archivo físico no encontrado'}), 404
        
        return send_file(
            archivo['ruta'],
            as_attachment=True,
            download_name=archivo['nombre_original']
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@archivos_bp.route('/archivos/contenido/<archivo_id>', methods=['GET'])
def obtener_contenido_archivo(archivo_id):
    """Obtener contenido de un archivo para que los agentes lo lean"""
    try:
        archivos = cargar_metadata_archivos()
        archivo = next((a for a in archivos if a['id'] == archivo_id), None)
        
        if not archivo:
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        if not os.path.exists(archivo['ruta']):
            return jsonify({'error': 'Archivo físico no encontrado'}), 404
        
        # Extraer contenido completo
        contenido = extraer_contenido_archivo(archivo['ruta'])
        
        return jsonify({
            'archivo': archivo,
            'contenido': contenido,
            'longitud': len(contenido) if contenido else 0
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@archivos_bp.route('/archivos/eliminar/<archivo_id>', methods=['DELETE'])
def eliminar_archivo(archivo_id):
    """Eliminar archivo del sistema"""
    try:
        archivos = cargar_metadata_archivos()
        archivo = next((a for a in archivos if a['id'] == archivo_id), None)
        
        if not archivo:
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        # Eliminar archivo físico
        if os.path.exists(archivo['ruta']):
            os.remove(archivo['ruta'])
        
        # Eliminar de metadatos
        archivos = [a for a in archivos if a['id'] != archivo_id]
        guardar_lista_metadata(archivos)
        
        return jsonify({
            'mensaje': f'Archivo {archivo["nombre_original"]} eliminado exitosamente'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@archivos_bp.route('/archivos/buscar', methods=['POST'])
def buscar_archivos():
    """Buscar archivos por contenido o nombre"""
    try:
        data = request.get_json()
        consulta = data.get('consulta', '').lower()
        destino = data.get('destino', None)
        
        if not consulta:
            return jsonify({'error': 'Consulta requerida'}), 400
        
        archivos = cargar_metadata_archivos()
        
        # Filtrar por destino si se especifica
        if destino:
            archivos = [a for a in archivos if a.get('destino') == destino]
        
        # Buscar en nombre y contenido
        resultados = []
        for archivo in archivos:
            coincidencia = False
            
            # Buscar en nombre
            if consulta in archivo['nombre_original'].lower():
                coincidencia = True
            
            # Buscar en contenido extraído
            if archivo.get('contenido_extraido') and consulta in archivo['contenido_extraido'].lower():
                coincidencia = True
            
            if coincidencia:
                resultados.append(archivo)
        
        return jsonify({
            'resultados': resultados,
            'total': len(resultados),
            'consulta': consulta
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extraer_contenido_archivo(filepath):
    """Extraer contenido de texto de diferentes tipos de archivo"""
    try:
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        
        if ext in ['.txt', '.md', '.csv', '.json', '.xml']:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        
        elif ext == '.pdf':
            try:
                import PyPDF2
                with open(filepath, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                return "PDF - Contenido no extraído (PyPDF2 no disponible)"
        
        elif ext in ['.doc', '.docx']:
            try:
                import docx
                doc = docx.Document(filepath)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except ImportError:
                return "Word - Contenido no extraído (python-docx no disponible)"
        
        else:
            return f"Archivo {ext} - Contenido no extraído"
    
    except Exception as e:
        return f"Error extrayendo contenido: {str(e)}"

def guardar_metadata_archivo(metadata):
    """Guardar metadatos de archivo en índice"""
    try:
        archivos = cargar_metadata_archivos()
        archivos.append(metadata)
        guardar_lista_metadata(archivos)
    except Exception as e:
        print(f"Error guardando metadata: {e}")

def cargar_metadata_archivos():
    """Cargar metadatos de archivos desde índice"""
    try:
        index_path = 'src/archivos_index.json'
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error cargando metadata: {e}")
        return []

def guardar_lista_metadata(archivos):
    """Guardar lista completa de metadatos"""
    try:
        index_path = 'src/archivos_index.json'
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(archivos, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando lista metadata: {e}")

