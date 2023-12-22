import csv
import datetime
import hashlib 
import requests
# import pytz

from flask import redirect, render_template, session
from functools import wraps


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


def get_movie_info(movie_id):
    '''Given a movie id, find the movie's info'''

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5MzU5Mzc1NDhjMDNlMDJjMGExNjg4ZGQyMjg3MjgxMSIsInN1YiI6IjY1ODM4NTVkZmJlMzZmNGFhZDdmMzVkYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ._Wa_5xjrCSE08JXWIe6t8-etYZm0xRNvnYr7C5Y5GuE"
    }   

    response = requests.get(url, headers=headers).json()
    return response


def now_playing():
    '''Find movies that are now playing'''

    url = 'https://api.themoviedb.org/3/movie/now_playing?language=en-US&page=1'
    
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5MzU5Mzc1NDhjMDNlMDJjMGExNjg4ZGQyMjg3MjgxMSIsInN1YiI6IjY1ODM4NTVkZmJlMzZmNGFhZDdmMzVkYiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ._Wa_5xjrCSE08JXWIe6t8-etYZm0xRNvnYr7C5Y5GuE'
    }

    response = requests.get(url, headers=headers).json()['results']

    movie_ids = []
    for movie in response:
        movie_ids.append((movie['id'], movie['title']))

    return movie_ids


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


def movie_info(movies, coming_soon=False):
    '''Return movie info as a list of dictionaries. Every movie is a dictionary.'''
    data, info, i = [], [], 0

    for movie in movies:
        temp = {}
        tmdb_info =  get_movie_info(movie['tmdb_id'])
        temp['title'] = movie['title']
        temp['active'] = movie['active']
        temp['release_date'] = display_date(tmdb_info['release_date'])
        if coming_soon:
            if datetime.datetime.strptime(temp['release_date'], '%b %d, %Y') < datetime.datetime.now():
                continue
        temp['status'] = tmdb_info['status']
        temp['poster_path'] = tmdb_info['poster_path']
        temp['adult'] = tmdb_info['adult']
        temp['popularity'] = tmdb_info['popularity']
        g = []
        for genre in tmdb_info['genres']:
            g.append(genre['name'])
        temp['genres'] = g
        data.append(temp)
        i += 1
        print(datetime.datetime.strptime(temp['release_date'], '%b %d, %Y') - datetime.datetime.now())
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


# User should be able to add upcoming movies
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
        
