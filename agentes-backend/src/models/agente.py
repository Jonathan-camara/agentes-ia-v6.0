from src.models.user import db
from datetime import datetime
import json

class Agente(db.Model):
    __tablename__ = 'agentes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(10), nullable=False)
    estado = db.Column(db.String(20), default='inactivo')
    modelo = db.Column(db.String(100), nullable=False)
    conversaciones = db.Column(db.Integer, default=0)
    precision = db.Column(db.Float, default=85.0)
    aprendiendo = db.Column(db.Boolean, default=True)
    prompt = db.Column(db.Text, nullable=False)
    temperatura = db.Column(db.Float, default=0.7)
    max_tokens = db.Column(db.Integer, default=1000)
    telegram = db.Column(db.Boolean, default=False)
    telegram_token = db.Column(db.String(200))
    base_datos = db.Column(db.String(200))
    voz = db.Column(db.String(20), default='masculina')
    conocimiento_base = db.Column(db.Text)  # JSON string
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'rol': self.rol,
            'avatar': self.avatar,
            'estado': self.estado,
            'modelo': self.modelo,
            'conversaciones': self.conversaciones,
            'precision': self.precision,
            'aprendiendo': self.aprendiendo,
            'prompt': self.prompt,
            'temperatura': self.temperatura,
            'maxTokens': self.max_tokens,
            'telegram': self.telegram,
            'telegramToken': self.telegram_token,
            'baseDatos': self.base_datos,
            'voz': self.voz,
            'conocimientoBase': json.loads(self.conocimiento_base) if self.conocimiento_base else [],
            'fechaCreacion': self.fecha_creacion.isoformat(),
            'fechaActualizacion': self.fecha_actualizacion.isoformat()
        }
    
    def from_dict(self, data):
        for field in ['nombre', 'rol', 'avatar', 'estado', 'modelo', 'conversaciones', 
                     'precision', 'aprendiendo', 'prompt', 'temperatura', 'telegram', 
                     'base_datos', 'voz']:
            if field in data:
                if field == 'maxTokens':
                    setattr(self, 'max_tokens', data[field])
                elif field == 'telegramToken':
                    setattr(self, 'telegram_token', data[field])
                elif field == 'baseDatos':
                    setattr(self, 'base_datos', data[field])
                else:
                    setattr(self, field, data[field])
        
        if 'conocimientoBase' in data:
            self.conocimiento_base = json.dumps(data['conocimientoBase'])

class Conversacion(db.Model):
    __tablename__ = 'conversaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    agente_id = db.Column(db.Integer, db.ForeignKey('agentes.id'), nullable=False)
    sala_id = db.Column(db.Integer, db.ForeignKey('salas.id'))
    usuario = db.Column(db.String(100))
    mensaje_usuario = db.Column(db.Text, nullable=False)
    respuesta_agente = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    canal = db.Column(db.String(20), default='web')  # web, telegram, api
    
    agente = db.relationship('Agente', backref=db.backref('conversaciones_rel', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'agenteId': self.agente_id,
            'salaId': self.sala_id,
            'usuario': self.usuario,
            'mensajeUsuario': self.mensaje_usuario,
            'respuestaAgente': self.respuesta_agente,
            'timestamp': self.timestamp.isoformat(),
            'canal': self.canal
        }

