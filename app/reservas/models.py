from app.extensions import db
from datetime import datetime

class Reserva(db.Model):
    __tablename__= 'reservas'

    id = db.Column(db.Integer, primary_key = True)
    cliente_nombre = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    fecha_reserva = db.Column (db.Date, nullable=False)
    hora_reserva = db.Column(db.Time, nullable=False)
    barbero = db.Column(db.Enum('Nacho','Luciano'), nullable=False)
    servicio = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def __repr__ (self):
    return f'<Reserva {self.cliente_nombre} - {self.fecha_reserva}>'