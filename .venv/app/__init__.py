from flask import Flask,render_template,url_for
from extensions import db
from config import Config
from .auth import auth_bp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .auth.routes import register_routes
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler as RF
import os

load_dotenv()

def create_app():
    application = Flask(__name__)
    if not os.path.exists("logs"):
        os.mkdir("logs")
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    file_handler = RF('logs/app.log',maxBytes=10240, backupCount=10,encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    application.logger.addHandler(file_handler)
    application.logger.setLevel(logging.INFO)
    application.config.from_object(Config)
    import app.models
    db.init_app(application)
    limiter = Limiter(
        app = application,
        key_func=get_remote_address)
    register_routes(limiter)
    application.register_blueprint(auth_bp,url_prefix='/auth')
    return application

