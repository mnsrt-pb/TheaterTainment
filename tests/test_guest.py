''' Test guest pages '''

from flask import url_for
from tests.utils import showtime_tomorrow
from theatert.config_test import movie_a, movie_b, tomorrow

import pytest
import os


if os.environ.get('SKIP_TEST_GUEST', 'false').lower() == 'true':
    pytestmark = pytest.mark.skip("Skipping tests in test_register_login.py")


@pytest.mark.skip
def test_home(client_movies):
    ''' Movies and their showtimes are displayed'''
    # added one showtime so showtime id is 1
    showtime_tomorrow(client_movies) 

    response = client_movies.get(url_for('users.home'))
    assert response.status_code == 200
    assert b'/member/profile' not in response.data

    assert movie_a['title'].encode('utf-8') in response.data
    assert movie_b['title'].encode('utf-8') in response.data

    assert movie_a['route'].encode('utf-8') in response.data
    assert movie_b['route'].encode('utf-8') in response.data

    assert movie_a['poster_path'].encode('utf-8') in response.data
    assert movie_b['poster_path'].encode('utf-8') in response.data

    assert b'/member/1/add_watchlist' in response.data
    assert b'/member/2/add_watchlist' in response.data

    assert b'/ticket-seat-map/1' not in response.data

    response = client_movies.get(url_for('users.home') + '?date=' + tomorrow.strftime("%Y-%m-%d"))

    assert response.status_code == 200
    assert b'/ticket-seat-map/1' in response.data


@pytest.mark.skip
def test_display_movie(client_movies):
    ''' Movie info page is displayed '''
    showtime_tomorrow(client_movies) 

    response = client_movies.get(url_for('users.movie', movie_route=movie_a['route']))
    assert response.status_code == 200
    assert b'/member/profile' not in response.data

    assert movie_a['title'].encode('utf-8') in response.data
    assert movie_a['rating'].encode('utf-8') in response.data
    assert movie_a['release_date'].strftime("%b %d, %Y").encode('utf-8') in response.data
    assert movie_a['poster_path'].encode('utf-8') in response.data
    assert movie_a['backdrop_path'].encode('utf-8') in response.data
    assert movie_a['trailer_path'].encode('utf-8') in response.data
    assert movie_a['overview'].encode('utf-8') in response.data

    assert b'/member/1/add_watchlist' in response.data

    response = client_movies.get(url_for('users.movie', movie_route=movie_a['route']) + '?date=' + tomorrow.strftime("%Y-%m-%d"))

    assert response.status_code == 200
    assert b'/ticket-seat-map/1' in response.data


@pytest.mark.skip
def test_display_movies(client_movies):
    ''' Now playing and coming soon are correctly displayed '''

    response = client_movies.get(url_for('users.movies'))
    assert response.status_code == 200
    assert b'/member/profile' not in response.data

    assert movie_a['title'].encode('utf-8') in response.data
    assert movie_b['title'].encode('utf-8')  not in response.data

    assert movie_a['route'].encode('utf-8') in response.data
    assert movie_b['route'].encode('utf-8') not in response.data

    assert movie_a['poster_path'].encode('utf-8') in response.data
    assert movie_b['poster_path'].encode('utf-8') not in response.data

    assert b'/member/1/add_watchlist' in response.data
    assert b'/member/2/add_watchlist' not in response.data

    response = client_movies.get(url_for('users.movies_coming_soon'))
    assert response.status_code == 200
    assert movie_a['title'].encode('utf-8') not in response.data
    assert movie_b['title'].encode('utf-8') in response.data

    assert movie_a['route'].encode('utf-8') not in response.data
    assert movie_b['route'].encode('utf-8') in response.data

    assert movie_a['poster_path'].encode('utf-8') not in response.data
    assert movie_b['poster_path'].encode('utf-8') in response.data

    assert b'/member/1/add_watchlist' not in response.data
    assert b'/member/2/add_watchlist' in response.data

