from app import create_app
from extenstions import db
from app import models

application = create_app()

with application.app_context():
    db.create_all()
    print("База данных успешно создана")