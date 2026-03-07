from flask import request, jsonify
from . import auth_bp
from app.models import User,Role
from extensions import db
from config import Config  
import jwt
from datetime import timedelta,datetime,timezone
from functools import wraps
from app.services.auth_service import AuthService

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Требуется авторизация'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user = User.query.get(payload['user_id'])
            
            if not user or not user.is_active:
                return jsonify({'message': 'Пользователь удален или не найден'}), 401
            return f(user, *args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Токен истёк'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Неверный токен'}), 401
    
    return decorated_function


def require_role(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not args:
                return jsonify({"message": "Ошибка авторизаций"}), 401
            user = args[0]
            user_id = user.id
            data = user.roles
            user_roles_list = [role.name for role in data]
            require_role_name = role_name
            if require_role_name not in user_roles_list:
                return jsonify({"message": "Роль не найден"}), 403 
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
                return jsonify({"message": "Нет прав доступа"}),403
        return decorated_function
    return decorator
            

            



@auth_bp.route('/register',methods=["POST"])
def register():
    data = request.get_json()
    if "email" not in data:
        return jsonify({'message':'необходимо заполнить email'}),400
    email = data['email']
    if "@" not in email:
        return jsonify({'message':"Email не валиден"}), 400
    if type(email) != str:
        return jsonify({'message': "Email должен быть строковым типом данных"})
    
    if 'password' not in data:
        return jsonify({'message': 'Заполните все поля'}),400
    if 'first_name' not in data or 'last_name' not in data:
        return jsonify({'message': 'Заполните все поля'}),400
    
    
    password = data['password']
    first_name = data["first_name"]
    last_name = data["last_name"]

    if type(first_name) != str or type(last_name) != str:
        return jsonify({"message": "Должно быть текстом быть текстом"})
    
    user,error_message = AuthService.register(email,password,first_name,last_name)
    
    if error_message:
        return jsonify({'message': error_message}), 409
    
    return jsonify({'message': 'User registered successful','user_id': user.id}),201 
      


@auth_bp.route('/login',methods=['POST'])

def login():
    data = request.get_json()
    if "email" not in data or "password" not in data:
        return jsonify({'message': 'Email и пароль - обязательны'}), 400
    
    email = data["email"]
    password = data["password"]
    exists = User.query.filter_by(email=email).first()


    if not exists:
        return jsonify({"message": "Пользователь не найден"}),404
    if not exists.check_password(password):
        return jsonify({"message": "Неверный логин или пароль"}),401
    

    payload = {
        'user_id': exists.id,
        'exp': datetime.now(timezone.utc)+ timedelta(hours=1)
    }
    token = jwt.encode(payload,Config.JWT_SECRET_KEY,algorithm="HS256")

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

