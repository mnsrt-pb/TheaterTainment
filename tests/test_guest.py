''' Test guest pages '''

from datetime import datetime, timedelta
from flask import url_for
from tests.utils import showtime_tomorrow

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

    assert b'Spirited Away' in response.data
    assert b'Princess Mononoke' in response.data

    assert b'/movie/spirited-away' in response.data
    assert b'/movie/princess-mononoke' in response.data

    assert b'/u1gGwSHTqTJ4hyclrC8owtJO66Y.jpg' in response.data
    assert b'/kifrm5sCZNMa1GsSAANg040Hay5.jpg' in response.data

    assert b'/member/1/add_watchlist' in response.data
    assert b'/member/2/add_watchlist' in response.data

    assert b'/ticket-seat-map/1' not in response.data

    tomorrow = datetime.now() + timedelta(days=1)
    response = client_movies.get(url_for('users.home') + '?date=' + tomorrow.strftime("%Y-%m-%d"))

    assert response.status_code == 200
    assert b'/ticket-seat-map/1' in response.data


@pytest.mark.skip
def test_display_movie(client_movies):
    ''' Movie info page is displayed '''
    showtime_tomorrow(client_movies) 

    response = client_movies.get(url_for('users.movie', movie_route='spirited-away'))
    assert response.status_code == 200
    assert b'/member/profile' not in response.data

    assert b'Spirited Away' in response.data
    assert b'PG' in response.data
    assert b'Jul 20, 2001' in response.data
    assert b'/u1gGwSHTqTJ4hyclrC8owtJO66Y.jpg' in response.data
    assert b'/ogRfsqklWMRpzmq4ZJcI0MvqzlN.jpg' in response.data
    assert b'GAp2_0JJskk' in response.data
    assert b'A young girl, Chihiro, becomes trapped in a strange new world of spirits.' in response.data
    assert b'/member/1/add_watchlist' in response.data

    tomorrow = datetime.now() + timedelta(days=1)
    response = client_movies.get(url_for('users.movie', movie_route='spirited-away') + '?date=' + tomorrow.strftime("%Y-%m-%d"))

    assert response.status_code == 200
    assert b'/ticket-seat-map/1' in response.data


@pytest.mark.skip
def test_display_movies(client_movies):
    ''' Now playing and coming soon are correctly displayed '''

    response = client_movies.get(url_for('users.movies'))
    assert response.status_code == 200
    assert b'/member/profile' not in response.data

    assert b'Spirited Away' in response.data
    assert b'Princess Mononoke' not in response.data

    assert b'/movie/spirited-away' in response.data
    assert b'/movie/princess-mononoke' not in response.data

    assert b'/u1gGwSHTqTJ4hyclrC8owtJO66Y.jpg' in response.data
    assert b'/kifrm5sCZNMa1GsSAANg040Hay5.jpg' not in response.data

    assert b'/member/1/add_watchlist' in response.data
    assert b'/member/2/add_watchlist' not in response.data

    response = client_movies.get(url_for('users.movies_coming_soon'))
    assert response.status_code == 200
    assert b'Spirited Away' not in response.data
    assert b'Princess Mononoke' in response.data

    assert b'/movie/spirited-away' not in response.data
    assert b'/movie/princess-mononoke' in response.data

    assert b'/u1gGwSHTqTJ4hyclrC8owtJO66Y.jpg' not in response.data
    assert b'/kifrm5sCZNMa1GsSAANg040Hay5.jpg' in response.data

    assert b'/member/1/add_watchlist' not in response.data
    assert b'/member/2/add_watchlist' in response.data

    