from flask import Flask,render_template,url_for
from extensions import db
from config import Config
from .auth import auth_bp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .auth.routes import register_routes
from dotenv import load_dotenv

load_dotenv()

def create_app():
    application = Flask(__name__)
    application.config.from_object(Config)
    import app.models
    db.init_app(application)
    limiter = Limiter(
        app = application,
        key_func=get_remote_address)
    register_routes(limiter)
    application.register_blueprint(auth_bp,url_prefix='/auth')
    return application

