from ..models import User
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import ValidationError
from flask_login import current_user


class LoginForm(Form):
    email = StringField('Email', validators=[Required(),
                        Length(1, 64), Email()])
    # New Length and Email validators here
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(),
                        Length(1, 64), Email()])
    username = StringField('Username', validators=[Required(),
                           Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                           'Usernames must have only letters, numbers,'
                                  'underscores or dots')])
    # Quote the passwordField python feature
    password = PasswordField('Password', validators=[Required(),
                             EqualTo('password2',
                             message="Passwords must match")])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    # These are named validate_field name so will also be invoked
    # These are our custom validators
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email is already registered.")


class ChangePasswordForm(Form):
    current_password = PasswordField('Current password',
                                     validators=[Required()])
    password = PasswordField('Password', validators=[Required(),
                             EqualTo('password2',
                             message="Passwords must match")])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Update Password')

    # Custom validator
    def validate_current_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError("Current password incorrect.")


class PasswordResetRequestForm(Form):
    email = StringField('Enter your registered email address',
                        validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField('Send Reset Link')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError("This email address is not registered.")


class PasswordResetForm(Form):
    email = StringField('Enter your registered email address',
                        validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('New password', validators=[Required(),
                             EqualTo('password2',
                             message="Passwords must match")])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError("This email address is not registered.")


class ChangeEmailForm(Form):
    email = StringField('Enter your new email address',
                        validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Enter your password', validators=[Required()])
    submit = SubmitField('Submit')

    def validate_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError("Password incorrect.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email is already registered.")
