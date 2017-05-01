from ..models import User, Role
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, BooleanField
from wtforms import SelectField
from wtforms import ValidationError
from wtforms.validators import Length, Email, Required, Regexp


class EditProfileForm(FlaskForm):
    name = StringField('Real Name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[Required(),
                           Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                           'Usernames must have only letters, numbers,'
                                  'underscores or dots')])
    confirmed = BooleanField('Confirmed')
    # Default is String for ids, we want ints, role id is int
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextField('About me')
    submit = SubmitField('Submit')

    # Custom init to set the user
    # We need a user instance var to compare fields with
    def __init__(self, user, *args, **kargs):
        super(EditProfileAdminForm, self).__init__(*args, **kargs)
        # Python fancy way of making a list of tuples
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_username(self, field):
        # Current username will already be in the field
        # Only validate if it has changed
        if field.data != self.user.username and \
             User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')

    def validate_email(self, field):
        # Current email will already be in the field
        # Only validate if it has changed
        if field.data != self.user.email and \
             User.query.filter_by(email=field.data).first():
            raise ValidationError("Email is already registered.")
