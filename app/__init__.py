from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'YourSecretKey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:winston1826@localhost/flaskapp_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    with app.app_context():
        db.create_all()

    from .routes import main as main_routes
    app.register_blueprint(main_routes)

    return app
