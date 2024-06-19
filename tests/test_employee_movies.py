''' Test movie management '''

from datetime import datetime, timedelta
from flask import url_for
from flask_login import current_user
from tests.utils import login_employee
from theatert import db
from theatert.models import Movie, Change, Genre, genres
from theatert.config_test import movie_a



import pytest
import os


if os.environ.get('SKIP_TEST_EMPLOYEE_MOVIES', 'false').lower() == 'true':
    pytestmark = pytest.mark.skip("Skipping tests in test_employee_movies.py")


''' SEARCH, ADD, DELETE AND FETCH MOVIE '''
@pytest.mark.skip
def test_search_movie(client_users):
    ''' Test search movie successfully'''
    login_employee(client_users)

    # Test that page loads correctly
    response = client_users.get(url_for('employees.movies.add_movie'))
    assert response.status_code == 200

    # Test searching for movie with title only
    response = client_users.post(url_for('employees.movies.add_movie'), 
                                    data={'title': movie_a['title']}, 
                                    follow_redirects=True)
    assert response.status_code == 200
    assert b'Add Movie' in response.data
    
    # Test searching for movie with title and releasae year
    response = client_users.post(url_for('employees.movies.add_movie'), 
                                    data={'title': movie_a['title'], 
                                          'release_year' : movie_a['release_date'].year}, 
                                    follow_redirects=True)
    assert response.status_code == 200
    assert b'Add Movie' in response.data


