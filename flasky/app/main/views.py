from flask import render_template, session, redirect, url_for, current_app
from . import main
# For the routing, use . to use from the __init__
from .forms import NameForm
# From the forms module import NameForm (same dir)
from .. import db
# From the package space above e.g. app import db
# Use . to get from the __init__
from ..models import User, Role
# From the space above import the User object from models
from ..email import send_email


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        role = Role.query.filter_by(name='User').first()
        if user is None:
            user = User(username=form.name.data, role=role)
            db.session.add(user)
            session['known'] = False
            if current_app.config['FLASKY_ADMIN']:
                send_email(current_app.config['FLASKY_ADMIN'], 'New User',
                           'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        # note that .index means current blueprint index function
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False))
