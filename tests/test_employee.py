''' Test home page and theater auditoriums display. '''

from flask import url_for
from tests.utils import login_employee
from theatert import db
from theatert.models import Auditorium, Seat 

import pytest


''' AUDITORIUMS '''
#@pytest.mark.skip
def test_auditoriums(client_users):
    ''' Test if the registration pages load correctly. '''
    # NOTE: This tests the auditoriums inserted from populate_db()
    # This must be updated if auditorium data changes.

    login_employee(client_users)

    response = client_users.get(url_for('employees.auditoriums'))
    assert response.status_code == 200

    with client_users.application.app_context():
        auditoriums = Auditorium.query
        assert auditoriums.count() == 4
        seat = Seat.query
        assert seat.count() == 360
        seats = Seat.query.filter(
                            db.and_(
                                Seat.auditorium_id.is_(1), 
                                Seat.seat_type.is_not('empty'))).count()
        assert (str(seats) + ' seats').encode('utf-8') in response.data



''' HOME '''
# NOTE: Home page will also be tested inside tests where employee makes changes. 
#@pytest.mark.skip
def test_home(client_users):
    login_employee(client_users)

    response = client_users.get(url_for('employees.home'))
    assert response.status_code == 200
    assert b'You have made no changes to the database.' in response.data

