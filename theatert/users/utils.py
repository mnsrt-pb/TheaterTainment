from datetime import datetime
from flask import render_template, redirect, request, session, url_for
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


def guest():
    '''Decorate routes to require login.'''

    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if  current_user.is_authenticated:
                if current_user.role == "EMPLOYEE":
                    return redirect(url_for('employees.home'))
                else:
                    return redirect(url_for('users.home'))

            return f(*args, **kwargs)
        return decorated_function
    return wrapper


def guest_or_member():
    '''Decorate routes to require login.'''

    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                if current_user.role == "EMPLOYEE":
                    return redirect(url_for('employees.home'))

            return f(*args, **kwargs)
        return decorated_function
    return wrapper


def login_required(role="ANY"):
    '''Decorate routes to require login.'''

    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if role == "MEMBER":
                    session['form_data_login'] = request.form
                return login_manager.unauthorized()

            return f(*args, **kwargs)
        return decorated_function
    return wrapper


def date_obj(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

