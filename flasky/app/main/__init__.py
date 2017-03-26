from flask import Blueprint

main = Blueprint('main', __name__)
# Call this Blueprint main

from . import views, errors
# Import from bottom to avoid circular dependencies IMPORTANT
# . means current package directory
# usually stick fo views and errors for each module
