from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
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

    inicio = datetime.combine(reserva.fecha_reserva, reserva.hora_reserva)
    fin = inicio + timedelta(minutes=45)

    fmt = "%Y%m%dT%H%M%S"

    google_cal_url = (
        f"https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text=Turno+en+Capricho+Barber"
        f"&dates={inicio.strftime(fmt)}/{fin.strftime(fmt)}"
        f"&details=Turno+para+{reserva.servicio.replace(' ', '+')}+con+{reserva.barbero}."
        f"&location=Capricho+Barber"
    )

    return render_template('confirm.html', reserva=reserva, google_cal_url=google_cal_url)

@reservas_bp.route('/calendario/apple/<int:id_reserva>')
def descargar_ics(id_reserva):
    reserva = Reserva.query.get_or_404(id_reserva)

    inicio = datetime.combine(reserva.fecha_reserva, reserva.hora_reserva)
    fin = inicio + timedelta(minutes=45)

    fmt = "%Y%m%dT%H%M%S"

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Capricho Barber//Reservas//ES
BEGIN:VEVENT
UID:turno_{reserva.id}@caprichobarber.com
DTSTAMP:{datetime.now().strftime(fmt)}
DTSTART:{inicio.strftime(fmt)}
DTEND:{fin.strftime(fmt)}
SUMMARY:Turno en Capricho Barber
DESCRIPTION:Turno para {reserva.servicio} con {reserva.barbero}.
LOCATION:Capricho Barber
BEGIN:VALARM
TRIGGER:-PT4H
ACTION:DISPLAY
DESCRIPTION:¡En 4 horas es tu turno en Capricho Barber!
END:VALARM
END:VEVENT
END:VCALENDAR"""

    return Response(
        ics_content,
        mimetype='text/calendar',
        headers={'Content-Disposition': f'attachment; filename=Turno_CaprichoBarber.ics'}
    )

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


