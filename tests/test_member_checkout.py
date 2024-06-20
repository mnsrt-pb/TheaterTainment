''' Test movie ticket purchases for members. '''
from datetime import datetime
from flask import url_for
from flask_login import current_user
from tests.utils import login_member, logout, showtime_tomorrow
from theatert import db, bcrypt
from theatert.config_test import movie_a, showtime_data, visa
from theatert.models import Card, Cards, Seat, Ticket, Purchase, Purchased_Ticket

import calendar
import pytest
import os


''' MAP '''
@pytest.mark.skip
def test_map_display(client_movies):
    ''' Ticket seat map is displayed '''
    login_member(client_movies)

    response = client_movies.get(url_for('users.ticket_seat_map', showtime_id=1))
    assert response.status_code == 404
    assert b'/member/profile' in response.data

    logout(client_movies)
    showtime_tomorrow(client_movies)
    login_member(client_movies)

    response = client_movies.get(url_for('users.ticket_seat_map', showtime_id=1))
    assert response.status_code == 200
    assert b'/member/profile' in response.data

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


@pytest.mark.skip
def test_post_map(client_movies):
    ''' Test proceeding to checkout '''
    showtime_tomorrow(client_movies)
    login_member(client_movies)

    data = dict(
        screening_id = 1,
        seats_selected = '1, 2, 3',
        adult_tickets = 1,
        child_tickets = 1,
        senior_tickets = 1
    )

    response = client_movies.post(url_for('members.checkout'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Checkout' in response.data




''' CHECKOUT '''
@pytest.mark.skip
def test_checkout_login(client_movies):
    ''' Test sign in before checkout '''
    showtime_tomorrow(client_movies)

    # CHECKOUT
    data = dict(
        screening_id = 1,
        seats_selected = '1, 2, 3',
        adult_tickets = 1,
        child_tickets = 1,
        senior_tickets = 1,
        form1 = ''
    )

    data.update(visa)

    response = client_movies.post(url_for('members.checkout'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page.' in response.data
    assert response.request.path == url_for('users.member_login')

    
@pytest.mark.skip
def test_checkout_no_default_payment(client_movies):
    ''' Test checkout, receipt, and purchases (no default payment method) '''
    showtime_tomorrow(client_movies)
    login_member(client_movies)

    # CHECKOUT
    data = dict(
        screening_id = 1,
        seats_selected = '1, 2, 3',
        adult_tickets = 1,
        child_tickets = 1,
        senior_tickets = 1,
        form1 = 'ignore'
    )

    data.update(visa)

    response = client_movies.post(url_for('members.checkout_validate'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Thank you for your purchase' in response.data

    confirmation = ''
    with client_movies.application.app_context():
        purchase = Purchase.query.first()
        assert purchase
        assert purchase.member
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

    # PURCHASES
    response = client_movies.get(url_for('members.purchases'))
    assert response.status_code == 200
    assert str(confirmation).encode('utf-8') in response.data
    assert url_for('users.receipt', confirmation = confirmation).encode('utf-8') in response.data
 

@pytest.mark.skip
def test_checkout_no_default_payment_failure(client_movies):
    ''' Test checkout and purchases (no default payment method) with invalid data '''
    showtime_tomorrow(client_movies)
    login_member(client_movies)

    # CHECKOUT
    data = dict(
        screening_id = 1,
        seats_selected = '1, 2, 3',
        adult_tickets = 1,
        child_tickets = 1,
        senior_tickets = 1 
    )

    data.update(visa)
    response = client_movies.post(url_for('members.checkout_validate'), data=data, follow_redirects=True)
    assert response.status_code == 404

    # PURCHASES
    with client_movies.application.app_context():
        purchase = Purchase.query.first()
        assert not purchase


@pytest.mark.skip
def test_checkout_save_default_payment(client_movies):
    ''' Test checkout, receipt, and purchases (save payment method) ''' 
    showtime_tomorrow(client_movies)
    login_member(client_movies)
    current_id = current_user.id

    # CHECKOUT
    data = dict(
        screening_id = 1,
        seats_selected = '1, 2, 3',
        adult_tickets = 1,
        child_tickets = 1,
        senior_tickets = 1,
        form1 = 'ignore', 
        save = True
    )

    data.update(visa)

    response = client_movies.post(url_for('members.checkout_validate'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Thank you for your purchase' in response.data

    confirmation = ''
    with client_movies.application.app_context():
        purchase = Purchase.query.first()
        assert purchase
        assert purchase.member
        assert str(purchase.confirmation).encode('utf-8') in response.data
        confirmation = purchase.confirmation

        card = Card.query.filter(Card.id.is_(purchase.card_id)).first()
        assert (card.card_type).encode('utf-8') in response.data 
        assert str(card.card_num)[-4:].encode('utf-8') in response.data

        assert Cards.query.filter_by(member_id=current_id, active=True).first()

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

    # PURCHASES
    response = client_movies.get(url_for('members.purchases'))
    assert response.status_code == 200
    assert str(confirmation).encode('utf-8') in response.data
    assert url_for('users.receipt', confirmation = confirmation).encode('utf-8') in response.data


@pytest.mark.skip
def test_checkout_default_payment(client_movies):
    ''' Test checkout and receipt, and purchases (default payment method) '''
    showtime_tomorrow(client_movies)
    login_member(client_movies)
    current_id = current_user.id

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
        db.session.commit()

        cards = Cards( member_id = current_id, card_id = card.id )
        db.session.add(cards)
        db.session.commit()

    # CHECKOUT
    data = dict(
        screening_id = 1,
        seats_selected = '1, 2, 3',
        adult_tickets = 1,
        child_tickets = 1,
        senior_tickets = 1,
        sec_code = visa['sec_code']
    )

    response = client_movies.post(url_for('members.checkout_validate'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Thank you for your purchase' in response.data

    confirmation = ''
    with client_movies.application.app_context():
        purchase = Purchase.query.first()
        assert purchase
        assert purchase.member
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

    # PURCHASES
    response = client_movies.get(url_for('members.purchases'))
    assert response.status_code == 200
    assert str(confirmation).encode('utf-8') in response.data
    assert url_for('users.receipt', confirmation = confirmation).encode('utf-8') in response.data
    

@pytest.mark.skip
def test_checkout_default_payment_failure(client_movies):
    ''' Test checkout and purchases (default payment method) with invalid data '''

    showtime_tomorrow(client_movies)
    login_member(client_movies)
    current_id = current_user.id

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
        db.session.commit()

        cards = Cards( member_id = current_id, card_id = card.id )
        db.session.add(cards)
        db.session.commit()

    # CHECKOUT
    data = dict(
        screening_id = 1,
        seats_selected = '1, 2, 3',
        adult_tickets = 1,
        child_tickets = 1,
        senior_tickets = 1,
        sec_code = '000',
    )

    response = client_movies.post(url_for('members.checkout_validate'), data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid data, transaction declined.' in response.data

    with client_movies.application.app_context():
        purchase = Purchase.query.first()
        assert not purchase