@pytest.mark.skip
def test_add_movie(client_users):
    ''' Test add movie successfully'''
    login_employee(client_users)
    current_id =  current_user.id

    # Test add movie feature
    response = client_users.post(url_for('employees.movies.add_movie'), 
                                        data={'m_id': movie_a['tmdb_id']}, 
                                        follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/movies/all-movies'

    with client_users.application.app_context():
        movie = Movie.query
        movie_total, movie = movie.count(), movie.first()
        movie_total == 1
        assert movie.id == 1
        assert movie.tmdb_id == movie_a['tmdb_id']

        change = Change.query
        change_total, change = change.count(), change.first()
        change_total == 1
        assert change.employee_id == current_id
        assert change.action == 'added'
        assert change.table_name == 'movie'
        assert change.data_id == movie.id

        genres = Genre.query.count()
        assert genres != 0
    
    # Test employee' change displayed in home page
    response = client_users.get(url_for('employees.home'))
    assert b'Movie</td>' in response.data
    assert b'added</td>' in response.data
    assert f"{movie_a['title']}</td>".encode('utf-8') in response.data


@pytest.mark.skip
def test_fetch_movie(client_movie):
    ''' Test adding a movie that already exists. 
    This should fetch new data and update movie. '''
    login_employee(client_movie)
    current_id =  current_user.id

    with client_movie.application.app_context():
        movie = Movie.query.first()
        movie.overview = None
        db.session.commit()

    # Test fetch api data for movie feature
    response = client_movie.post(url_for('employees.movies.add_movie'), 
                                        data={'m_id': str(movie_a['tmdb_id'])}, 
                                        follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/movies/all-movies'

    with client_movie.application.app_context():
        movie = Movie.query
        movie_total, movie = movie.count(), movie.first()
        movie_total == 1
        assert movie.id == 1
        assert movie.tmdb_id == movie_a['tmdb_id']
        assert movie.overview

        change = Change.query
        change_total, change = change.count(), change.first()
        change_total == 1
        assert change.employee_id == current_id
        assert change.action == 'fetched new data'
        assert change.table_name == 'movie'
        assert change.data_id == movie.id

        genres = Genre.query.count()
        assert genres != 0

    # Test employee's change displayed in home page
    response = client_movie.get(url_for('employees.home'))
    assert response.status_code == 200
    assert b'Movie</td>' in response.data
    assert b'fetched new data</td>' in response.data
    assert f"{movie_a['title']}</td>".encode('utf-8') in response.data


@pytest.mark.skip
def test_delete_movie(client_movie):
    ''' Test delete movie successfully. Deleted Movie should not be displayed in inactive and active. (All-movies and coming-soon tested elsewhere.)'''
    login_employee(client_movie)
    current_id =  current_user.id

    # Test delete movie feature
    response = client_movie.post(url_for('employees.movies.delete_movie', 
                                        movie_id = 1, 
                                        follow_redirects=True))
    assert response.status_code == 302
    assert '/employee/movies/all-movies' in response.headers['Location']
    
    with client_movie.application.app_context():
        movie = Movie.query.first()
        assert movie.id == 1
        assert movie.tmdb_id == movie_a['tmdb_id']
        assert movie.deleted

        change = Change.query
        change_total, change = change.count(), change.first()
        change_total == 1
        assert change.employee_id == current_id
        assert change.action == 'deleted'
        assert change.table_name == 'movie'
        assert change.data_id == movie.id

    # Test employee's change displayed in home page
    response = client_movie.get(url_for('employees.home'))
    assert response.status_code == 200
    assert b'Movie</td>' in response.data
    assert b'deleted</td>' in response.data
    assert f"{movie_a['title']}</td>".encode('utf-8') in response.data

    # Should not display deleted movie in active-movies and inactive-movies pages
    route = movie_a['route']
    response = client_movie.get(url_for('employees.movies.active'))
    assert response.status_code == 200
    assert f'href="/employee/movies/{route}"'.encode('utf-8') not in response.data # movie card
    assert f"{movie_a['title']}</option>".encode('utf-8') not in response.data # inactivate movie select option

    response = client_movie.get(url_for('employees.movies.inactive'))
    assert response.status_code == 200

    assert f'href="/employee/movies/{route}"'.encode('utf-8') not in response.data # movie card
    assert f"{movie_a['title']}</option>".encode('utf-8') not in response.data # activate movie select option


@pytest.mark.skip
def test_add_deleted_movie(client_users):
    ''' Test adding a movie that was deleted. 
    This should also fetch new data and update movie. '''
    login_employee(client_users)
    current_id =  current_user.id

    # Deleted Movie
    with client_users.application.app_context():
        movie = Movie(
            tmdb_id = movie_a['tmdb_id'],
            title = movie_a['title'],
            route = movie_a['route'],
            deleted = True
        )

        db.session.add(movie)
        db.session.commit()

    # Test add movie feature
    response = client_users.post(url_for('employees.movies.add_movie'), 
                                        data={'m_id': movie_a['tmdb_id']}, 
                                        follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/movies/all-movies'

    with client_users.application.app_context():
        movie = Movie.query
        movie_total, movie = movie.count(), movie.first()
        movie_total == 1
        assert movie.id == 1
        assert movie.tmdb_id == movie_a['tmdb_id']
        assert movie.deleted == False
        assert movie.tagline is not None 

        change = Change.query
        change_total, change = change.count(), change.first()
        change_total == 1
        assert change.employee_id == current_id
        assert change.action == 'added'
        assert change.table_name == 'movie'
        assert change.data_id == movie.id

        genres = Genre.query.count()
        assert genres != 0


@pytest.mark.skip   
def test_search_add_movie_failure(client_users):
    ''' Test searching/adding movie with invalid data '''
    login_employee(client_users)
    
    # Test searching for movie with incorrect data
    response = client_users.post(url_for('employees.movies.add_movie'), 
                                    data={'title': movie_a['title'] + ' Incorrect'}, 
                                    follow_redirects=True)
    assert response.status_code == 200
    assert b'No results' in response.data

    # Test adding movie with incorrect m_id
    response = client_users.post(url_for('employees.movies.add_movie'), 
                                        data={'m_id':'incorrect'})
    assert response.status_code == 200
    assert b'Add Movie' in response.data
    assert b'Cannot add movie at this time.' in response.data

    with client_users.application.app_context():
        movie = Movie.query.first()
        assert not movie
        change = Change.query.first()
        assert not change

    # Test employee home page
    response = client_users.get(url_for('employees.home'))
    assert b'Movie</td>' not in response.data
    assert b'added</td>' not in response.data
    assert f"{movie_a['title']}</td>".encode('utf-8') not in response.data

    # Test movie is not displayed in all-movies page
    response = client_users.get(url_for('employees.movies.all_movies'))
    route = movie_a['route']
    assert f'href="/employee/movies/{route}"'.encode('utf-8') not in response.data


@pytest.mark.skip 
def test_delete_movie_failure(client_users):
    ''' Test delete movie given invalid data '''   
    login_employee(client_users)

    response = client_users.post(url_for('employees.movies.delete_movie', movie_id = 1, 
                                follow_redirects=True))
    assert response.status_code == 404

    
# TODO: Test deleting a movie that can't be deleted (has showtimes)
@pytest.mark.skip
def test_delete_movie_showtimes_failure(client_users):
    ''' Test delete movie with showtimes '''
    login_employee(client_users)
    pass




''' ACTIVATE AND INACTIVATE MOVIE'''
@pytest.mark.skip
def test_display_active(client_movie):
    ''' Display active movie. Coming-soon tested elsewhere. '''
    login_employee(client_movie)

    response = client_movie.get(url_for('employees.movies.active'))
    assert response.status_code == 200
    assert b'There are no movies.' in response.data
    
    with client_movie.application.app_context():
        movie = Movie.query.first()
        movie.active = True
        db.session.commit()

    response = client_movie.get(url_for('employees.movies.active'))
    assert response.status_code == 200
    route = movie_a['route']
    assert f'href="/employee/movies/{route}"'.encode('utf-8') in response.data # movie card
    assert f"{movie_a['title']}</option>".encode('utf-8') in response.data # inactivate movie select option
    
    response = client_movie.get(url_for('employees.movies.inactive'))
    assert response.status_code == 200
    assert f'href="/employee/movies/{route}"'.encode('utf-8') not in response.data
    assert f"{movie_a['title']}</option>".encode('utf-8') not in response.data # activate movie select option

    # Displayed in all-movies
    response = client_movie.get(url_for('employees.movies.all_movies'))
    assert response.status_code == 200
    assert f'href="/employee/movies/{route}"'.encode('utf-8') in response.data


@pytest.mark.skip
def test_display_inactive(client_movie):
    ''' Display inactive movie. Coming-soon tested elsewhere. '''
    login_employee(client_movie)

    with client_movie.application.app_context():
        movie = Movie.query.first()
        movie.active = True
        db.session.commit()

    response = client_movie.get(url_for('employees.movies.inactive'))
    assert response.status_code == 200
    assert b'There are no movies.' in response.data

    with client_movie.application.app_context():
        movie = Movie.query.first()
        movie.active = False
        db.session.commit()

    response = client_movie.get(url_for('employees.movies.inactive'))
    assert response.status_code == 200
    route = movie_a['route']
    assert f'href="/employee/movies/{route}"'.encode('utf-8') in response.data # movie card
    assert f"{movie_a['title']}</option>".encode('utf-8') in response.data # activate movie select option

    response = client_movie.get(url_for('employees.movies.active'))
    assert response.status_code == 200
    assert f'href="/employee/movies/{route}"'.encode('utf-8') not in response.data
    assert f"{movie_a['title']}</option>".encode('utf-8') not in response.data # inactivate movie select option

    # Displayed in all-movies
    response = client_movie.get(url_for('employees.movies.all_movies'))
    assert response.status_code == 200
    assert f'href="/employee/movies/{route}"'.encode('utf-8') in response.data


@pytest.mark.skip
@pytest.mark.parametrize('poster_path_param, backdrop_path_param, trailer_path_param, release_date_param, runtime_param', 
    [(None, movie_a['backdrop_path'], movie_a['trailer_path'], movie_a['release_date'], movie_a['runtime']),
     ('', movie_a['backdrop_path'], movie_a['trailer_path'], movie_a['release_date'], movie_a['runtime']), 
     (movie_a['poster_path'], None, movie_a['trailer_path'], movie_a['release_date'], movie_a['runtime']), 
     (movie_a['poster_path'], '', movie_a['trailer_path'], movie_a['release_date'], movie_a['runtime']), 
     (movie_a['poster_path'], movie_a['backdrop_path'], None, movie_a['release_date'], movie_a['runtime']), 
     (movie_a['poster_path'], movie_a['backdrop_path'], '', movie_a['release_date'], movie_a['runtime']), 
     (movie_a['poster_path'], movie_a['backdrop_path'], movie_a['trailer_path'], None, movie_a['runtime']),
     (movie_a['poster_path'], movie_a['backdrop_path'], movie_a['trailer_path'], movie_a['release_date'], None),
     (movie_a['poster_path'], movie_a['backdrop_path'], movie_a['trailer_path'], movie_a['release_date'], 0)
    ])
def test_display_inactive_2(client_users, poster_path_param, backdrop_path_param, trailer_path_param, release_date_param, runtime_param):
    ''' Inactive movies with missing data should not be displayed as options to activate. '''
    login_employee(client_users)

    with client_users.application.app_context():
        movie = Movie(
            tmdb_id = movie_a['tmdb_id'],
            title = movie_a['title'],
            route = movie_a['route'],
            status = movie_a['status'],
            release_date = release_date_param,
            runtime = runtime_param,
            rating = movie_a['rating'],
            poster_path = poster_path_param,
            backdrop_path = backdrop_path_param,
            trailer_path = trailer_path_param,
            overview = movie_a['overview'],
        )
        db.session.add(movie)
        db.session.commit()

    response = client_users.get(url_for('employees.movies.inactive'))
    assert response.status_code == 200
    route = movie_a['route']
    assert f'href="/employee/movies/{route}"'.encode('utf-8') in response.data # movie card
    assert f"{movie_a['title']}</option>".encode('utf-8') not in response.data # activate movie select option


@pytest.mark.skip
def test_activate_movie(client_movie):
    ''' Test activate movie sucessfully '''
    login_employee(client_movie)
    current_id =  current_user.id

    response = client_movie.post(url_for('employees.movies.inactive'),
                                    data={'m_id':'1'}, 
                                    follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/movies/active'
    
    with client_movie.application.app_context():
        movie = Movie.query.first()
        assert movie.active
        assert movie.poster_path
        assert movie.poster_path is not ''
        assert movie.backdrop_path
        assert movie.backdrop_path is not ''
        assert movie.trailer_path
        assert movie.trailer_path is not ''
        assert movie.runtime
        assert movie.runtime is not 0
    
        change = Change.query.first()
        assert change.employee_id == current_id
        assert change.action == 'activated'
        assert change.table_name == 'movie'
        assert change.data_id == movie.id
    

@pytest.mark.skip
def test_inactivate_movie(client_movie):
    ''' Test inactivate movie sucessfully '''
    login_employee(client_movie)
    current_id =  current_user.id

    with client_movie.application.app_context():
        movie = Movie.query.first()
        movie.active = True
        db.session.commit()

    response = client_movie.post(url_for('employees.movies.active'),
                                    data={'m_id':'1'}, 
                                    follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/movies/inactive'
    
    with client_movie.application.app_context():
        movie = Movie.query.first()
        assert not movie.active
    
        change = Change.query.first()
        assert change.employee_id == current_id
        assert change.action == 'inactivated'
        assert change.table_name == 'movie'
        assert change.data_id == movie.id


@pytest.mark.skip
def test_activate_movie_failure(client_users):
    ''' Test activate movie with invalid data. (Movie is not listed in inactivated movies to activate) '''
    login_employee(client_users)

    response = client_users.post(url_for('employees.movies.active'),
                                    data={'m_id': 1}, 
                                    follow_redirects=True)
    # Nothing happens
    assert response.status_code == 200
    assert response.request.path == '/employee/movies/active' 

    
@pytest.mark.skip
def test_inactivate_movie_failure(client_users):
    ''' Test inactivate movie with invalid data. (Movie is not listed in activated movies to inactivate) '''
    login_employee(client_users)

    response = client_users.post(url_for('employees.movies.inactive'),
                                    data={'m_id': 1}, 
                                    follow_redirects=True)
    # Nothing happens
    assert response.status_code == 200
    assert response.request.path == '/employee/movies/inactive'




''' DISPLAY MOVIES AND MOVIE INFO PAGE'''
@pytest.mark.skip
def test_display_movies(client_users):
    '''  Movies are correctly displayed in all-movies and coming-soon '''
    login_employee(client_users)

    response = client_users.get(url_for('employees.movies.all_movies'))
    assert response.status_code == 200
    assert b'There are no movies.' in response.data
    response = client_users.get(url_for('employees.movies.coming_soon'))
    assert response.status_code == 200
    assert b'There are no movies.' in response.data

    with client_users.application.app_context():
        movie = Movie (
            tmdb_id = movie_a['tmdb_id'],
            title = movie_a['title'],
            route = movie_a['route'],
            status = movie_a['status'],
            release_date = movie_a['release_date'],
            overview = movie_a['overview'],
            runtime = movie_a['runtime'],
            rating = movie_a['rating'],
            poster_path = movie_a['poster_path'],
            backdrop_path = movie_a['backdrop_path'],
            trailer_path = movie_a['trailer_path'],
            active = True)
        db.session.add(movie)

        coming_soon = Movie (
            tmdb_id = 4935, # Howl's Moving Castle's tmdb id
            title = 'Not Released',
            route = 'not-released',
            release_date = datetime.now() + timedelta(days=1))
        db.session.add(coming_soon)

        deleted = Movie (
            tmdb_id = 12429, # Ponyo's tmdb id
            title = 'Deleted',
            route = 'deleted',
            release_date = datetime.now(),
            deleted = True)
        db.session.add(deleted)
        db.session.commit()

    route = movie_a['route']
    response = client_users.get(url_for('employees.movies.all_movies'))
    # Test movie cards
    assert f'href="/employee/movies/{route}'.encode() in response.data
    assert b'href="/employee/movies/not-released"' in response.data 
    assert b'href="/employee/movies/deleted"' not in response.data 

    response = client_users.get(url_for('employees.movies.coming_soon'))
    # Test movie cards
    assert f'href="/employee/movies/{route}"'.encode() not in response.data
    assert b'href="/employee/movies/not-released"' in response.data 
    assert b'href="/employee/movies/deleted"' not in response.data 


@pytest.mark.skip
def test_display_movie(client_movie):
    ''' Display movie info page '''
    login_employee(client_movie)
    m_genre = 'Fantasy'

    with client_movie.application.app_context():
        movie = Movie.query.first()
        movie.active = True
        db.session.commit()

        genre = Genre (name = m_genre)
        db.session.add(genre)
        db.session.commit()

        db.session.execute(
            genres.insert().values(movie_id=movie.id, genre_id=genre.id)
        )
        db.session.commit()

    response = client_movie.get(url_for('employees.movies.movie', movie_route=movie_a['route']))
    assert response.status_code == 200

    assert movie_a['title'].encode('UTF-8') in response.data
    assert movie_a['rating'].encode() in response.data
    assert movie_a['release_date'].strftime("%b %d, %Y").encode() in response.data
    assert m_genre.encode() in response.data
    assert movie_a['poster_path'].encode() in response.data
    assert movie_a['backdrop_path'].encode() in response.data
    assert movie_a['trailer_path'].encode() in response.data
    assert movie_a['overview'].encode() in response.data
    assert b'Update</a></li>' in response.data
    assert b'Showtimes</a></li>' in response.data
    assert b'Delete</button></li>' in response.data
    



''' UPDATE MOVIE '''
@pytest.mark.skip
def test_update_movie(client_movie):
    ''' Test update poster, backdrop, and trailer path '''
    login_employee(client_movie)
    current_id =  current_user.id

    with client_movie.application.app_context():
        movie = Movie.query.first()
        movie.poster_path = None
        movie.backdrop_path = None
        movie.trailer_path = None
        db.session.commit()

    response = client_movie.get(url_for('employees.movies.update_movie', movie_route=movie_a['route']))
    assert response.status_code == 200

    # Poster, backdrop, and trailer
    data = dict(
        poster = movie_a['poster_path'],
        backdrop = movie_a['backdrop_path'],
        trailer = movie_a['trailer_path']
    )

    response = client_movie.post(url_for('employees.movies.update_movie', movie_route=movie_a['route']), data=data, follow_redirects=True)
    assert response.status_code == 200

    with client_movie.application.app_context():
        movie = Movie.query.first()
        assert movie.poster_path 
        assert movie.backdrop_path
        assert movie.trailer_path

        change = Change.query.first()
        assert change.employee_id == current_id
        assert change.action == 'updated'
        assert change.table_name == 'movie'
        assert change.data_id == movie.id


@pytest.mark.skip
def test_update_movie_poster(client_movie):
    ''' Test update poster only '''
    login_employee(client_movie)
    current_id =  current_user.id

    with client_movie.application.app_context():
        movie = Movie.query.first()
        movie.poster_path = None
        movie.backdrop_path = None
        movie.trailer_path = None
        db.session.commit()

    response = client_movie.post(url_for('employees.movies.update_movie', movie_route=movie_a['route']), data={'poster':movie_a['poster_path']}, follow_redirects=True)
    assert response.status_code == 200

    with client_movie.application.app_context():
        movie = Movie.query.first()
        assert movie.poster_path
        assert not movie.backdrop_path
        assert not movie.trailer_path

        change = Change.query.first()
        assert change.employee_id == current_id
        assert change.action == 'updated'
        assert change.table_name == 'movie'
        assert change.data_id == movie.id


@pytest.mark.skip
def test_update_movie_failure(client_movie):
    ''' Test update poster, backdrop, and trailer path with invalid data '''
    login_employee(client_movie)

    with client_movie.application.app_context():
        movie = Movie.query.first()
        movie.poster_path = None
        movie.backdrop_path = None
        movie.trailer_path = None
        db.session.commit()

    response = client_movie.get(url_for('employees.movies.update_movie', movie_route=movie_a['route']))
    assert response.status_code == 200

    # Poster, backdrop, and trailer
    data = dict(
        poster = None,
        backdrop = None,
        trailer = None
    )

    response = client_movie.post(url_for('employees.movies.update_movie', movie_route=movie_a['route']), data=data, follow_redirects=True)
    assert response.status_code == 200

    with client_movie.application.app_context():
        movie = Movie.query.first()
        assert not movie.poster_path
        assert not movie.backdrop_path
        assert not movie.trailer_path

        Change.query.count() == 0

