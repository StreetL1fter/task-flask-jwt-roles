from flask import Flask,render_template,url_for
from extenstions import db
from config import Config
from .auth import auth_bp


def create_app():
    application = Flask(__name__)
    application.config.from_object(Config)
    db.init_app(application)
    import app.models
    application.register_blueprint(auth_bp,url_prefix='/auth')
    return application