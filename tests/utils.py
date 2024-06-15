from flask import url_for


def login_employee(user):
    data = dict( username='testuser', password='Valid*123')
    response = user.post(url_for('users.employee_login'), data=data, follow_redirects=True)
    assert response.status_code == 200

    
def login_member(user):
    data = dict( email='test@user.com', password='valid*123')
    response = user.post(url_for('users.member_login'), data=data, follow_redirects=True)
    assert response.status_code == 200
