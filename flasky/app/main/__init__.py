from flask import Blueprint

main = Blueprint('main', __name__)
# Call this Blueprint main
from ..models import Permission
# We want this available to Jinja
from . import views, errors
# Import from bottom to avoid circular dependencies IMPORTANT
# . means current package directory
# usually stick fo views and errors for each module


# This is a context processor that makes the var available to all templates
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
