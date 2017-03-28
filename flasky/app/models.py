from . import db
from . import login_manager
# From current package eg app __init__ import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    # lazy = 'dynamic' allows us to apply filters

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):  # Here we inherit from two classes
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))

    # Custom property getter
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # Custom property setter
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    # Note that we have inherited from UserMixin the methods:
    # is_authenticated, is_active, is_anonymous, get_id


# This callback requires a method with a single param that returns an int
# The param is a user_id it passes in (most likely the primary_key)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    # get returns a user by querying the primary_key
    # get is a primary_key query
    # This will load the user each time we need it