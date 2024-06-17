from datetime import datetime
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
def client_member(client):
    ''' Member user in database. '''
    # NOTE: Phone number was taken from import phonenumbers' documentation

    with client.application.app_context():
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


        yield client

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


