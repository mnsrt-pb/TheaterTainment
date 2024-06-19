''' Test Employees: Home, auditoriums, purchase info, and tickets '''

from flask import url_for
from tests.utils import login_employee
from theatert.models import Auditorium, Seat

import pytest
import os


if os.environ.get('SKIP_TEST_EMPLOYEE', 'false').lower() == 'true':
    pytestmark = pytest.mark.skip("Skipping tests in test_employee.py")


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



''' HOME '''
# NOTE: Home page will also be tested inside tests where employee makes changes. 
#@pytest.mark.skip
def test_home(client_users):
    login_employee(client_users)

    response = client_users.get(url_for('employees.home'))
    assert response.status_code == 200
    assert b'You have made no changes to the database.' in response.data



