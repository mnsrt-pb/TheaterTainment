import datetime
import tmdbsimple as tmdb
import os

from theatert import db
from theatert.models import Genre, genres


tmdb.API_KEY = os.environ.get('TMDB_API_KEY')


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

