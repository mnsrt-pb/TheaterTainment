''' Test showtime management and track changes made by employee. '''

from datetime import datetime, timedelta
from flask import url_for
from flask_login import current_user
from tests.utils import login_employee
from theatert import db, max_price, min_price
from theatert.models import Movie, Change, Screening, Seat, Ticket
from theatert.config_test import movie_a, showtime_data, tomorrow, yesterday

import pytest
import os


''' DISPLAY SHOWTIMES '''
@pytest.mark.skip
def test_display_showtimes(client_movie):
    ''' Showtimes are correctly displayed in all, past, and upcoming
        Showtimes are correctly displayin in movie's showtimes. Auditorium and date filter work. '''
    # NOTE: For this test, the screening created in db will not have tickets.
    #  Tickets are generated automatically in add_showtime when a new screening is added to db. 
    login_employee(client_movie)

    response = client_movie.get(url_for('employees.showtimes.all_showtimes'))
    assert response.status_code == 200
    assert b'There are no showtimes.' in response.data

    response = client_movie.get(url_for('employees.showtimes.past_showtimes'))
    assert response.status_code == 200
    assert b'There are no showtimes.' in response.data

    response = client_movie.get(url_for('employees.showtimes.upcoming_showtimes'))
    assert response.status_code == 200
    assert b'There are no showtimes.' in response.data

    
    data = dict( 
        m_id = 1,
        a_id = 1,
        adult_price = 12.50,
        child_price = 10.50,
        senior_price = 9.00
    )

    with client_movie.application.app_context():
        movie = Movie.query.first()
        movie.active = True

        # Upcoming showtime
        start_dt = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        end_dt = start_dt + timedelta(minutes=(movie.runtime)+20)
        screening = Screening(
                    start_datetime = start_dt,
                    end_datetime = end_dt,
                    adult_price = data['adult_price'],
                    child_price = data['child_price'],
                    senior_price = data['senior_price'],
                    auditorium_id = data['a_id'],
                    movie_id = data['m_id']
                )  
        db.session.add(screening)
        
        # Past showtime
        start_dt = yesterday.replace(hour=10, minute=30, second=0, microsecond=0)
        end_dt = start_dt + timedelta(minutes=(movie.runtime)+20)
        screening = Screening(
                    start_datetime = start_dt,
                    end_datetime = end_dt,
                    adult_price = data['adult_price'],
                    child_price = data['child_price'],
                    senior_price = data['senior_price'],
                    auditorium_id = data['a_id'],
                    movie_id = data['m_id']
                )  
        db.session.add(screening)
        db.session.commit()

    response = client_movie.get(url_for('employees.showtimes.all_showtimes'))
    assert response.status_code == 200
    assert b'10:00 AM' in response.data
    assert b'10:30 AM' in response.data
    assert b'/employee/tickets/1' in response.data
    assert b'/employee/tickets/2' in response.data

    # NOTE: If auditorium/date filters work for all showtimes it also works for past and upcoming.
    response = client_movie.get(url_for('employees.showtimes.all_showtimes') + '?auditorium=2')
    assert response.status_code == 200
    assert b'There are no showtimes.' in response.data
    
    response = client_movie.get(url_for('employees.showtimes.all_showtimes') + '?date=' + datetime.now().strftime("%Y-%m-%d"))
    assert response.status_code == 200
    assert b'There are no showtimes.' in response.data

    response = client_movie.get(url_for('employees.showtimes.past_showtimes'))
    assert response.status_code == 200
    assert b'10:00 AM' not in response.data
    assert b'10:30 AM' in response.data
    assert b'/employee/tickets/1' not in response.data
    assert b'/employee/tickets/2' in response.data

    response = client_movie.get(url_for('employees.showtimes.upcoming_showtimes'))
    assert response.status_code == 200
    assert b'10:00 AM' in response.data
    assert b'10:30 AM' not in response.data
    assert b'/employee/tickets/1' in response.data
    assert b'/employee/tickets/2' not in response.data

    response = client_movie.get(url_for('employees.showtimes.movie', movie_route=movie_a['route']))
    assert response.status_code == 200
    assert b'10:00 AM' in response.data
    assert b'10:30 AM' in response.data
    assert b'/employee/tickets/1' in response.data
    assert b'/employee/tickets/2' in response.data
    
    response = client_movie.get(url_for('employees.showtimes.movie', movie_route=movie_a['route']) + '?auditorium=2')
    assert response.status_code == 200
    assert b'There are no showtimes.' in response.data
    
    response = client_movie.get(url_for('employees.showtimes.movie', movie_route=movie_a['route']) + '?date=' + datetime.now().strftime("%Y-%m-%d"))
    assert response.status_code == 200
    assert b'There are no showtimes.' in response.data




