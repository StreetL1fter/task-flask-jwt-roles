from flask import Blueprint,request



auth_bp = Blueprint("auth",__name__)


from .import routes
    
    