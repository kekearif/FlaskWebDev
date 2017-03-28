from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm
from .. import db


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        # Why don't we need to commit to the database?
        flash('You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # Note an easy error to make here is to forget the (), be careful!
    if form.validate_on_submit():
        # Get a user by email and check password matches hash
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # Next is a link it should go to if login presented from protected
            # Eg control panel protected so after login go there
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)
    # By default in templates but here we change dir to be organized


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))
    # Remember to include the blueprint main
