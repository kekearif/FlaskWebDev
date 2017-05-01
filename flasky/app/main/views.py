from flask import render_template
from . import main
from ..decorators import admin_required, permission_required
from flask_login import login_required
from ..models import Permission
# For the routing, use . to use from the __init__


@main.route('/')
def index():
    return render_template('index.html')


# Just an example of how the permissions could work
@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "This is for admins"


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "This is for moderators"


@main.route('/keke')
def for_keke():
    return "this is keke"
