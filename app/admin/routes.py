import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.reservas.models import Reserva
from datetime import date

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')

        if password == os.environ.get('ADMIN_PASSWORD'):
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Contraseña incorrecta', 'error')

    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    filtro_fecha = request.args.get('filtro_fecha')
    filtro_barbero = request.args.get('filtro_barbero')

    filtros = []

    if filtro_fecha == 'hoy':
        filtros.append(Reserva.fecha_reserva == date.today())

    if filtro_barbero in ['Nacho', 'Luciano']:
        filtros.append(Reserva.barbero == filtro_barbero)

    reservas = Reserva.query.filter(*filtros).order_by(
        Reserva.fecha_reserva.asc(),
        Reserva.hora_reserva.asc()
    ).all()

    return render_template('admin/admin.html', reservas=reservas, filtro_fecha=filtro_fecha,filtro_barbero=filtro_barbero)
    
@admin_bp.route('/eliminar/<int:id_reserva>', methods=['POST'])
def eliminar_reserva(id_reserva):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    reserva = Reserva.query.get_or_404(id_reserva)

    try:
        db.session.delete(reserva)
        db.session.commit()
        flash('El turno fue cancelado y eliminado satisfactoriamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash('Hubo un error al intentar eliminar la reserva.', 'error')
        print(f"Error al eliminar: {e}")

    return redirect(url_for('admin.dashboard'))