from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from app.extensions import db
from app.reservas.models import Reserva

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nombre = request.form.get('cliente_nombre')
        telefono = request.form.get('telefono')
        fecha_str = request.form.get('fecha_reserva')
        hora_str = request.form.get('hora_reserva')
        servicio = request.form.get('servicio')
        barbero = request.form.get('barbero')

        if not all([nombre, telefono, fecha_str, hora_str, servicio]):
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('reservas.index'))

        try:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora_obj = datetime.strptime(hora_str, '%H:%M').time()

            # 4. Creación de la instancia del modelo
            nueva_reserva = Reserva(
                cliente_nombre=nombre,
                telefono=telefono,
                fecha_reserva=fecha_obj,
                hora_reserva=hora_obj,
                servicio=servicio,
                barbero=barbero
            )

            db.session.add(nueva_reserva)
            db.session.commit()
            
            return redirect(url_for('reservas.confirm', id_reserva=nueva_reserva.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Hubo un error al procesar la reserva. Intente de nuevo.', 'error')
            print(f"Error de BD: {e}") 
            return redirect(url_for('reservas.index'))

    return render_template('formulario.html')

@reservas_bp.route('/confirm/<int:id_reserva>')
def confirm(id_reserva):
    reserva = Reserva.query.get_or_404(id_reserva)

    return render_template('confirm.html', reserva=reserva)