''' ADD SHOWTIMES '''
@pytest.mark.skip
def test_add_showtime_(client_movie):
    ''' Test add showtime
        Users can add a showtime to a movie if it exists, is not deleted, active, 
        and its release date is at most 20 days from today's date.
    '''
    # NOTE: add showtime in showtimes.movie redirects to showtimes.add_showtime 
    # so adding showtimes is only tested inside showtimes.add_showtim
    login_employee(client_movie)
    current_id =  current_user.id

    with client_movie.application.app_context():
        movie = Movie.query.first()
        movie.active = True

        # Release date is at most 20 days from today's date
        coming_soon = Movie (
            tmdb_id = 4935, # Howl's Moving Castle's tmdb id
            title = 'Not Released',
            route = 'not-released',
            release_date = datetime.now() + timedelta(days=20),
            runtime = 50,
            active = True)
        # NOTE: if a movie is active it must have poster, backdrop, and trailer paths but it can be ignored for this test
            # This is checked in test_activate_movie
        db.session.add(coming_soon)
        db.session.commit()

    # RELEASED MOVIE
    response = client_movie.post(url_for('employees.showtimes.add_showtime'), data=showtime_data, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/showtimes/' + movie_a['route']
    assert b'Showtime was created and tickets have been generated.' in response.data

    # Screening and Tickets generated!
    with client_movie.application.app_context():
        screening = Screening.query.first()
        assert screening

        seat_count = Seat.query.filter(
                            db.and_(
                                Seat.auditorium_id.is_(screening.auditorium_id), 
                                Seat.seat_type.is_not('empty'))).count()
        assert Ticket.query.count() == seat_count

        change = Change.query
        change_total, change = change.count(), change.first()
        change_total == 1
        assert change.employee_id == current_id
        assert change.action == 'added'
        assert change.table_name == 'screening'
        assert change.data_id == screening.id

    # UNRELEASED MOVIE
    data = dict(
        m_id = 2, 
        a_id = 2, 
        date_time = (datetime.now() + timedelta(days=21)).replace(hour=10, minute=0, second=0, microsecond=0), # tomorrow at 10AM
        adult_price = showtime_data['adult_price'],
        child_price = showtime_data['child_price'],
        senior_price = showtime_data['senior_price']
    )

    response = client_movie.post(url_for('employees.showtimes.add_showtime'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/showtimes/not-released'
    assert b'Showtime was created and tickets have been generated.' in response.data

    # Screening and Tickets generated!
    with client_movie.application.app_context():
        screening = Screening.query.order_by(Screening.id.desc()).first()
        assert screening

        seat_count = Seat.query.filter(
                            db.and_(
                                Seat.auditorium_id.is_(screening.auditorium_id), 
                                Seat.seat_type.is_not('empty'))).count()
        assert Ticket.query.filter(Ticket.screening_id.is_(screening.id)).count() == seat_count

        change = Change.query
        change_total, change = change.count(), change.order_by(Change.id.desc()).first()
        change_total == 2
        assert change.employee_id == current_id
        assert change.action == 'added'
        assert change.table_name == 'screening'
        assert change.data_id == screening.id


@pytest.mark.skip
def test_add_showtime_failure(client_users):
    ''' Test add showtime with incorrect data
        Users can add a showtime to a movie if it exists, is not deleted, active, 
        and its release date is at most 20 days from today's date.
    '''
    # NOTE: active should never be true for deleted movies but it's necessary for this test
    # NOTE: if a movie is active it must have poster, backdrop, and trailer paths but it can be ignored for this test
            # This is checked in test_activate_movie

    login_employee(client_users)
    response = client_users.get(url_for('employees.showtimes.add_showtime'))
    assert response.status_code == 200

    with client_users.application.app_context():
        deleted = Movie (
            tmdb_id = 12429, # Ponyo's tmdb id
            title = 'Deleted',
            route = 'deleted',
            deleted = True, 
            active = True, 
            release_date = datetime.now())
        db.session.add(deleted)

        inactive = Movie (
            tmdb_id = 128, # Princess Mononoke's tmdb id
            title = 'Inactive',
            route = 'inactive', 
            release_date = datetime.now())
        db.session.add(inactive)

        # Release date is NOT at most 20 days from today's date
        coming_soon_incorrect = Movie (
            tmdb_id = 4935, # Howl's Moving Castle's tmdb id
            title = 'More Than 20 Days',
            route = 'more-than-20-days',
            active = True,
            release_date = datetime.now() + timedelta(days=21))
        db.session.add(coming_soon_incorrect)
        
        # Correct movie entry but other data will be incorrect
        movie = Movie(
            tmdb_id = movie_a['tmdb_id'],
            title = movie_a['title'],
            route = movie_a['route'],
            status = movie_a['status'],
            release_date = datetime.now() + timedelta(days=3),
            overview = movie_a['overview'],
            runtime = movie_a['runtime'],
            rating = movie_a['rating'],
            poster_path = movie_a['poster_path'],
            backdrop_path = movie_a['backdrop_path'],
            trailer_path = movie_a['trailer_path'],
            active = True
        )
        db.session.add(movie)
        db.session.commit()

    # Add showtime to a deleted movie
    data = dict( 
        m_id = 1, #deleted
        a_id = 1,
        date_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0),
        adult_price = 12.50,
        child_price = 10.50,
        senior_price = 9.00
    )

    response = client_users.post(url_for('employees.showtimes.add_showtime'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/showtimes/add-showtime'
    assert b'Not a valid choice.' in response.data

    # Add showtime to an inactivated movie
    data['m_id'] = 2 # inactive
    response = client_users.post(url_for('employees.showtimes.add_showtime'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/showtimes/add-showtime'
    assert b'Not a valid choice.' in response.data
    
    # Add showtime to a movie when its release date is more than 20 days from today's date
    data['m_id'] = 3 # coming soon incorrect
    response = client_users.post(url_for('employees.showtimes.add_showtime'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/showtimes/add-showtime'
    assert b'Not a valid choice.' in response.data

    # Add showtime with an auditorium that doesn't exist
    data['m_id'] = 4 # valid movie
    data['a_id'] = 5
    response = client_users.post(url_for('employees.showtimes.add_showtime'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/showtimes/add-showtime'
    assert b'Not a valid choice.' in response.data

    # Showtimes date and time are before movie's releasae date
    data['a_id'] = 1 # valid auditorium
    response = client_users.post(url_for('employees.showtimes.add_showtime'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/showtimes/add-showtime'
    assert b'has not been released for the date entered.' in response.data

    # Showtime time has passed
    yesterday =  datetime.now() - timedelta(days=1)
    data['date_time'] = yesterday.replace(hour=10, minute=0, second=0, microsecond=0)
    response = client_users.post(url_for('employees.showtimes.add_showtime'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/showtimes/add-showtime'
    assert b'This date/time has passed!' in response.data

    # Showtime time is before earliest screening time
    data['date_time'] = tomorrow.replace(hour=9, minute=59, second=0, microsecond=0)
    response = client_users.post(url_for('employees.showtimes.add_showtime'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/showtimes/add-showtime'
    assert b'Invalid time.' in response.data


    # Showtime time is after latest screening time
    data['date_time'] = tomorrow.replace(hour=22, minute=1, second=0, microsecond=0)
    response = client_users.post(url_for('employees.showtimes.add_showtime'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/showtimes/add-showtime'
    assert b'Invalid time.' in response.data
    
    # Price is less than min price 
    data['date_time'] = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0) # valid entry
    data['adult_price'] = min_price - 1
    response = client_users.post(url_for('employees.showtimes.add_showtime'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/showtimes/add-showtime'
    assert b'Must be between $' in response.data

    # Price is greater than max price
    data['date_time'] = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0) # valid entry
    data['adult_price'] = max_price + 1
    response = client_users.post(url_for('employees.showtimes.add_showtime'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/showtimes/add-showtime'
    assert b'Must be between $' in response.data

    # Check that no screenigs or tickets have been added :)
    with client_users.application.app_context():
        assert Screening.query.count() == 0
        assert Ticket.query.count() == 0
        assert Change.query.count() == 0


@pytest.mark.skip
@pytest.mark.parametrize('hour, minute', [(10, 0), (11, 00), (12, 25)])
def test_add_showtime_failure_2(client_movie, hour, minute):
    ''' Test screening two movies in the same auditorium at overlapping times. '''
    # NOTE: For this test, the screening created in db will not have tickets.
    #  Tickets are generated automatically in add_showtime when a new screening is added to db. 
    
    login_employee(client_movie)

    data = dict( 
        m_id = 1,
        a_id = 1,
        date_time = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0),
        adult_price = 12.50,
        child_price = 10.50,
        senior_price = 9.00
    )

    with client_movie.application.app_context():
        movie = Movie.query.first()
        movie.active = True

        start_dt = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        end_dt = start_dt + timedelta(minutes=(movie.runtime)+20)

        # Movie screens from 10:00AM - 12:25 AM
        screening = Screening(
                    start_datetime = start_dt,
                    end_datetime = end_dt,
                    adult_price = data['adult_price'],
                    child_price = data['child_price'],
                    senior_price = data['senior_price'],
                    auditorium_id = data['a_id'],
                    movie_id = data['m_id']
                )  
        db.session.add(screening)
        db.session.commit()

    response = client_movie.post(url_for('employees.showtimes.add_showtime'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/employee/showtimes/add-showtime'
    assert b'A movie will screen in Auditorium 1 at this time. Try a different auditorium or time.' in response.data

    # Check that no screenigs or tickets were added :)
    with client_movie.application.app_context():
        assert Screening.query.count() == 1
        assert Ticket.query.count() == 0
        assert Change.query.count() == 0

