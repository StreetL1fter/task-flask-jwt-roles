import os
from datetime import timedelta

class Config():
    SQLALCHEMY_DATABASE_URI =  "sqlite:///test-task.db"
    SQLALCHEMY_TRACK_MODIFICATIONS  = False
    SECRET_KEY = 'my-secret-motherfucker-key'
    JWT_SECRET_KEY = 'super-secure-jwt-secret-key-for-production-use' 
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

class DevelopmentClass(Config):
    DEBUG = True

class ProductionClass(Config):
    DEBUG = True

