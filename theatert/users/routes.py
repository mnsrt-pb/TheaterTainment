from flask import Blueprint, flash, render_template,  redirect, request, url_for
from flask_login import current_user, login_user, logout_user
from theatert import bcrypt
from theatert.models import Employee
from theatert.users.employees.forms import LoginForm
from theatert.users.utils import apology


users = Blueprint('users', __name__)


@users.route('/employee/login', methods=['GET', 'POST'])
def employee_login():
    '''Login employee'''

    if current_user.is_authenticated:
        return redirect(url_for('employees.employees.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Employee.query.filter_by(username=form.username.data).first()

        # Ensure username exists and password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            return redirect(next_page) if next_page else redirect(url_for('employees.home'))
        
        flash('Invalid Username or Password.', 'danger')

    return render_template('/employee/login.html', form=form)


@users.route('/logout')
def logout():
    '''Log user out'''

    logout_user()

    # Redirect user to login form 
    return apology('TODO', 'member/layout.html', 403)
