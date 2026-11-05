from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, time, timedelta
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

            hoy = date.today()
            limite_futuro = hoy + timedelta(days=14)

            if not (hoy <= fecha_obj <= limite_futuro):
                flash('Solo puedes reservar turnos para los próximos 14 días.', 'error')
                return redirect(url_for('reservas.index'))

            if fecha_obj.weekday() in (0, 6):
                flash('La barbería permanece cerrada los domingos y lunes.', 'error')
                return redirect(url_for('reservas.index'))

            minutos_desde_medianoche = hora_obj.hour * 60 + hora_obj.minute
            apertura = 11 * 60
            cierre = 20 * 60

            if minutos_desde_medianoche < apertura or minutos_desde_medianoche > cierre:
                flash('El horario de atención es de 11:00 a 20:00hs.', 'error')
                return redirect(url_for('reservas.index'))

            if (minutos_desde_medianoche - apertura) % 45 != 0:
                flash('Los turnos solo se otorgan en bloques exactos de 45 minutos.', 'error')
                return redirect(url_for('reservas.index'))

            reserva_existente = Reserva.query.filter_by(
                fecha_reserva = fecha_obj,
                hora_reserva = hora_obj,
                barbero = barbero
            ).first()

            if reserva_existente:
                flash(f'Lo sentimos, {barbero} ya tiene un turno reservado para el { fecha_str } a las { hora_str }. Por favor, seleccione otro día, horario o barbero.', 'error')
                return redirect(url_for('reservas.index'))

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

    hoy = date.today()
    max_date = hoy + timedelta(days=14)

    return render_template('formulario.html')

@reservas_bp.route('/confirm/<int:id_reserva>')
def confirm(id_reserva):
    reserva = Reserva.query.get_or_404(id_reserva)

    return render_template('confirm.html', reserva=reserva)

@reservas_bp.route('/api/disponibilidad/<fecha>')
def api_disponibilidad(fecha):
    try: 
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'Error': "Formato de fecha inválido"})

    reservas_del_dia = Reserva.query.filter_by(fecha_reserva=fecha_obj).all()

    ocupados = {
        "Nacho": [],
        "Luciano": []
    }

    for r in reservas_del_dia:
        if r.barbero in ocupados:
            ocupados[r.barbero].append(r.hora_reserva.strftime('%H:%M'))

    return jsonify(ocupados)


