from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm
from .forms import PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from .. import db
from ..email import send_email


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        # Commit NOW not the end of the requst. The below method needs the
        # user ID!
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm your account', 'auth/email/confirm',
                   user=user, token=token)
        flash('A confirmation email has been sent to your email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


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


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or expired')
    return redirect(url_for('main.index'))


# This will call before any request in the app
# Bounce to auth.unconfirmed and skip the request if conditions met
@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
         and not current_user.confirmed \
         and request.endpoint[:5] != 'auth.':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm your account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A confirmation email has been sent to your email.')
    return redirect(url_for('main.index'))


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.add(current_user)
        flash('Your password has been changed.')
        return redirect(url_for('main.index'))
    return render_template('auth/change_password.html', form=form)


@auth.route('/password_reset_request', methods=['GET', 'POST'])
def password_reset_request():
    # This checks the user is not logged in
    # It's the opposite of if current_user.is_authenticated
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset your password',
                       'auth/email/reset_password', user=user, token=token)
            flash('An email with instructions on how to reset your password '
                  'has been sent.')
            return redirect(url_for('auth.login'))
    return render_template('auth/password_reset.html', form=form)


@auth.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.reset_password(token, form.password.data):
                flash('Your password has been reset.')
                return redirect(url_for('auth.login'))
            else:
                flash('The reset password link is invalid or expired')
        return redirect(url_for('main.index'))
    return render_template('auth/password_reset.html', form=form)


@auth.route('/change_email_request', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        token = current_user.generate_change_email_token(form.email.data)
        send_email(current_user.email, 'Change your Email Address',
                   'auth/email/change_email', user=current_user, token=token)
        flash('An email with a confirmation link has been sent to your new '
              'email address.')
        return redirect(url_for('main.index'))
    return render_template('auth/change_email_request.html', form=form)


# Note that <token> allows us to put it in the link
@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated')
    else:
        flash('The change email link is invalid or expired')
    return redirect(url_for('main.index'))
