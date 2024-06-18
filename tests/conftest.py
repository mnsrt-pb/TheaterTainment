from datetime import datetime, timedelta
from flask import url_for
from theatert import create_app, db
from theatert.users.utils import populate_db

from theatert import bcrypt, db
from theatert.models import Employee, Member, Movie

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
def client_employee(client):
    ''' Employee user in database. '''

    with client.application.app_context():
        user = Employee (
            username = 'testuser',
            password = bcrypt.generate_password_hash('Valid*123').decode('utf-8')
        )
        db.session.add(user)
        db.session.commit()

        yield client

        db.session.delete(user)
        db.session.commit


@pytest.fixture()
def client_both(client_employee):
    ''' Member user in database. '''
    # NOTE: Phone number was taken from import phonenumbers' documentation

    with client_employee.application.app_context():
        user = Member (
            username = 'test@user.com',
            password = bcrypt.generate_password_hash('valid*123').decode('utf-8'),
            email = 'test@user.com',
            fname = 'Test',
            lname = 'User',
            phone = '5107488230',
            zip_code = '12345'
        )
        db.session.add(user)
        db.session.commit()


        yield client_employee

        db.session.delete(user)
        db.session.commit


@pytest.fixture()
def client_movie(client_employee):
    with client_employee.application.app_context():
        movie = Movie(
            tmdb_id = 129,
            title = 'Spirited Away',
            route = 'spirited-away',
            status = 'Released',
            release_date = datetime.strptime('2001-07-20', '%Y-%m-%d').date(),
            overview = 'A young girl, Chihiro, becomes trapped in a strange new world of spirits. When her parents undergo a mysterious transformation, she must call upon the courage she never knew she had to free her family.',
            runtime = 125,
            rating = 'PG',
            poster_path = '/u1gGwSHTqTJ4hyclrC8owtJO66Y.jpg',
            backdrop_path = '/ogRfsqklWMRpzmq4ZJcI0MvqzlN.jpg',
            trailer_path = 'GAp2_0JJskk'
        )

        db.session.add(movie)
        db.session.commit()

        yield client_employee

        db.session.delete(movie)
        db.session.commit


@pytest.fixture()
def client_movies(client_both):
    with client_both.application.app_context():
        now_playing = Movie(
            tmdb_id = 129,
            title = 'Spirited Away',
            route = 'spirited-away',
            status = 'Released',
            release_date = datetime.strptime('2001-07-20', '%Y-%m-%d').date(),
            overview = 'A young girl, Chihiro, becomes trapped in a strange new world of spirits. When her parents undergo a mysterious transformation, she must call upon the courage she never knew she had to free her family.',
            runtime = 125,
            rating = 'PG',
            poster_path = '/u1gGwSHTqTJ4hyclrC8owtJO66Y.jpg',
            backdrop_path = '/ogRfsqklWMRpzmq4ZJcI0MvqzlN.jpg',
            trailer_path = 'GAp2_0JJskk',
            active = True
        )
        db.session.add(now_playing)

        day_after_tomorrow = datetime.now() + timedelta(days=2)
        day_after_tomorrow = day_after_tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        coming_soon = Movie(
            tmdb_id = 128,
            title = 'Princess Mononoke',
            route = 'princess-mononoke',
            status = 'Released',
            release_date = day_after_tomorrow,
            overview = 'Ashitaka, a prince of the disappearing Emishi people, is cursed by a demonized boar god and must journey to the west to find a cure. Along the way, he encounters San, a young human woman fighting to protect the forest, and Lady Eboshi, who is trying to destroy it. Ashitaka must find a way to bring balance to this conflict.',
            runtime = 134,
            rating = 'PG-13',
            poster_path = '/kifrm5sCZNMa1GsSAANg040Hay5.jpg',
            backdrop_path = '/yoIybVuiUWtDf2X8dCt4vZgfC3q.jpg',
            trailer_path = 'opCxPAwdB6U',
            active = True
        )
        db.session.add(coming_soon)
        db.session.commit()

        yield client_both

        db.session.delete(now_playing)
        db.session.delete(coming_soon)
        db.session.commit
