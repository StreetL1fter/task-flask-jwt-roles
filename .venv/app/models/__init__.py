from extenstions import db
from werkzeug.security import generate_password_hash, check_password_hash 




users_roles = db.Table('users_roles',
    db.Column('user_id',db.Integer,db.ForeignKey('users.id'),primary_key=True),
    db.Column('role_id',db.Integer,db.ForeignKey('roles.id'),primary_key=True))


roles_permissions = db.Table('roles_permissions',
        db.Column('role_id',db.Integer,db.ForeignKey('roles.id'),primary_key=True),
        db.Column('permission_id',db.Integer,db.ForeignKey('permissions.id'),primary_key=True))



class User(db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(200),nullable = False)
    password_hash = db.Column(db.String(200),nullable=False)
    first_name = db.Column(db.String(100),nullable = False)
    last_name = db.Column(db.String(100),nullable = False)
    is_active = db.Column(db.Boolean,default=True,nullable = False)
    roles = db.relationship('Role', secondary=users_roles, backref='users')

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    

    def get_permission(self):
        permissions = set()
        for role in self.roles:
            for permission in role.permissions:
                permissions.add(permission.name)
        return permissions
    
    def __repr__(self):
        return f'<User {self.first_name}>'

    
class Role(db.Model):

    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)

    permissions = db.relationship("Permission",secondary=roles_permissions,backref="roles")


class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False,unique=True)
