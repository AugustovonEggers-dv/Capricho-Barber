from flask import Flask
from app.extensions import db

def create_app():
    app = Flask(__name__)
    
    app.config.from_object('app.config.Config')
    db.init_app(app)

    from app.reservas import models

    with app.app_context():
        db.create_all()

    from app.reservas.routes import reservas_bp
    app.register_blueprint(reservas_bp, url_prefix='/')

    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    return app