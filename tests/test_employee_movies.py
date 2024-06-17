''' Test movie management '''

from datetime import datetime, timedelta
from flask import url_for
from flask_login import current_user
from tests.utils import login_employee
from theatert import db
from theatert.models import Movie, Change, Genre, genres

import pytest
import os


if os.environ.get('SKIP_TEST_EMPLOYEE_MOVIES', 'false').lower() == 'true':
    pytestmark = pytest.mark.skip("Skipping tests in test_employee_movies.py")


''' SEARCH, ADD, DELETE AND FETCH MOVIE '''
#@pytest.mark.skip
def test_search_movie(client_employee):
    ''' Test search movie successfully'''
    login_employee(client_employee)

    # Test that page loads correctly
    response = client_employee.get(url_for('employees.movies.add_movie'))
    assert response.status_code == 200

    # Test searching for movie with title only
    response = client_employee.post(url_for('employees.movies.add_movie'), 
                                    data={'title':'Spirited Away'}, 
                                    follow_redirects=True)
    assert response.status_code == 200
    assert b'Add Movie' in response.data
    
    # Test searching for movie with title and releasae year
    response = client_employee.post(url_for('employees.movies.add_movie'), 
                                    data={'title':'Spirited Away', 
                                          'release_year' : 2001}, 
                                    follow_redirects=True)
    assert response.status_code == 200
    assert b'Add Movie' in response.data


