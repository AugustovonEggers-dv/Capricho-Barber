import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.reservas.models import Reserva, Barbero
from datetime import date
import cloudinary
import cloudinary.uploader

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

@admin_bp.route('/barberos')
def gestionar_barberos():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    barberos = Barbero.query.all()
    return render_template('/admin/barberos/admin_barberos.html', barberos=barberos)

@admin_bp.route('/barberos/crear', methods=['GET', 'POST'])
def crear_barbero():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    nombre = request.form.get('nombre')
    foto = request.files.get('foto')
    
    # 1. Barrera de seguridad: Verificar que el nombre no esté vacío
    if not nombre or nombre.strip() == '':
        flash('El nombre del barbero es obligatorio.', 'error')
        return redirect(url_for('admin.gestionar_barberos'))
        
    # 2. Barrera de seguridad: Verificar que no exista un duplicado
    existente = Barbero.query.filter_by(nombre=nombre).first()
    if existente:
        flash(f'El barbero {nombre} ya existe en el sistema.', 'error')
        return redirect(url_for('admin.gestionar_barberos'))

    # 3. Proceso de Cloudinary
    nueva_url = None
    if foto and foto.filename != '':
        try:
            respuesta = cloudinary.uploader.upload(foto)
            nueva_url = respuesta.get('secure_url')
        except Exception as e:
            flash('Error al subir la imagen a la nube. Se creará sin foto.', 'error')
            print(f"Error Cloudinary: {e}")

    # 4. Creación y guardado seguro (El código solo llega aquí si pasó las barreras)
    nuevo_barbero = Barbero(nombre=nombre)
    if nueva_url:
        nuevo_barbero.foto_url = nueva_url
        
    db.session.add(nuevo_barbero)
    db.session.commit()
    flash(f'Barbero {nombre} añadido exitosamente.', 'success')
        
    return redirect(url_for('admin.gestionar_barberos'))
    
@admin_bp.route('barberos/alternar/<int:id>', methods=['POST'])
def alternar_barbero(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    barbero = Barbero.query.get_or_404(id)

    barbero.activo = not barbero.activo
    db.session.commit()

    estado = "activado" if barbero.activo else "dado de baja"
    flash (f'El barbero {barbero.nombre} fue {estado}', 'success')

    return redirect (url_for('admin.gestionar_barberos'))