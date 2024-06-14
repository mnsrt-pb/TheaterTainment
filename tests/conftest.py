from theatert import create_app, db
from theatert.users.utils import populate_db

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

