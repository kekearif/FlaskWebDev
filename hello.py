import os
from flask_script import Manager, Shell
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread
# Note that flask.ext is no longer used. We use flask_extname for import


app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
# The __name__ argument is used for flask to determine the root path of the app
# Note how the ext is init the same as the others, passing the app in
# This moment object is now available in templates
# The config is a dictionary. sec key is a config var used by flask and exts
# First wtf import is the flask ext
# The other two are from the wtforms package


basedir = os.path.abspath(os.path.dirname(__file__))
# The key should really be put in the system config
app.config['SECRET_KEY'] = 'sfd7868732hfayf92'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:////' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Basic database setup

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>'
app.config['FLASKY_ADMIN'] = 'keke.arif@snapask.co'
mail = Mail(app)


# Here we have a one to many relationship, one role can have many users
# We must declare this relationship. e.g users in role
# If we pull a model from our table we can now easily get all the users
# Backref allows us to pull a user and instantly get the role object


class Role(db.Model):
    __tablename__ = 'roles'  # Default var name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # Declare the relationship one - many , role - many users
    # This is the owning side
    # lazy='dynamic' allows us to add filters to the users
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):  # Override for testing
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # All models need prim key id
    username = db.Column(db.String(64), unique=True, index=True)
    age = db.Column(db.Integer)
    # Not the relationship declaration. Here we are just setting the link
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):  # Override for testing
        return '<User %r>' % self.username


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


# Put the method we want async in here
def send_async_email(app, msg):
    # Need to create this new app context for the thread work
    with app.app_context():
        mail.send(msg)


# **kwargs allows us to pass command line stuff e.g. user=user
def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    # Target and the args to pass, just start and return
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


# GET is the default if we provide dict need to add get if need it
# Here we need a dict for the POST method on the form
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    # Check all validators are ok
    if form.validate_on_submit:
        user = User.query.filter_by(username=form.name.data).first()
        user_role = Role.query.filter_by(name='User').first()
        if user is None:
            user = User(username=form.name.data, role=user_role)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User',
                           'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data  # When submit set the name
        redirect(url_for("index"))
        form.name.data = ''
    return render_template('index.html', name=session.get('name'), form=form,
                           known=session.get('known', False))
    # Get is standard dict method that returns None if nothing


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.route('/shitform')
def shitform():
    form = NameForm()
    return render_template('shitform.html', form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html')


# Tbis is my function definition
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


# Here we pass in the dictionary to the shell
# Add MigrateCommand to the script manager object that is attached to db
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':  # Only run dev server if script ex diretly
    manager.run()
