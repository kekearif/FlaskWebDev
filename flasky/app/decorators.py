from functools import wraps
from flask import abort
from flask.ext.login import current_user


def permission_required(permission):
    def decorator(f):
        # @wraps makes testing easier
        @wraps
        def decorated_function(*args, **kargs):
            if not current_user.can(permission):
                abort(404)
            return f(*args, **kargs)
        return decorated_function
    return decorator
