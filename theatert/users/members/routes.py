from datetime import datetime
from flask import Blueprint, flash, render_template,  redirect, request, url_for
from flask_login import current_user
from theatert import db, bcrypt
from theatert.users.members.forms import RegistrationForm, AccountInfoForm, EmailForm, PasswordForm, DefaultPaymentForm, DeleteDefaultPayemnt
from theatert.models import Member, Card, Cards
from theatert.users.utils import apology, login_required

import calendar


members = Blueprint('members', __name__, url_prefix='/member')


@members.route('/profile', methods=['GET', 'POST'])
@login_required(role='MEMBER')
def profile():
    info_form = AccountInfoForm()
    email_form = EmailForm()
    password_form = PasswordForm()
    payment_form = DefaultPaymentForm()
    delete_default = DeleteDefaultPayemnt()

    if 'fname' in request.form:
        hidden1, hidden2, hidden3, hidden4, hidden5 = 'hidden', '', 'hidden', 'hidden', 'hidden'
        email_form.email.data = current_user.email

        if info_form.validate_on_submit():
            current_user.fname = info_form.fname.data
            current_user.lname = info_form.lname.data
            current_user.phone = info_form.phone.data
            current_user.zip_code = info_form.zip_code.data

            if info_form.dob.data:
                current_user.dob = datetime.strptime(info_form.dob.data, '%m/%d').date()
            db.session.commit()

            hidden1, hidden2, hidden3, hidden4, hidden5 = '', 'hidden', 'hidden', 'hidden', 'hidden'
            flash('Your information has been updated!', 'success')
            return redirect(url_for('members.profile'))

    elif 'email' in request.form:
        hidden1, hidden2, hidden3, hidden4, hidden5 = 'hidden', 'hidden', '', 'hidden', 'hidden'

        info_form.fname.data = current_user.fname
        info_form.lname.data = current_user.lname
        info_form.dob.data = current_user.dob.strftime('%m/%d')
        info_form.zip_code.data = current_user.zip_code
        info_form.phone.data = current_user.phone

        if email_form.validate_on_submit():
            current_user.email = email_form.email.data
            current_user.username = email_form.email.data
            db.session.commit()

            hidden1, hidden2, hidden3, hidden4, hidden5 = '', 'hidden', 'hidden', 'hidden', 'hidden'
            flash('Your email has been updated!', 'success')
            return redirect(url_for('members.profile'))

    elif 'new_password' in request.form:
        hidden1, hidden2, hidden3, hidden4, hidden5 = 'hidden', 'hidden', 'hidden', '', 'hidden'

        info_form.fname.data = current_user.fname
        info_form.lname.data = current_user.lname
        info_form.dob.data = current_user.dob.strftime('%m/%d')
        info_form.zip_code.data = current_user.zip_code
        info_form.phone.data = current_user.phone

        email_form.email.data = current_user.email

        if password_form.validate_on_submit():
            current_user.password = bcrypt.generate_password_hash(password_form.new_password.data).decode('utf-8')
            db.session.commit()

            hidden1, hidden2, hidden3, hidden4, hidden5 = '', 'hidden', 'hidden', 'hidden', 'hidden'
            flash('Your password has been updated!', 'success')
            return redirect(url_for('members.profile'))

    elif 'card_number' in request.form:
        hidden1, hidden2, hidden3, hidden4, hidden5 = 'hidden', 'hidden', 'hidden', 'hidden', ''

        info_form.fname.data = current_user.fname
        info_form.lname.data = current_user.lname
        info_form.dob.data = current_user.dob.strftime('%m/%d')
        info_form.zip_code.data = current_user.zip_code
        info_form.phone.data = current_user.phone

        email_form.email.data = current_user.email

        if payment_form.validate_on_submit():
            day = str(calendar.monthrange(payment_form.exp_year.data, payment_form.exp_month.data)[1])
            exp_date = datetime.strptime(str(payment_form.exp_month.data) + '/' + day + '/' + str(payment_form.exp_year.data), '%m/%d/%Y').date()

            card_guest = Card.query.filter_by(card_num = payment_form.card_number.data, member = False).first()
            card_member = Card.query.filter_by(card_num = payment_form.card_number.data, member = True).first()

            if not card_guest and not card_member:
                card = Card(
                        card_num = payment_form.card_number.data,
                        exp_date = exp_date,
                        card_type = payment_form.card_type.data,
                        billing_zip = payment_form.zip_code.data,
                        sec_code = payment_form.sec_code.data,
                    )
                db.session.add(card)
                
            else:
                if card_member: 
                # Cards with the same card number's must have the same data (sec_code, exp_date, and billing_zip)
                # A card can be saved in the Card table at most twice (once for member's and once for guests)
                    if not (card_member.exp_date == exp_date and card_member.card_type == payment_form.card_type.data \
                        and card_member.billing_zip == int(payment_form.zip_code.data) and card_member.sec_code == int(payment_form.sec_code.data)):
                        # Card exists but data does not match
                        flash('Invalid card.', 'danger')
                        return redirect(url_for('members.profile'))
                    else: 
                        card = card_member
                    
                else:
                    if not (card_guest.exp_date == exp_date and card_guest.card_type == payment_form.card_type.data \
                        and card_guest.billing_zip == int(payment_form.zip_code.data) and card_guest.sec_code == int(payment_form.sec_code.data)): # Data does not match
                    
                        flash('Invalid card.', 'danger')
                        return redirect(url_for('members.profile'))
                    else:
                        card = Card(
                            card_num = payment_form.card_number.data,
                            exp_date = exp_date,
                            card_type = payment_form.card_type.data,
                            billing_zip = payment_form.zip_code.data,
                            sec_code = payment_form.sec_code.data,
                        )
                        db.session.add(card)

            cards = Cards.query.filter_by(card_id = card.id, member_id=current_user.id).first()

            if cards:
                if not cards.active:
                    cards.active = True

            else:
                cards = Cards(
                    card_id = card.id,
                    member_id = current_user.id
                )
                db.session.add(cards)
            db.session.commit()

            flash('Default Payment Saved!', 'success')
            return redirect(url_for('members.profile'))

    elif 'delete' in request.form:
        hidden1, hidden2, hidden3, hidden4, hidden5 = '', 'hidden', 'hidden', 'hidden', 'hidden'
        saved_data = Cards.query.filter_by(member_id=current_user.id, active=True).first()
        saved_data.active = False
        db.session.commit()

        flash('Saved Card Removed!', 'success')
        return redirect(url_for('members.profile'))

    else:
        hidden1, hidden2, hidden3, hidden4, hidden5 = '', 'hidden', 'hidden', 'hidden', 'hidden'

        info_form.fname.data = current_user.fname
        info_form.lname.data = current_user.lname
        info_form.dob.data = current_user.dob.strftime('%m/%d')
        info_form.zip_code.data = current_user.zip_code
        info_form.phone.data = current_user.phone

        email_form.email.data = current_user.email
    
    saved_data = Cards.query.filter_by(member_id=current_user.id, active=True).first()

    if saved_data:
        saved_card = Card.query.filter_by(id=saved_data.card_id).first()
    else:
        saved_card = None

    return render_template('member/profile.html', info_form=info_form, email_form=email_form, \
                           password_form=password_form, payment_form=payment_form, delete_default=delete_default, \
                           hidden1=hidden1, hidden2=hidden2, hidden3=hidden3, hidden4=hidden4, hidden5=hidden5, saved_card=saved_card)

@members.route('/register', methods=['GET', 'POST'])
def register():
    '''Register associate'''

    # FIXME: add members.home
    if current_user.is_authenticated:
        if current_user.role == 'EMPLOYEE':
            return redirect(url_for('employees.home'))
        return redirect(url_for('users.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Insert a new user to database
        user = Member(
            username = form.email.data,
            password = bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
            email = form.email.data,
            fname = form.fname.data,
            lname = form.lname.data,
            phone = form.phone.data,
            zip_code = form.zip_code.data            
        )

        db.session.add(user)
        db.session.commit()

        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('users.member_login'))
    else:
        return render_template('member/register.html', form=form)

