from . import db
from . import login_manager
# From current package eg app __init__ import db login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from datetime import datetime
import hashlib
from markdown import markdown
import bleach


class Follow(db.Model):
    # Two primary keys Self-Referential relationship
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    # Note that a relationship is not actually displayed in the database UI
    # The relationship is just so we can query
    # lazy = 'dynamic' allows us to apply filters

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
            # Note that 0xff is 11111111 in binary, all the flags on
            # The | operator combines flags
            }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            # Access dict via key and then tuple element
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):  # Here we inherit from two classes
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    # Note the use of defualts here
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    # Text does not require a max length
    about_me = db.Column(db.Text())
    # Here we are passing functions to call
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # Here is the many to many relationship
    # Need to specify which foreign key to use here because there are two
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    # Custom init to assign a role
    # Note we pass a variable number of arguments eg User(username='bleh')
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions='0xff').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        # So we can see our own posts in followed too
        self.follow(self)

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

    # 60 min standard exp time
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        # Don't need expiration here as not generating
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})
        # Note we use a new token method with reset instead of confirm

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_change_email_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        # Here we put the email in the token
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        self.email = data.get('new_email')
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        # This will commit at the end of a request

    def gravatar(self, size=100, default='identicon', rating='g'):
        # note how with Python don't need to first define url, not static typed
        # What is this?
        if request.is_secure:
            url = 'http://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        # Note the use of or if not true
        hash = self.avatar_hash or hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    @staticmethod
    def generate_fake(count=100):
        # Note how we can do an import here
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        # Set the randomizer seed for forgery
        seed()
        # 0 .. 100 , generate 100 items
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True)
                     )
            db.session.add(u)
            # Username and email but be unique in our database
            # Check we don't accidently get a duplicate
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def follow(self, user):
        if not self.is_following(user):
            # Note we can use the backrefs we made here
            f = Follow(followed=user, follower=self)
            db.session.add(f)

    def unfollow(self, user):
        if self.is_following(user):
            f = self.followed.filter_by(followed_id=user.id).first()
            if f:
                db.session.delete(f)

    def is_followed_by(self, user):
        # Standard relationship query here
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    # Define property do not need to call a method this way
    @property
    def followed_posts(self):
        # Here we will use a table join so we can use a single query
        # First line sets the join
        # Second line we can set a filter, here we filter Follow table by id
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
                .filter(Follow.follower_id == self.id)

    # DB method to fix self follows
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

# Add some functionality to the non-logged in user object that flask_login uses
# We can call can and is_administrator on non-logged in users now
# e.g users we get from current_user
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser
# Set the actual class for the login manager


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80
    # These are hex codes from binary.
    # Note they are class vars not instance with self


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def generate_fake(count=100):
        # Note how we can do an import here
        from random import seed, randint
        import forgery_py

        # Set the randomizer seed for forgery
        seed()
        # 0 .. 100 , generate 100 items
        user_count = User.query.count()
        for i in range(count):
            # Can use offset like an array
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            # No unique fields here so don't need to error check
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Post.body, 'set', Post.on_changed_body)


# This callback requires a method with a single param that returns an int
# The param is a user_id it passes in (most likely the primary_key)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    # get returns a user by querying the primary_key
    # get is a primary_key query
    # This will load the user each time we need it
