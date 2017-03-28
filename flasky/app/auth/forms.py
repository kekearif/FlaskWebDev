from ..models import User
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import ValidationError


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
        if User.query.filter_by(email=field.data):
            raise ValidationError("Email is already registered.")