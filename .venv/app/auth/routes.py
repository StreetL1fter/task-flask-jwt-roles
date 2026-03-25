from flask import request, jsonify
from . import auth_bp
from app.models import User,Role,Blacklistedtoken
from extensions import db
from config import Config  
import jwt
from flask import current_app
from datetime import timedelta,datetime,timezone
from functools import wraps
from app.services.auth_service import AuthService
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import uuid





def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            current_app.logger.error("Требуется авторизация")
            return jsonify({'message': 'Требуется авторизация'}), 401
        
        token = auth_header.split(' ')[1]
        
        
        try:
            
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user = User.query.get(payload['user_id'])
            jti = payload['jti']
            is_blacklisted = Blacklistedtoken.query.filter_by(jwt_token_id=jti).first()

            if not user or not user.is_active:
                current_app.logger.error("Пользователь удалён или не найден")
                return jsonify({'message': 'Пользователь удален или не найден'}), 401
            
            if is_blacklisted is not None:
                current_app.logger.error("Ошибка авторизаций")
                return jsonify({"message": "Ошибка авторизаций"}),401

            return f(user, *args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            current_app.logger.error("Токен истёк")
            return jsonify({'message': 'Токен истёк'}), 401
        except jwt.InvalidTokenError:
            current_app.logger.error("Неверный токен")
            return jsonify({'message': 'Неверный токен'}), 401
    
    return decorated_function


def require_role(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not args:
                current_app.logger.error("Ошибка авторизаций")
                return jsonify({"message": "Ошибка авторизаций"}), 401
            user = args[0]
            user_id = user.id
            data = user.roles
            user_roles_list = [role.name for role in data]
            require_role_name = role_name
            if require_role_name not in user_roles_list:
                current_app.logger.error("Роль не найдена")
                return jsonify({"message": "Роль не найдена"}), 403 
            return f(user, *args, **kwargs)
        return decorated_function
    return decorator 


def require_permission(permission_name):
    def decorator(ismail):
        @wraps(ismail)
        def decorated_function(*args,**kwargs):
            user = args[0]
            all_role_permission = []
            for role in user.roles:
                for permission in role.permissions:
                    all_role_permission.append(permission.name)
            if permission_name in all_role_permission:
                return ismail(*args,**kwargs)
            else:
                current_app.logger.error("Нет прав доступа")
                return jsonify({"message": "Нет прав доступа"}),403
        return decorated_function
    return decorator
            
def register_routes(limiter):
    @auth_bp.route('/logout',methods=["POST"])
    def logout():

        data = request.headers.get('Authorization').split(' ')[1]
        try:
            token = jwt.decode(data,Config.JWT_SECRET_KEY,algorithm="HS256")
            jti = token.get("jti")
        except KeyError as ke:
            current_app.logger.warning("Токен некорректен")
            return jsonify({"message": "Токен некорректен"})
        try:
            if jti is not None:
                new_entry = Blacklistedtoken(jwt_token_id = jti)
                db.session.add(new_entry)
                db.session.commit()
                current_app.logger.info("Successfully logged out")
                return jsonify({"message":"Successfully logged out"}),200
        except:
            current_app.logger.error("500 Internal Server Error")
            return jsonify({"message": "500 Internal Server Error"}),500

    @auth_bp.route('/register',methods=["POST"])
    def register():
        data = request.get_json()
        if "email" not in data:
            current_app.logger.error("Необходимо заполнить email")
            return jsonify({'message':'необходимо заполнить email'}),400
        email = data['email']
        if "@" not in email:
            current_app.logger.error("Email не валиден")
            return jsonify({'message':"Email не валиден"}), 400
        if type(email) != str:
            current_app.logger.error("Email должен быть строковым типом данных")
            return jsonify({'message': "Email должен быть строковым типом данных"})
        
        if 'password' not in data:
            current_app.logger.error("Заполните все поля")
            return jsonify({'message': 'Заполните все поля'}),400
        if 'first_name' not in data or 'last_name' not in data:
            current_app.logger.error("Заполните все поля")
            return jsonify({'message': 'Заполните все поля'}),400
        
        
        password = data['password']
        first_name = data["first_name"]
        last_name = data["last_name"]

        if type(first_name) != str or type(last_name) != str:
            current_app.logger.error("Должно быть текстом быть текстом")
            return jsonify({"message": "Должно быть текстом быть текстом"})
        
        user,error_message = AuthService.register(email,password,first_name,last_name)
        
        if error_message:
            current_app.logger.error(error_message)
            return jsonify({'message': error_message}), 409
        
        current_app.logger.info("User registered successful")
        return jsonify({'message': 'User registered successful','user_id': user.id}),201 
        
    @auth_bp.route('/login',methods=['POST'])
    @limiter.limit("10 per minute")
    def login():
        from flask import current_app
        current_app.logger.info("Тестовый лог")
        data = request.get_json()
        if "email" not in data or "password" not in data:
            current_app.logger.error("Email и пароль - обязательны")
            return jsonify({'message': 'Email и пароль - обязательны'}), 400
            
        email = data["email"]
        password = data["password"]
        exists = User.query.filter_by(email=email).first()

        if not exists:
            current_app.logger.error("Пользователь не найден")
            return jsonify({"message": "Пользователь не найден"}),404
        if not exists.check_password(password):
            current_app.logger.error("Неверный логин или пароль")
            return jsonify({"message": "Неверный логин или пароль"}),401
            

        payload = {
            'user_id': exists.id,
            'exp': datetime.now(timezone.utc)+ timedelta(hours=1),
            'jti': str(uuid.uuid4()),
            
        }
        token = jwt.encode(payload,Config.JWT_SECRET_KEY,algorithm="HS256")

        current_app.logger.info("User successful")
        return jsonify({"message":"User successful","token": token}),200



    @auth_bp.route('/protected',methods=['GET'])
    @require_auth
    @require_permission("ismail:read")
    def get_protected_user(user):
        all_role_permission = []
        for role in user.roles:
            for permission in role.permissions:
                all_role_permission.append(permission.name)
        return jsonify({
            'message': 'Доступ разрешён',
            "email": user.email,
            'user_id': user.id,
            'roles': [role.name for role in user.roles],
            'permissions': all_role_permission
        }),200
    
    return auth_bp

