from theatert import create_app, db
from theatert.users.utils import populate_db
from theatert import bcrypt, db
from theatert.models import Employee, Member, Movie
from theatert.config_test import movie_a, movie_b

import os
import pytest


class TestingConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture()
def app():
    app = create_app(TestingConfig) 

    # Add models to database
    with app.app_context():
        db.create_all()
        populate_db()

        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def client_users(client):
    ''' Employee user in database. '''
    # NOTE: Phone number was taken from import phonenumbers' documentation

    with client.application.app_context():
        employee = Employee (
            username = 'testuser',
            password = bcrypt.generate_password_hash('Valid*123').decode('utf-8')
        )
        member = Member (
            username = 'test@user.com',
            password = bcrypt.generate_password_hash('valid*123').decode('utf-8'),
            email = 'test@user.com',
            fname = 'Test',
            lname = 'User',
            phone = '5107488230',
            zip_code = '12345'
        )
        
        db.session.add(employee)
        db.session.add(member)

        db.session.commit()

        yield client

        db.session.delete(employee)
        db.session.delete(member)
        db.session.commit


@pytest.fixture()
def client_movie(client_users):
    with client_users.application.app_context():
        movie = Movie(
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
            trailer_path = movie_a['trailer_path']
        )

        db.session.add(movie)
        db.session.commit()

        yield client_users

        db.session.delete(movie)
        db.session.commit


@pytest.fixture()
def client_movies(client_users):
    with client_users.application.app_context():
        now_playing = Movie(
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
            active = True
        )
        db.session.add(now_playing)
        
        coming_soon = Movie(
            tmdb_id = movie_b['tmdb_id'],
            title = movie_b['title'],
            route = movie_b['route'],
            status = movie_b['status'],
            release_date = movie_b['release_date'],
            overview = movie_b['overview'],
            runtime = movie_b['runtime'],
            rating = movie_b['rating'],
            poster_path = movie_b['poster_path'],
            backdrop_path = movie_b['backdrop_path'],
            trailer_path = movie_b['trailer_path'],
            active = True
        )
        db.session.add(coming_soon)
        db.session.commit()

        yield client_users

        db.session.delete(now_playing)
        db.session.delete(coming_soon)
        db.session.commit

