from flask import url_for
from flask_login import current_user
from theatert.config_test import showtime_data

def login_employee(user):
    data = dict( username='testuser', password='Valid*123')
    response = user.post(url_for('users.employee_login'), data=data, follow_redirects=True)
    assert response.status_code == 200

    
def login_member(user):
    data = dict( email='test@user.com', password='valid*123')
    response = user.post(url_for('users.member_login'), data=data, follow_redirects=True)
    assert response.status_code == 200


def logout(user):
    response = user.get(url_for('users.logout'), follow_redirects=True)
    assert response.status_code == 200


def showtime_tomorrow(user):
    ''' NOTE: tests that use this function will fail if test_add_showtime fails '''
    login_employee(user)
    current_id =  current_user.id

    response = user.post(url_for('employees.showtimes.add_showtime'), data=showtime_data, follow_redirects=True)
    assert response.status_code == 200

    logout(user)
    
    return response, current_id


