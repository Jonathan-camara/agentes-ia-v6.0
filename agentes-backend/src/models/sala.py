from src.models.user import db
from datetime import datetime
import json

class Sala(db.Model):
    __tablename__ = 'salas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # ejecutiva, creativa
    agentes_activos = db.Column(db.Text)  # JSON array de IDs
    grabando = db.Column(db.Boolean, default=False)
    configuracion = db.Column(db.Text)  # JSON object
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'agentesActivos': json.loads(self.agentes_activos) if self.agentes_activos else [],
            'grabando': self.grabando,
            'configuracion': json.loads(self.configuracion) if self.configuracion else {},
            'fechaCreacion': self.fecha_creacion.isoformat(),
            'fechaActualizacion': self.fecha_actualizacion.isoformat()
        }
    
    def from_dict(self, data):
        for field in ['nombre', 'tipo', 'grabando']:
            if field in data:
                setattr(self, field, data[field])
        
        if 'agentesActivos' in data:
            self.agentes_activos = json.dumps(data['agentesActivos'])
        
        if 'configuracion' in data:
            self.configuracion = json.dumps(data['configuracion'])

class Mensaje(db.Model):
    __tablename__ = 'mensajes'
    
    id = db.Column(db.Integer, primary_key=True)
    sala_id = db.Column(db.Integer, db.ForeignKey('salas.id'), nullable=False)
    agente_id = db.Column(db.Integer, db.ForeignKey('agentes.id'))
    tipo = db.Column(db.String(20), nullable=False)  # usuario, agente, sistema
    texto = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    metadatos = db.Column(db.Text)  # JSON object para datos adicionales
    
    sala = db.relationship('Sala', backref=db.backref('mensajes_rel', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'salaId': self.sala_id,
            'agenteId': self.agente_id,
            'tipo': self.tipo,
            'texto': self.texto,
            'timestamp': self.timestamp.isoformat(),
            'metadatos': json.loads(self.metadatos) if self.metadatos else {}
        }

class Archivo(db.Model):
    __tablename__ = 'archivos'
    
    id = db.Column(db.Integer, primary_key=True)
    sala_id = db.Column(db.Integer, db.ForeignKey('salas.id'), nullable=False)
    armario_id = db.Column(db.Integer, db.ForeignKey('armarios.id'))
    nombre = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(100))
    tamano = db.Column(db.Integer)
    ruta_archivo = db.Column(db.String(500))
    contenido = db.Column(db.Text)  # Para archivos de texto
    metadatos = db.Column(db.Text)  # JSON object
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    
    sala = db.relationship('Sala', backref=db.backref('archivos_rel', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'salaId': self.sala_id,
            'armarioId': self.armario_id,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'tamano': self.tamano,
            'rutaArchivo': self.ruta_archivo,
            'contenido': self.contenido,
            'metadatos': json.loads(self.metadatos) if self.metadatos else {},
            'fechaSubida': self.fecha_subida.isoformat()
        }

class Armario(db.Model):
    __tablename__ = 'armarios'
    
    id = db.Column(db.Integer, primary_key=True)
    sala_id = db.Column(db.Integer, db.ForeignKey('salas.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    sala = db.relationship('Sala', backref=db.backref('armarios_rel', lazy=True))
    archivos = db.relationship('Archivo', backref='armario', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'salaId': self.sala_id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'archivos': [archivo.to_dict() for archivo in self.archivos],
            'fechaCreacion': self.fecha_creacion.isoformat()
        }

class ConocimientoSala(db.Model):
    __tablename__ = 'conocimiento_salas'
    
    id = db.Column(db.Integer, primary_key=True)
    sala_id = db.Column(db.Integer, db.ForeignKey('salas.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # conocimiento, patron, analisis
    contenido = db.Column(db.Text, nullable=False)
    metadatos = db.Column(db.Text)  # JSON object
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    sala = db.relationship('Sala', backref=db.backref('conocimiento_rel', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'salaId': self.sala_id,
            'tipo': self.tipo,
            'contenido': self.contenido,
            'metadatos': json.loads(self.metadatos) if self.metadatos else {},
            'fechaCreacion': self.fecha_creacion.isoformat()
        }

