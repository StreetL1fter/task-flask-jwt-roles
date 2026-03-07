from app.models import User,Role
from extensions import db
from flask import request,jsonify
from app.auth import routes


class AuthService:
    @staticmethod
    def register(email, password, first_name, last_name):

        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Дубликат'}), 409
        user = User(email=email,
                    first_name = first_name,
                    last_name = last_name,
                    is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user,None  