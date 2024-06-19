''' Test guest pages '''

from datetime import datetime, timedelta
from flask import url_for
from flask_login import current_user
from tests.utils import showtime_tomorrow, login_member
from theatert import bcrypt, db
from theatert.models import Member, Card, Cards, Watchlist
from theatert.config_test import visa, movie_a, movie_b

import calendar
import pytest
import os


if os.environ.get('SKIP_TEST_MEMBER', 'false').lower() == 'true':
    pytestmark = pytest.mark.skip("Skipping tests in test_register_login.py")


''' MOVIES '''
@pytest.mark.skip
def test_home(client_movies):
    ''' Movies and their showtimes are displayed'''
    showtime_tomorrow(client_movies) # added one showtime so showtime id is 1
    login_member(client_movies)

    response = client_movies.get(url_for('users.home'))
    assert response.status_code == 200
    assert b'/member/profile' in response.data

    assert movie_a['title'].encode('utf-8') in response.data
    assert movie_b['title'].encode('utf-8') in response.data

    assert movie_a['route'].encode('utf-8') in response.data
    assert movie_b['route'].encode('utf-8') in response.data

    assert movie_a['poster_path'].encode('utf-8') in response.data
    assert movie_b['poster_path'].encode('utf-8') in response.data

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
    login_member(client_movies)

    response = client_movies.get(url_for('users.movie', movie_route=movie_a['route']))
    assert response.status_code == 200
    assert b'/member/profile' in response.data

    assert movie_a['title'].encode('utf-8') in response.data
    assert movie_a['rating'].encode('utf-8') in response.data
    assert movie_a['release_date'].strftime("%b %d, %Y").encode('utf-8') in response.data
    assert movie_a['poster_path'].encode('utf-8') in response.data
    assert movie_a['backdrop_path'].encode('utf-8') in response.data
    assert movie_a['trailer_path'].encode('utf-8') in response.data
    assert movie_a['overview'].encode('utf-8') in response.data

    assert b'/member/1/add_watchlist' in response.data

    tomorrow = datetime.now() + timedelta(days=1)
    response = client_movies.get(url_for('users.movie', movie_route=movie_a['route']) + '?date=' + tomorrow.strftime("%Y-%m-%d"))

    assert response.status_code == 200
    assert b'/ticket-seat-map/1' in response.data


@pytest.mark.skip
def test_display_movies(client_movies):
    ''' Now playing and coming soon are correctly displayed '''
    login_member(client_movies)

    response = client_movies.get(url_for('users.movies'))
    assert response.status_code == 200
    assert b'/member/profile' in response.data

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




''' PROFILE '''
@pytest.mark.skip
def test_profile_display(client_users):
    ''' Profile info is correctly displayed. Without DOB or CC. '''
    login_member(client_users)

    response = client_users.get(url_for('members.profile'))
    assert response.status_code == 200
    assert b'Test User' in response.data
    assert b'ZIP Code: 12345' in response.data
    assert b'test@user.com' in response.data
    assert b'5107488230' in response.data
    assert b'Date of Birth:' not in response.data


