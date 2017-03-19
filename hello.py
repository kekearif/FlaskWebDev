import os
from flask_script import Manager
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
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
app.config['SECRET_KEY'] = 'sfd7868732hfayf92'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:////' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)
# Basic database setup


class Role(db.Model):
    __tablename__ = 'roles'  # Default var name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):  # Override for testing
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # All models need prim key id
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):  # Override for testing
        return '<User %r>' % self.username


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


# GET is the default if we provide dict need to add get if need it
# Here we need a dict for the POST method on the form
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    # Check all validators are ok
    if form.validate_on_submit:
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name now!')
            # flash sends a message in the response
        session['name'] = form.name.data  # When submit set the name
        redirect(url_for("index"))
        form.name.data = ''
    return render_template('index.html', name=session.get('name'), form=form)
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


if __name__ == '__main__':  # Only run dev server if script ex diretly
    manager.run()
