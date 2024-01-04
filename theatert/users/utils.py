from flask import render_template
from flask_login import current_user
from functools import wraps
from theatert import login_manager

def apology(message, extends, code=400):
    '''Render message as an apology to user.'''

    def escape(s):
        '''
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        '''
        for old, new in [
            ('-', '--'),
            (' ', '-'),
            ('_', '__'),
            ('?', '~q'),
            ('%', '~p'),
            ('#', '~h'),
            ('/', '~s'),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template('other/apology.html', ext=extends, top=code, bottom=escape(message)), code


def login_required(role="ANY"):
    '''Decorate routes to require login.'''

    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if (current_user.role != role) and (role == "ANY"):
                return login_manager.unauthorized()

            return f(*args, **kwargs)
        return decorated_function
    return wrapper

