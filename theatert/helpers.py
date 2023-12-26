import csv
import config
import datetime
import requests
import tmdbsimple as tmdb
from flask import redirect, render_template, url_for
from flask_login import current_user, login_user
from functools import wraps
from theatert import login_manager


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


def database_movies(movies, coming_soon=False):
    '''Return movie info as a list of movie dictionaries.'''
    
    data = []

    for movie in movies:
        m = tmdb.Movies(movie['tmdb_id'])

        temp = {k:v for k,v in m.info().items() if k in ['title', 'status', 'poster_path', 'popularity']}
        temp['active'] = movie['active']

        try:
            temp['release_date'] = display_date(m.info()['release_date'])
        except:
            temp['release_date'] = 'N/A'

        if coming_soon and temp['release_date'] != 'N/A':
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


def search_movie(title, year, db):
    '''Return query results as a list of movie dictionaries.'''
    
    result = tmdb.Search().movie(query=title, year=year)['results']
    
    data = []
    for movie in result:
        temp = {k:v for k,v in movie.items() if k in ['id', 'popularity', 'poster_path', 'release_date', 'title']}
        try:
            temp['release_date'] = display_date(temp['release_date'])
        except:
            temp['release_date'] = 'N/A'
        data.append(temp)

    return data


def date():
    '''Return current date'''
    
    now = datetime.datetime.now()
    return now.strftime('%b %d, %Y %H:%M:%S')


def display_date(date_str):
    '''Convert string to date object'''

    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    return date_obj.strftime('%b %d, %Y')


def get_title(tmdb_id):
    '''Given a movie's tmdb id return its title'''

    return tmdb.Movies(tmdb_id).info()['title']


def login_required(role="ANY"):
    '''Decorate routes to require login.'''

    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if (current_user.role != role) and (role != "ANY"):
                return login_manager.unauthorized()

            return f(*args, **kwargs)
        return decorated_function
    return wrapper


def released(tmdb_id):
    '''Find upcoming movies'''
    try:
        r = display_date(tmdb.Movies(tmdb_id).info()['release_date'] )
    except:
       return False

    return datetime.datetime.strptime(r, '%b %d, %Y') < datetime.datetime.now()


def sort_by(data):
    '''Sort movies by popularity, release date, and in alphabetical order'''

    def sort_dates(movies):
        '''Sort dates when N/A could be included'''

        na = list(filter(lambda x: x['release_date'] == 'N/A', movies))
        to_sort = list(filter(lambda x: x['release_date'] != 'N/A', movies))

        return sorted(to_sort, key=lambda x: (datetime.datetime.now() - datetime.datetime.strptime(x['release_date'], '%b %d, %Y'))) + na
    
    info = []
    info.append(sorted(data, key=lambda x: x['popularity'], reverse=True))
    info.append(sort_dates(data))
    info.append(data)
    return info


