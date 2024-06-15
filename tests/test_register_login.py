''' Test register and login for Employees and Members '''

from flask import url_for
from flask_login import current_user
from theatert import employee_key
from tests.utils import login_employee, login_member
from theatert.models import Employee, Member
from theatert.users.employees.forms import RegistrationForm as EmployeeRegistrationForm
from theatert.users.members.forms import RegistrationForm as MemberRegistrationForm

import pytest
import os


if os.environ.get('SKIP_TEST_REGISTER_LOGIN', 'false').lower() == 'true':
    pytestmark = pytest.mark.skip("Skipping tests in test_register_login.py")


''' REGISTER '''
def test_register_pages(client):
    ''' Test if the registration pages load correctly. '''

    response = client.get(url_for('employees.register'))
    assert response.status_code == 200

    response = client.get(url_for('members.register'))
    assert response.status_code == 200
    

def test_employee_register(client):
    ''' Test successful registration. '''

    data = dict(
        username='testuser',
        password='Valid*123',
        confirm='Valid*123',
        key=employee_key
    )

    response = client.post(url_for('employees.register'), data=data , follow_redirects=True)
    assert response.status_code == 200

    with client.application.app_context():
        employee = Employee.query.first()
        assert employee.username == 'testuser'


def test_member_register(client):
    ''' Test successful registration. '''
    # NOTE: Phone number was taken from import phonenumbers' documentation

    data=dict(
        fname='Test',
        lname='User',
        email='test@user.com',
        confirm_email='test@user.com',
        password='valid*123',
        confirm='valid*123',
        phone='5107488230',
        zip_code='12345', 
        agree='True'
    )

    response = client.post(url_for('members.register'), data=data , follow_redirects=True)
    assert response.status_code == 200

    with client.application.app_context():
        member = Member.query.first()
        assert member.email == 'test@user.com'


@pytest.mark.parametrize('password', ['short', 'missingstuff'])
def test_employee_register_failure(client, password):
    '''Test registration with invalid data.'''

    data = dict(
        username='',
        password=password,
        confirm='different',
        key='incorrect'
    )

    form = EmployeeRegistrationForm(data=data)
    form.validate()

    assert 'username' in form.errors
    assert 'password' in form.errors
    assert 'confirm' in form.errors
    assert 'key' in form.errors

    response = client.post(url_for('members.register'), data=data, follow_redirects=True)
    assert response.status_code == 200

    with client.application.app_context():
        member = Member.query.first()
        assert member is None
    

@pytest.mark.parametrize('password', ['short', 'missingstuff'])
def test_member_register_failure(client, password):
    '''Test registration with invalid data.'''

    data=dict(
        fname='',
        lname='',
        email='invalid',
        confirm_email='different',
        password=password,
        confirm='different',
        phone='0',
        zip_code='0', 
        agree=''
    )

    form = MemberRegistrationForm(data=data)
    form.validate()

    assert 'fname' in form.errors
    assert 'lname' in form.errors
    assert 'email' in form.errors
    assert 'confirm_email' in form.errors
    assert 'password' in form.errors
    assert 'confirm' in form.errors
    assert 'phone' in form.errors
    assert 'zip_code' in form.errors
    assert 'agree' in form.errors

    response = client.post(url_for('members.register'), data=data, follow_redirects=True)
    assert response.status_code == 200

    with client.application.app_context():
        member = Member.query.first()
        assert member is None




''' LOGIN '''
def test_login_pages(client):
    ''' Test if the registration pages load correctly. '''
    response = client.get(url_for('users.employee_login'))
    assert response.status_code == 200

    response = client.get(url_for('users.member_login'))
    assert response.status_code == 200


def test_employee_login(client_employee):
    ''' Test successful login '''
    login_employee(client_employee)

    assert current_user.is_authenticated
    current_id =  current_user.id

    with client_employee.application.app_context():
        user = Employee.query.first()
        assert current_id == user.id
    

def test_member_login(client_member):
    ''' Test successful login '''
    login_member(client_member)

    assert current_user.is_authenticated
    current_id =  current_user.id

    with client_member.application.app_context():
        user = Member.query.first()
        assert current_id == user.id


@pytest.mark.parametrize('username, password', [
    ('wronguser', 'wrongpassword'),
    ('testuser', 'wrongpassword')])
def test_employee_login_failure(client_employee, username, password):
    ''' Test login with invalid data '''

    data = dict( username=username, password=password)
    response = client_employee.post(url_for('users.employee_login'), data=data, follow_redirects=True)
    
    assert response.status_code == 200
    assert not current_user.is_authenticated


@pytest.mark.parametrize('username, password', [
    ('wrong@user.com', 'wrongpassword'),
    ('test@user.com', 'wrongpassword')])
def test_member_login_failure(client_member, username, password):
    ''' Test login with invalid data '''

    data = dict( username=username, password=password)
    response = client_member.post(url_for('users.employee_login'), data=data, follow_redirects=True)
    
    assert response.status_code == 200
    assert not current_user.is_authenticated




''' REDIRECTED CORRECTLY IF NOT LOGGED IN '''
def test_employee_home_redirect(client_employee):
    ''' Redirect employees to login page '''

    response = client_employee.get(url_for('employees.home'))
    assert response.status_code == 302
    assert 'employee/login' in response.headers['Location']


def test_member_home_redirect(client_member):
    ''' Redirect employees to login page '''

    response = client_member.get(url_for('members.profile'))
    assert response.status_code == 302
    assert 'member/login' in response.headers['Location']

