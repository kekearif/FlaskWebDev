from flask import render_template, abort, flash, redirect, url_for
from . import main
from .forms import EditProfileForm
from ..decorators import admin_required, permission_required
from flask_login import login_required, current_user
from ..models import Permission, User
from .. import db
# For the routing, use . to use from the __init__


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Note we are already logged in here
    form = EditProfileForm()
    # This is a callback
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


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
