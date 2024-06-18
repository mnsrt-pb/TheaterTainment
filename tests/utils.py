from datetime import datetime, timedelta
from flask import url_for


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

    # Showtime
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    data = dict( 
        m_id = 1,
        a_id = 4,
        date_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0),
        adult_price = 12.5,
        child_price = 10.5,
        senior_price = 9
    )
    response = user.post(url_for('employees.showtimes.add_showtime'), data=data, follow_redirects=True)
    assert response.status_code == 200

    logout(user)