@pytest.mark.skip
def test_edit_personal_info(client_users):
    ''' Test changes in personal information '''
    # NOTE: Phone number was taken from import phonenumbers' documentation
    login_member(client_users)

    data = dict(
        fname = 'Different',
        lname = 'Name',
        dob = '12/25',
        zip_code = '67890',
        phone = '7034800500'
    )

    response = client_users.post(url_for('members.profile'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your information has been updated!' in response.data

    with client_users.application.app_context():
        member = Member.query.first()
        assert member.fname == 'Different'
        assert member.lname == 'Name'
        assert member.phone == 7034800500
        assert member.zip_code == 67890
        assert member.dob ==  datetime.strptime('1900-12-25', '%Y-%m-%d').date()
    assert b'Date of Birth: 12/25' in response.data


@pytest.mark.skip
def test_change_email(client_users):
    ''' Test change email '''
    login_member(client_users)

    data = dict(
        email = 'different@email.com',
        confirm_email = 'different@email.com',
        password = 'valid*123'
    )

    response = client_users.post(url_for('members.profile'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your email has been updated!' in response.data

    with client_users.application.app_context():
        member = Member.query.first()
        assert member.email == 'different@email.com'



@pytest.mark.skip
def test_change_email_failure(client_users):
    ''' Test change email with invalid data '''
    login_member(client_users)

    data = dict(
        email = 'test@user.com',
        confirm_email = 'test@user.com',
        password = 'valid*123',
    )

    response = client_users.post(url_for('members.profile'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'You must use a different email.' in response.data

    with client_users.application.app_context():
        second = Member (
            username = 'second@user.com',
            password = bcrypt.generate_password_hash('valid*123').decode('utf-8'),
            email = 'second@user.com',
            fname = 'Second',
            lname = 'User',
            phone = '5107488230',
            zip_code = '12345'
        )
        db.session.add(second)
        db.session.commit()
    
    data = dict(
        email = 'second@user.com',
        confirm_email = 'second@user.com',
        password = 'valid*123',
    )

    response = client_users.post(url_for('members.profile'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'An account with this email already exists.' in response.data


@pytest.mark.skip
def test_change_password(client_users):
    ''' Test change password '''
    login_member(client_users)

    data = dict(
        current_password = 'valid*123',
        new_password = 'als0valid!',
        confirmation = 'als0valid!'
    )

    response = client_users.post(url_for('members.profile'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Your password has been updated!' in response.data

    with client_users.application.app_context():
        member = Member.query.first()
        assert bcrypt.check_password_hash(member.password, data['new_password'])
        

@pytest.mark.skip
def test_change_password_failure(client_users):
    ''' Test change password with incorrect data '''
    login_member(client_users)
    current_password = current_user.password

    data = dict(
        current_password = 'incorrect',
        new_password = 'als0valid!',
        confirmation = 'als0valid!'
    )

    response = client_users.post(url_for('members.profile'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'To change your password, you must enter the current password for the account.' in response.data

    with client_users.application.app_context():
        member = Member.query.first()
        assert member.password == current_password # same hash


@pytest.mark.skip
def test_add_cc(client_users):
    ''' Test add credit card '''
    # NOTE: card number was taken from Paypal's card testing data 
    login_member(client_users)
    current_id =  current_user.id

    # Add card if card does't exist
    data = dict(
        card_type = visa['card_type'],
        card_number = visa['card_number'],
        exp_month = visa['exp_month'],
        exp_year = visa['exp_year'],
        zip_code = visa['zip_code'],
        sec_code = visa['sec_code']
    )

    response = client_users.post(url_for('members.profile'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Default payment saved!' in response.data

    with client_users.application.app_context():
        card = Card.query.first()
        cards = Cards.query.first()
        assert card and cards
        assert cards.member_id == current_id
        assert cards.card_id == card.id

    # Add card if card was used by a member and/or current user before
        cards.active = False
        db.session.commit()

    response = client_users.post(url_for('members.profile'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Default payment saved!' in response.data

    with client_users.application.app_context():
        card = Card.query.first()
        cards = Cards.query.first()
        assert cards.active

    # Add card if card was used by a guest before
        card.member = False
        cards.active = False
        db.session.commit()

    response = client_users.post(url_for('members.profile'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Default payment saved!' in response.data

    with client_users.application.app_context():
        assert Card.query.count() == 2
        assert Cards.query.count() == 2

        card = Card.query.filter_by(member = True).first()
        cards = Cards.query.filter_by(member_id = current_id, card_id = card.id).first()
        assert card
        assert cards


@pytest.mark.skip
@pytest.mark.parametrize('exp_month, exp_year, zip_code, sec_code', 
                         [(visa['exp_month'] + 1, visa['exp_year'], visa['zip_code'], visa['sec_code']), 
                          (visa['exp_month'], visa['exp_year'] + 1, visa['zip_code'], visa['sec_code']),
                          (visa['exp_month'], visa['exp_year'], '00000', visa['sec_code']),
                          (visa['exp_month'], visa['exp_year'], visa['zip_code'], '000')])
def test_add_cc_failure(client_users, exp_month, exp_year, zip_code, sec_code):
    ''' Test add credit card with incorrect data '''
    # NOTE: card number was taken from Paypal's card testing data 
    login_member(client_users)

    member_data = dict(
        card_type = 'Discover',
        card_number = '6011287354412626',
        exp_month = 5,
        exp_year = datetime.today().year + 1,
        zip_code = '44444',
        sec_code = '335'
    )
    guest_data = dict(
        card_type = visa['card_type'],
        card_number = visa['card_number'],
        exp_month = visa['exp_month'],
        exp_year = visa['exp_year'],
        zip_code = visa['zip_code'],
        sec_code = visa['sec_code']
    )

    with client_users.application.app_context():
        day = str(calendar.monthrange(guest_data['exp_year'], guest_data['exp_month'])[1])
        exp_date = datetime.strptime(str(guest_data['exp_month']) + '/' + day + '/' + str(guest_data['exp_year']), '%m/%d/%Y').date()

        member_card = Card(
                    card_num = guest_data['card_number'],
                    exp_date = exp_date,
                    card_type = guest_data['card_type'],
                    billing_zip = guest_data['zip_code'],
                    sec_code = bcrypt.generate_password_hash(guest_data['sec_code']).decode('utf-8'),
                    )
        db.session.add(member_card)

        guest_card = Card(
                    card_num = member_data['card_number'],
                    exp_date = exp_date,
                    card_type = member_data['card_type'],
                    billing_zip = member_data['zip_code'],
                    sec_code = bcrypt.generate_password_hash(member_data['sec_code']).decode('utf-8'), 
                    member = False
                    )
        db.session.add(guest_card)

        db.session.commit()

    # Cards with the same card number's must have the same data (sec_code, exp_date, and billing_zip)
    member_data['sec_code'] = sec_code
    member_data['exp_month'] = exp_month
    member_data['exp_year'] = exp_year
    member_data['zip_code'] = zip_code
    response = client_users.post(url_for('members.profile'), data=member_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid card.' in response.data

    guest_data['sec_code'] = sec_code
    guest_data['exp_month'] = exp_month
    guest_data['exp_year'] = exp_year
    guest_data['zip_code'] = zip_code
    response = client_users.post(url_for('members.profile'), data=guest_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid card.' in response.data

    with client_users.application.app_context():
        assert Card.query.count() == 2
        assert Cards.query.count() == 0


@pytest.mark.skip
def test_delete_cc(client_users):
    ''' Test delete default payment method '''
    login_member(client_users)
    current_id = current_user.id

    with client_users.application.app_context():
        day = str(calendar.monthrange(visa['exp_year'] + 1, visa['exp_month'])[1])
        exp_date = datetime.strptime(str(visa['exp_month']) + '/' + day + '/' + str(visa['exp_year'] + 1), '%m/%d/%Y').date()

        card = Card(
                    card_num = visa['card_number'],
                    exp_date = exp_date,
                    card_type = visa['card_type'],
                    billing_zip = visa['zip_code'],
                    sec_code = bcrypt.generate_password_hash(visa['sec_code']).decode('utf-8'),
                    )
        db.session.add(card)
        db.session.commit()

        cards = Cards( member_id = current_id, card_id = card.id )
        db.session.add(cards)
        db.session.commit()

    response = client_users.post(url_for('members.profile'), data={'delete':''}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Default payment removed!' in response.data

    with client_users.application.app_context():
        default_payment = Cards.query.filter_by(member_id = current_id).first()
        assert not default_payment.active 




''' WATCHLIST '''
@pytest.mark.skip
def test_watchlist_empty(client_movie):
    ''' Test watchlist display '''
    login_member(client_movie)

    response = client_movie.get(url_for('members.watchlist'))
    assert response.status_code == 200
    assert b'Don\'t miss that movie you want to see. Tap the' in response.data


@pytest.mark.skip
def test_add_watchlist(client_movies):
    ''' Test watchlist display '''
    login_member(client_movies)
    current_id = current_user.id
    m_id = 1

    response = client_movies.get(url_for('members.add_watchlist', m_id = m_id))
    assert response.status_code == 302

    with client_movies.application.app_context():
        watchlist = Watchlist.query.filter_by(member_id = current_id).first()
        assert watchlist.movie_id == m_id


@pytest.mark.skip
def test_remove_watchlist(client_movies):
    ''' Test watchlist display '''
    login_member(client_movies)
    current_id = current_user.id
    m_id = 1

    with client_movies.application.app_context():
        watchlist = Watchlist( movie_id = m_id, member_id = current_id )
        db.session.add(watchlist)
        db.session.commit()
        
    response = client_movies.get(url_for('members.remove_watchlist', m_id = m_id))
    assert response.status_code == 302

    with client_movies.application.app_context():
        assert not Watchlist.query.filter_by(member_id = current_id).first()

