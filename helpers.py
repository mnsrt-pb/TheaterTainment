import csv
import config
import datetime
import hashlib 
import requests
import tmdbsimple as tmdb
import urllib.parse
# import pytz

from flask import redirect, render_template, session
from functools import wraps

tmdb.API_KEY = config.api_key


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


def check_password_hash(pwhash, password):
    return pwhash == generate_password_hash(password)


def database_movies(movies, coming_soon=False):
    '''Return movie info as a list of dictionaries. Every movie is a dictionary with movies's data '''
    
    data = []

    for movie in movies:
        m = tmdb.Movies(movie['tmdb_id'])

        temp = {k:v for k,v in m.info().items() if k in ['title', 'status', 'poster_path', 'popularity']}
        temp['active'] = movie['active']
        temp['release_date'] = display_date(m.info()['release_date'])
        if coming_soon:
            if datetime.datetime.strptime(temp['release_date'], '%b %d, %Y') < datetime.datetime.now():
                continue
        
        g = []
        for genre in m.info()['genres']:
            g.append(genre['name'])
        temp['genres'] = g

        for item in m.release_dates()['results']:
            if item['iso_3166_1'] == 'US':
                temp['rating'] = item["release_dates"][0]['certification']
                break

        data.append(temp)
    return sort_by(data)


def date():
    '''Return current date'''
    # now = datetime.datetime.now(pytz.timezone('US/Eastern'))
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')


def display_date(date_str):
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    return date_obj.strftime('%b %d, %Y')


def generate_password_hash(password):
    hash = hashlib.md5(password.encode())
    return hash.hexdigest()


def member_login_required(f):
    '''
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    '''

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        elif session.get('user_type') != 'member':
            return redirect('/')
        return f(*args, **kwargs)

    return decorated_function


def sort_by(data):
    '''Sort movies by popularity, release date, and in alphabetical order'''
    info = []
    info.append(sorted(data, key=lambda x: x['popularity'], reverse=True))
    info.append(sorted(data, key=lambda x: (datetime.datetime.now() - datetime.datetime.strptime(x['release_date'], '%b %d, %Y'))))
    info.append(data)
    return info


def staff_login_required(f):
    '''
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    '''

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/e-login')
        elif session.get('user_type') != 'staff':
            return redirect('/')
        return f(*args, **kwargs)

    return decorated_function


def upcoming():
    '''Find upcoming movies'''
    # Movie release date must be later than current date
    # Movie must not already be in database
    return 


def validate_password(password):
    has_num, has_upper, has_lower, has_special_char = False, False, False, False

    for char in password:
        if char.isnumeric():
            has_num = True
        elif char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char in '[@_!#$%^&*()<>?/\|}{~:]':
            has_special_char = True

    print(has_num, has_upper, has_lower, has_special_char)
    return has_num and has_upper and has_lower and has_special_char and (len(password) >= 8)
        
