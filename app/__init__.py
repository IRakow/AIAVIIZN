from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config.config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    from app.routes import main, auth, properties, tenants
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(properties.bp)
    app.register_blueprint(tenants.bp)
    
    return app