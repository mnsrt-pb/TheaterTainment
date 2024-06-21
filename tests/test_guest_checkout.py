''' Test movie ticket purchases for guests. '''
from datetime import datetime
from flask import url_for
from tests.utils import showtime_tomorrow
from theatert import db, bcrypt
from theatert.config_test import movie_a, showtime_data, visa
from theatert.models import Card, Seat, Ticket, Purchase, Purchased_Ticket

import calendar
import pytest


''' MAP '''
#@pytest.mark.skip
def test_map_display(client_movies):
    ''' Ticket seat map is displayed '''

    response = client_movies.get(url_for('users.ticket_seat_map', showtime_id=1))
    assert response.status_code == 404

    showtime_tomorrow(client_movies)

    response = client_movies.get(url_for('users.ticket_seat_map', showtime_id=1))
    assert response.status_code == 200
    assert movie_a['title'].encode('utf-8') in response.data
    assert str(showtime_data['adult_price']).encode('utf-8') in response.data
    assert str(showtime_data['child_price']).encode('utf-8') in response.data
    assert str(showtime_data['senior_price']).encode('utf-8') in response.data

    with client_movies.application.app_context():
        seats = Seat.query.filter(
                            db.and_(
                                Seat.auditorium_id.is_(showtime_data['a_id']), 
                                Seat.seat_type.is_not('empty'))).count()
        tickets = Ticket.query.filter_by(screening_id = 1)
        assert seats == tickets.count()

        for ticket in tickets:
            assert ('data-seat-id="' +  str(ticket.seat_id)  + '"').encode('utf-8') in response.data


#@pytest.mark.skip
def test_post_map(client_movies):
    ''' Test proceeding to checkout '''
    showtime_tomorrow(client_movies)

    data = dict(
        screening_id = 1,
        seats_selected = '1, 2, 3',
        adult_tickets = 1,
        child_tickets = 1,
        senior_tickets = 1
    )

    response = client_movies.post(url_for('users.checkout'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Sign in to use saved payment information. If you don\'t have an account, you can register for a Cinemark account.' in response.data


''' CHECKOUT '''
#@pytest.mark.skip
def test_checkout(client_movies):
    ''' Test checkout and receipt '''
    showtime_tomorrow(client_movies)

    # CHECKOUT
    data = dict(
        screening_id = 1,
        seats_selected = '1, 2, 3',
        adult_tickets = 1,
        child_tickets = 1,
        senior_tickets = 1,
        email = 'test@guest.com'
    )
    data.update(visa)

    response = client_movies.post(url_for('users.checkout_validate'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Thank you for your purchase' in response.data

    confirmation = ''
    with client_movies.application.app_context():
        purchase = Purchase.query.first()
        assert purchase
        assert not purchase.member
        assert str(purchase.confirmation).encode('utf-8') in response.data
        confirmation = purchase.confirmation

        card = Card.query.filter(Card.id.is_(purchase.card_id)).first()
        assert (card.card_type).encode('utf-8') in response.data 
        assert str(card.card_num)[-4:].encode('utf-8') in response.data

        purchased_tickets = Purchased_Ticket.query.filter_by(purchase_id = purchase.id)
        for p in purchased_tickets:
            ticket = Ticket.query.join(Seat).filter(Ticket.id.is_(p.ticket_id)).first()
            assert str(ticket.seat.row_name + str(ticket.seat.col)).encode('utf-8') in response.data
            print(str(ticket.seat.row_name + str(ticket.seat.col)).encode('utf-8'))


    assert ('Adult Tickets (' + str(data['adult_tickets']) + ')').encode('utf-8') in response.data
    assert ('Child Tickets (' + str(data['child_tickets']) + ')').encode('utf-8') in response.data
    assert ('Senior Tickets (' + str(data['senior_tickets']) + ')').encode('utf-8') in response.data

    assert str(showtime_data['adult_price'] * data['adult_tickets']).encode('utf-8') in response.data
    assert str(showtime_data['child_price'] * data['child_tickets']).encode('utf-8') in response.data
    assert str(showtime_data['senior_price'] * data['senior_tickets']).encode('utf-8') in response.data

    assert str(showtime_data['adult_price'] * data['adult_tickets'] + 
               showtime_data['child_price'] * data['child_tickets'] + 
               showtime_data['senior_price'] * data['senior_tickets']).encode('utf-8') in response.data
    
    # RECEIPT (users are redirected here after purchasing a ticket but can also get here via a get request)
    response = client_movies.get(url_for('users.receipt', confirmation = confirmation))
    assert response.status_code == 200
    

#@pytest.mark.skip
def test_checkout_failure(client_movies):
    ''' Test checkout with invalid data'''
    showtime_tomorrow(client_movies)

    with client_movies.application.app_context():
        day = str(calendar.monthrange(visa['exp_year'], visa['exp_month'])[1])
        exp_date = datetime.strptime(str(visa['exp_month']) + '/' + day + '/' + str(visa['exp_year']), '%m/%d/%Y').date()

        card = Card(
                    card_num = visa['card_number'],
                    exp_date = exp_date,
                    card_type = visa['card_type'],
                    billing_zip = visa['zip_code'],
                    sec_code = bcrypt.generate_password_hash(visa['sec_code']).decode('utf-8'),
                    )
        db.session.add(card)

    data = dict(
        screening_id = 1,
        seats_selected = '1, 2, 3',
        adult_tickets = 1,
        child_tickets = 1,
        senior_tickets = 1,
        email = 'test@guest.com'
    )
    data.update(visa)
    data['sec_code'] = '000'

    response = client_movies.post(url_for('users.checkout_validate'), data=data, follow_redirects=True)
    assert response.status_code == 200


#@pytest.mark.skip
def test_checkout_purchased_ticket(client_movies):
    ''' Test checkout a purchased ticket without a default payment method '''
    showtime_tomorrow(client_movies)

    # CHECKOUT
    data = dict(
        screening_id = 1,
        seats_selected = '1, 2, 3',
        adult_tickets = 1,
        child_tickets = 1,
        senior_tickets = 1,
        email = 'test@guest.com'
    )
    data.update(visa)

    response = client_movies.post(url_for('users.checkout_validate'), data=data, follow_redirects=True)
    assert response.status_code == 200

    # Purchase a ticket already bought
    response = client_movies.post(url_for('users.checkout_validate'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'is unavailable' in response.data

    with client_movies.application.app_context():
        for t in Purchase.query.all():
            print(t)
        assert Purchase.query.count() == 1

