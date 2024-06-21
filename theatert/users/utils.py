from datetime import datetime
from flask import render_template, redirect, request, session, url_for
from flask_login import current_user
from functools import wraps
from theatert import login_manager
from theatert import db


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


def date_obj(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def guest():
    '''Decorate routes to not allow logged users.'''

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
    '''Decorate routes to require guests or Member accounts only.'''

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


def populate_db():
    from theatert.models import Seat, Auditorium, Movie, Employee

    # Auditoriums 
    auditoriums = [
        Auditorium(rows=8, cols=12),
        Auditorium(rows=8, cols=12),
        Auditorium(rows=6, cols=18),
        Auditorium(rows=6, cols=10)
    ]
    db.session.add_all(auditoriums)
    db.session.commit()

    # Seats 
    seat_configurations = {
        1 : { 'A': ['normal'] * 12,
              'B': ['normal'] * 12,
              'X': ['empty'] * 12,
              'C': ['companion', 'wheelchair', 'empty', 'wheelchair', 'companion', 
                     'companion', 'wheelchair', 'empty', 'wheelchair', 'companion', 
                     'empty', 'empty'],
              'D': ['normal'] * 10 + ['empty'] * 2,
              'E': ['normal'] * 10 + ['empty'] * 2,
              'F': ['normal'] * 10 + ['empty'] * 2,
              'G': ['normal'] * 10 + ['empty'] * 2 },

        2 : { 'A': ['normal'] * 12,
              'B': ['normal'] * 12,
              'X': ['empty'] * 14,
              'C': ['companion', 'wheelchair', 'empty', 'wheelchair', 'companion', 
                    'companion', 'wheelchair', 'empty', 'wheelchair', 'companion'],
              'D': ['empty'] * 2 + ['normal'] * 10,
              'E': ['empty'] * 2 + ['normal'] * 10,
              'F': ['empty'] * 2 + ['normal'] * 10,
              'G': ['empty'] * 2 + ['normal'] * 10 },

        3 : { 'A': ['normal'] * 2 + ['empty'] + ['normal'] * 12 + ['empty'] + ['normal'] * 2,
              'B': ['normal'] * 2 + ['empty'] + ['normal'] * 12 + ['empty'] + ['normal'] * 2,
              'C': ['normal'] * 2 + ['empty'] + ['normal'] * 12 + ['empty'] + ['normal'] * 2,
              'D': ['normal'] * 2 + ['empty'] + ['normal'] * 12 + ['empty'] + ['normal'] * 2,
              'E': ['normal'] * 2 + ['empty'] + ['normal'] * 12 + ['empty'] + ['normal'] * 2,
              'F': ['normal'] * 2 + ['empty'] * 2 + ['normal'] + 
                   ['companion'] + ['wheelchair'] * 2 + ['companion'] * 2 + ['wheelchair'] * 2 + ['companion'] + 
                   ['normal'] + ['empty'] * 2 + ['normal'] * 2 },

        4 : { 'A': ['normal'] * 10,
              'B': ['normal'] * 10,
              'C': ['normal'] * 10,
              'D': ['normal'] * 10,
              'E': ['normal'] * 10,
              'F': ['empty'] + ['companion'] + ['wheelchair'] * 2 + ['companion'] * 2 + 
                   ['wheelchair'] * 2 + ['companion'] + ['empty']}
    }

    seats = []
    for (auditorium, config) in seat_configurations.items():
        for row_index, (row_name, seat_types) in enumerate(config.items(), start=1):
            for col_index, seat_type in enumerate(seat_types, start=1):
                seats.append(Seat(row=row_index, col=col_index, row_name=row_name, seat_type=seat_type, auditorium_id=auditorium))

    db.session.add_all(seats)
    db.session.commit()


def clear_session():
    if session.get('form_data'):
        session.pop('form_data')
        
    if session.get('form2_data'):
        session.pop('form2_data')

    if session.get('form_data_login'):
        session.pop('form_data_login')