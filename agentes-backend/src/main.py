import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.agente import Agente, Conversacion
from src.models.sala import Sala, Mensaje, Archivo, Armario, ConocimientoSala
from src.routes.user import user_bp
from src.routes.agentes import agentes_bp
from src.routes.salas import salas_bp
from src.routes.modelos import modelos_bp
from src.routes.archivos import archivos_bp
from src.routes.web import web_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para todas las rutas
CORS(app, origins="*")

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(agentes_bp, url_prefix='/api')
app.register_blueprint(salas_bp, url_prefix='/api')
app.register_blueprint(modelos_bp, url_prefix='/api')
app.register_blueprint(archivos_bp, url_prefix='/api')
app.register_blueprint(web_bp, url_prefix='/api')

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Crear todas las tablas
with app.app_context():
    db.create_all()
    
    # Crear agentes de ejemplo si no existen
    if Agente.query.count() == 0:
        agentes_ejemplo = [
            {
                'nombre': 'Analista Financiero',
                'rol': 'Finanzas',
                'avatar': '💰',
                'modelo': 'gpt-4',
                'prompt': 'Eres un analista financiero experto especializado en análisis de mercados, inversiones y estrategias financieras.',
                'temperatura': 0.7,
                'max_tokens': 1000,
                'voz': 'masculina'
            },
            {
                'nombre': 'Jefe de Ventas',
                'rol': 'Ventas',
                'avatar': '📈',
                'modelo': 'claude-3-sonnet-20240229',
                'prompt': 'Eres un experto en ventas y estrategias comerciales, especializado en cerrar deals y generar leads.',
                'temperatura': 0.8,
                'max_tokens': 1200,
                'voz': 'masculina'
            },
            {
                'nombre': 'Especialista Marketing',
                'rol': 'Marketing',
                'avatar': '🎨',
                'modelo': 'gemini-pro',
                'prompt': 'Eres un especialista en marketing digital y estrategias de marca, experto en campañas creativas.',
                'temperatura': 0.9,
                'max_tokens': 1500,
                'voz': 'femenina'
            },
            {
                'nombre': 'Desarrollador Senior',
                'rol': 'Desarrollo',
                'avatar': '💻',
                'modelo': 'ollama:codellama',
                'prompt': 'Eres un desarrollador senior experto en múltiples lenguajes de programación y arquitectura de software.',
                'temperatura': 0.3,
                'max_tokens': 2000,
                'voz': 'masculina'
            }
        ]
        
        for agente_data in agentes_ejemplo:
            agente = Agente()
            agente.from_dict(agente_data)
            db.session.add(agente)
        
        db.session.commit()
    
    # Crear salas de ejemplo si no existen
    if Sala.query.count() == 0:
        salas_ejemplo = [
            {
                'nombre': 'Sala Ejecutiva',
                'tipo': 'ejecutiva',
                'agentesActivos': [],
                'configuracion': {
                    'grabacionAutomatica': False,
                    'transcripcionVoz': True,
                    'notificacionesTelegram': False,
                    'backupAutomatico': True
                }
            },
            {
                'nombre': 'Sala Creativa',
                'tipo': 'creativa',
                'agentesActivos': [],
                'configuracion': {
                    'grabacionAutomatica': False,
                    'transcripcionVoz': True,
                    'notificacionesTelegram': False,
                    'backupAutomatico': True
                }
            }
        ]
        
        for sala_data in salas_ejemplo:
            sala = Sala()
            sala.from_dict(sala_data)
            db.session.add(sala)
            db.session.commit()
            
            # Crear armarios por defecto
            if sala_data['tipo'] == 'ejecutiva':
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

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de salud para verificar que el backend funciona"""
    return {
        'status': 'ok',
        'message': 'Backend de Agentes IA funcionando correctamente',
        'version': '6.0',
        'timestamp': os.popen('date').read().strip()
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
