from app import create_app
from app.models import User,Role,Permission
from extensions import db


application = create_app()

with application.app_context():
    user_email = "ismail@test.ru"
    role_name = "User"

    user = User.query.filter_by(email=user_email).first()
    role = Role.query.filter_by(name=role_name).first()

    if user and role:
        if role not in user.roles:
            user.roles.append(role)
            db.session.commit()