#@pytest.mark.skip
def test_add_movie(client_employee):
    ''' Test add movie successfully'''
    login_employee(client_employee)
    current_id =  current_user.id

    # Test add movie feature
    response = client_employee.post(url_for('employees.movies.add_movie'), 
                                        data={'m_id':'129'}, 
                                        follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/movies/all-movies'

    with client_employee.application.app_context():
        movie = Movie.query
        movie_total, movie = movie.count(), movie.first()
        movie_total == 1
        assert movie.id == 1
        assert movie.tmdb_id == 129

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
    response = client_employee.get(url_for('employees.home'))
    assert b'Movie</td>' in response.data
    assert b'added</td>' in response.data
    assert b"Spirited Away</td>" in response.data


#@pytest.mark.skip
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
                                        data={'m_id':'129'}, 
                                        follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/movies/all-movies'

    with client_movie.application.app_context():
        movie = Movie.query
        movie_total, movie = movie.count(), movie.first()
        movie_total == 1
        assert movie.id == 1
        assert movie.tmdb_id == 129
        assert movie.overview is not None

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
    assert b"Spirited Away</td>" in response.data


#@pytest.mark.skip
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
        assert movie.tmdb_id == 129
        assert movie.deleted is True

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
    assert b"Spirited Away</td>" in response.data

    # Should not display deleted movie in active-movies and inactive-movies pages
    response = client_movie.get(url_for('employees.movies.active'))
    assert response.status_code == 200
    assert b'href="/employee/movies/spirited-away"' not in response.data # movie card
    assert b'Spirited Away</option>' not in response.data # inactivate movie select option

    response = client_movie.get(url_for('employees.movies.inactive'))
    assert response.status_code == 200
    assert b'href="/employee/movies/spirited-away"' not in response.data # movie card
    assert b'Spirited Away</option>' not in response.data # activate movie select option


#@pytest.mark.skip
def test_add_deleted_movie(client_employee):
    ''' Test adding a movie that was deleted. 
    This should also fetch new data and update movie. '''
    login_employee(client_employee)
    current_id =  current_user.id

    # Deleted Movie
    with client_employee.application.app_context():
        movie = Movie(
            tmdb_id = 129,
            title = 'Spirited Away',
            route = 'spirited-away',
            deleted = True
        )

        db.session.add(movie)
        db.session.commit()

    # Test add movie feature
    response = client_employee.post(url_for('employees.movies.add_movie'), 
                                        data={'m_id':'129'}, 
                                        follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/movies/all-movies'

    with client_employee.application.app_context():
        movie = Movie.query
        movie_total, movie = movie.count(), movie.first()
        movie_total == 1
        assert movie.id == 1
        assert movie.tmdb_id == 129
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


#@pytest.mark.skip   
def test_search_add_movie_failure(client_employee):
    ''' Test searching/adding movie with invalid data '''
    login_employee(client_employee)
    
    # Test searching for movie with incorrect data
    response = client_employee.post(url_for('employees.movies.add_movie'), 
                                    data={'title':'Spirited Away Incorrect'}, 
                                    follow_redirects=True)
    assert response.status_code == 200
    assert b'No results' in response.data

    # Test adding movie with incorrect m_id
    response = client_employee.post(url_for('employees.movies.add_movie'), 
                                        data={'m_id':'incorrect'})
    assert response.status_code == 200
    assert b'Add Movie' in response.data
    assert b'Cannot add movie at this time.' in response.data

    with client_employee.application.app_context():
        movie = Movie.query.first()
        assert movie is None
        change = Change.query.first()
        assert change is None

    # Test employee home page
    response = client_employee.get(url_for('employees.home'))
    assert b'Movie</td>' not in response.data
    assert b'added</td>' not in response.data
    assert b"Spirited Away</td>" not in response.data

    # Test movie is not displayed in all-movies page
    response = client_employee.get(url_for('employees.movies.all_movies'))
    assert b'href="/employee/movies/spirited-away"' not in response.data


#@pytest.mark.skip 
def test_delete_movie_failure(client_employee):
    ''' Test delete movie given invalid data '''   
    login_employee(client_employee)

    response = client_employee.post(url_for('employees.movies.delete_movie', movie_id = 1, 
                                follow_redirects=True))
    assert response.status_code == 404

    
# TODO: Test deleting a movie that can't be deleted (has showtimes)
#@pytest.mark.skip
def test_delete_movie_showtimes_failure(client_employee):
    ''' Test delete movie with showtimes '''
    login_employee(client_employee)
    pass




''' ACTIVATE AND INACTIVATE MOVIE'''
#@pytest.mark.skip
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
    assert b'href="/employee/movies/spirited-away"' in response.data # movie card
    assert b'Spirited Away</option>' in response.data # inactivate movie select option
    
    response = client_movie.get(url_for('employees.movies.inactive'))
    assert response.status_code == 200
    assert b'href="/employee/movies/spirited-away"' not in response.data
    assert b'Spirited Away</option>' not in response.data # activate movie select option

    # Displayed in all-movies
    response = client_movie.get(url_for('employees.movies.all_movies'))
    assert response.status_code == 200
    assert b'href="/employee/movies/spirited-away"' in response.data


#@pytest.mark.skip
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
    assert b'href="/employee/movies/spirited-away"' in response.data # movie card
    assert b'Spirited Away</option>' in response.data # activate movie select option

    response = client_movie.get(url_for('employees.movies.active'))
    assert response.status_code == 200
    assert b'href="/employee/movies/spirited-away"' not in response.data
    assert b'Spirited Away</option>' not in response.data # inactivate movie select option

    # Displayed in all-movies
    response = client_movie.get(url_for('employees.movies.all_movies'))
    assert response.status_code == 200
    assert b'href="/employee/movies/spirited-away"' in response.data


#@pytest.mark.skip
@pytest.mark.parametrize('poster_path, backdrop_path, trailer_path, release_date', 
    [(None, '/ogRfsqklWMRpzmq4ZJcI0MvqzlN.jpg', 'GAp2_0JJskk', datetime.strptime("2001-07-20", "%Y-%m-%d").date()),
     ('/u1gGwSHTqTJ4hyclrC8owtJO66Y.jpg', None, 'GAp2_0JJskk', datetime.strptime("2001-07-20", "%Y-%m-%d").date()), 
     ('/u1gGwSHTqTJ4hyclrC8owtJO66Y.jpg', '/ogRfsqklWMRpzmq4ZJcI0MvqzlN.jpg', None, datetime.strptime("2001-07-20", "%Y-%m-%d").date()), 
     ('/u1gGwSHTqTJ4hyclrC8owtJO66Y.jpg', '/ogRfsqklWMRpzmq4ZJcI0MvqzlN.jpg', 'GAp2_0JJskk', None)])
def test_display_inactive_2(client_employee, poster_path, backdrop_path, trailer_path, release_date):
    ''' Inactive movies with missing data should not be displayed as options to activate. '''
    login_employee(client_employee)

    with client_employee.application.app_context():
        movie = Movie(
            tmdb_id = 129,
            title = 'Spirited Away',
            route = 'spirited-away',
            status = 'Released',
            release_date = release_date,
            overview = 'A young girl, Chihiro, becomes trapped in a strange new world of spirits. When her parents undergo a mysterious transformation, she must call upon the courage she never knew she had to free her family.',
            runtime = 125,
            rating = 'PG',
            poster_path = poster_path,
            backdrop_path = backdrop_path,
            trailer_path = trailer_path
        )
        db.session.add(movie)
        db.session.commit()

    response = client_employee.get(url_for('employees.movies.inactive'))
    assert response.status_code == 200
    assert b'href="/employee/movies/spirited-away"' in response.data # movie card
    assert b'Spirited Away</option>' not in response.data # activate movie select option


#@pytest.mark.skip
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
        assert movie.active is True
    
        change = Change.query.first()
        assert change.employee_id == current_id
        assert change.action == 'activated'
        assert change.table_name == 'movie'
        assert change.data_id == movie.id
    

#@pytest.mark.skip
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
        assert movie.active is False
    
        change = Change.query.first()
        assert change.employee_id == current_id
        assert change.action == 'inactivated'
        assert change.table_name == 'movie'
        assert change.data_id == movie.id


#@pytest.mark.skip
def test_activate_movie_failure(client_employee):
    ''' Test activate movie with invalid data '''
    login_employee(client_employee)

    response = client_employee.post(url_for('employees.movies.active'),
                                    data={'m_id': 1}, 
                                    follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/movies/active'

    
#@pytest.mark.skip
def test_inactivate_movie_failure(client_employee):
    ''' Test inactivate movie with invalid data '''
    login_employee(client_employee)

    response = client_employee.post(url_for('employees.movies.inactive'),
                                    data={'m_id': 1}, 
                                    follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/movies/inactive'




''' DISPLAY MOVIES AND MOVIE INFO PAGE'''
#@pytest.mark.skip
def test_display_movies(client_employee):
    '''  Movies are correctly displayed in all-movies and coming-soon '''
    login_employee(client_employee)

    response = client_employee.get(url_for('employees.movies.all_movies'))
    assert response.status_code == 200
    assert b'There are no movies.' in response.data
    response = client_employee.get(url_for('employees.movies.coming_soon'))
    assert response.status_code == 200
    assert b'There are no movies.' in response.data

    with client_employee.application.app_context():
        movie = Movie (
            tmdb_id = 129,
            title = 'Spirited Away',
            route = 'spirited-away',
            status = 'Released',
            release_date = datetime.strptime('2001-07-20', '%Y-%m-%d').date(),
            overview = 'A young girl, Chihiro, becomes trapped in a strange new world of spirits. \
                When her parents undergo a mysterious transformation, she must call upon the courage \
                she never knew she had to free her family.',
            runtime = 125,
            rating = 'PG',
            poster_path = '/u1gGwSHTqTJ4hyclrC8owtJO66Y.jpg',
            backdrop_path = '/ogRfsqklWMRpzmq4ZJcI0MvqzlN.jpg',
            trailer_path = 'GAp2_0JJskk',
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

    response = client_employee.get(url_for('employees.movies.all_movies'))

    # Test movie cards
    assert b'href="/employee/movies/spirited-away"' in response.data
    assert b'href="/employee/movies/not-released"' in response.data 
    assert b'href="/employee/movies/deleted"' not in response.data 

    response = client_employee.get(url_for('employees.movies.coming_soon'))
    # Test movie cards
    assert b'href="/employee/movies/spirited-away"' not in response.data
    assert b'href="/employee/movies/not-released"' in response.data 
    assert b'href="/employee/movies/deleted"' not in response.data 


#@pytest.mark.skip
def test_display_movie(client_movie):
    ''' Display movie info page '''
    login_employee(client_movie)

    with client_movie.application.app_context():
        movie = Movie.query.first()
        movie.active = True
        db.session.commit()

        genre = Genre (name = 'Fantasy')
        db.session.add(genre)
        db.session.commit()

        db.session.execute(
            genres.insert().values(movie_id=movie.id, genre_id=genre.id)
        )
        db.session.commit()

    response = client_movie.get(url_for('employees.movies.movie', movie_route='spirited-away'))
    assert response.status_code == 200

    assert b'Spirited Away' in response.data
    assert b'PG' in response.data
    assert b'Jul 20, 2001' in response.data
    assert b'Fantasy' in response.data
    assert b'/u1gGwSHTqTJ4hyclrC8owtJO66Y.jpg' in response.data
    assert b'/ogRfsqklWMRpzmq4ZJcI0MvqzlN.jpg' in response.data
    assert b'GAp2_0JJskk' in response.data
    assert b'A young girl, Chihiro, becomes trapped in a strange new world of spirits.' in response.data
    assert b'Update</a></li>' in response.data
    assert b'Showtimes</a></li>' in response.data
    assert b'Delete</button></li>' in response.data
    



''' UPDATE MOVIE '''
#@pytest.mark.skip
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

    response = client_movie.get(url_for('employees.movies.update_movie', movie_route='spirited-away'))
    assert response.status_code == 200

    # Poster, backdrop, and trailer
    data = dict(
        poster='/u1gGwSHTqTJ4hyclrC8owtJO66Y.jpg',
        backdrop='/gZ5ouTdBxLPCDezpG7MxdEezCF3.jpg',
        trailer='GAp2_0JJskk'
    )

    response = client_movie.post(url_for('employees.movies.update_movie', movie_route='spirited-away'), data=data, follow_redirects=True)
    assert response.status_code == 200

    with client_movie.application.app_context():
        movie = Movie.query.first()
        assert movie.poster_path is not None
        assert movie.backdrop_path is not  None
        assert movie.trailer_path is not None

        change = Change.query.first()
        assert change.employee_id == current_id
        assert change.action == 'updated'
        assert change.table_name == 'movie'
        assert change.data_id == movie.id


#@pytest.mark.skip
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

    response = client_movie.post(url_for('employees.movies.update_movie', movie_route='spirited-away'), data={'poster':'/u1gGwSHTqTJ4hyclrC8owtJO66Y.jpg'}, follow_redirects=True)
    assert response.status_code == 200

    with client_movie.application.app_context():
        movie = Movie.query.first()
        assert movie.poster_path is not None
        assert movie.backdrop_path is None
        assert movie.trailer_path is None

        change = Change.query.first()
        assert change.employee_id == current_id
        assert change.action == 'updated'
        assert change.table_name == 'movie'
        assert change.data_id == movie.id


#@pytest.mark.skip
def test_update_movie_failure(client_movie):
    ''' Test update poster, backdrop, and trailer path with invalid data '''
    login_employee(client_movie)

    with client_movie.application.app_context():
        movie = Movie.query.first()
        movie.poster_path = None
        movie.backdrop_path = None
        movie.trailer_path = None
        db.session.commit()

    response = client_movie.get(url_for('employees.movies.update_movie', movie_route='spirited-away'))
    assert response.status_code == 200

    # Poster, backdrop, and trailer
    data = dict(
        poster = None,
        backdrop = None,
        trailer = None
    )

    response = client_movie.post(url_for('employees.movies.update_movie', movie_route='spirited-away'), data=data, follow_redirects=True)
    assert response.status_code == 200

    with client_movie.application.app_context():
        movie = Movie.query.first()
        assert movie.poster_path is None
        assert movie.backdrop_path is  None
        assert movie.trailer_path is None

        Change.query.count() == 0

