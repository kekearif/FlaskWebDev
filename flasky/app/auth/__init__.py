from flask import Blueprint

auth = Blueprint('auth', __name__)
# Call this Blueprint auth

from . import views
