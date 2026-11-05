import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.reservas.models import Reserva

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

    reservas = Reserva.query.order_by(Reserva.fecha_reserva.asc(), Reserva.hora_reserva.asc()).all()

    return render_template('admin/admin.html', reservas=reservas)