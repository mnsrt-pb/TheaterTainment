import datetime
import tmdbsimple as tmdb
import os

from flask import redirect, render_template, url_for
from flask_login import current_user, login_user
from functools import wraps
from theatert import db, login_manager
from theatert.models import Genre, genres


tmdb.API_KEY = os.environ.get('TMDB_API_KEY')


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


def search_movie(title, year):
    '''Return query results as a list of movie dictionaries.'''
    
    result = tmdb.Search().movie(query=title, year=year)['results']
    
    data = []
    for movie in result:
        temp = {k:v for k,v in movie.items() if k in ['id', 'popularity', 'poster_path', 'title']}
        try:
            temp['release_date'] = datetime.datetime.strptime(movie['release_date'], '%Y-%m-%d').date()
        except:
            pass
        data.append(temp)

    return data


def add_genres(movie, info):
    for g in info['genres']:
        genre = Genre.query.filter_by(name=g['name']).first()
        if not genre:
            genre = Genre(
                name = g['name']
            )
            db.session.add(genre)
            db.session.commit()
        if not genre in movie.genres:
            m_g = genres.insert().values(movie_id=movie.id, genre_id=genre.id)
            db.session.execute(m_g)
        

def add_rating(movie, data):         
    for item in data.release_dates()['results']:
        if item['iso_3166_1'] == 'US':
            for r in item['release_dates']:
                if r['certification'] != "":
                    movie.rating = r['certification']
                    break
            break


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


def route_name(title):
    title = ''.join(c for c in title.lower() if c.isalnum() or c.isspace())
    title = '-'.join(title.split())
    return title


def update_choices(images, videos):
    posters = [('None', 'Select Poster')]
    i = 1
    for b in images['posters']:
        posters.append((b['file_path'], str(i)))
        i += 1

    backdrops = [('None', 'Select Backdrop')]
    i = 1
    for b in images['backdrops']:
        backdrops.append((b['file_path'],str(i)))
        i += 1

    trailers = [('None', 'Select Trailers')]
    i = 1
    for v in videos:
        trailers.append((v['key'], str(i) + '. ' + v['name'] ))
        i += 1
    return posters, backdrops, trailers

