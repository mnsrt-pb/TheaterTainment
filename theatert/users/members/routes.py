from datetime import datetime
from flask import abort, Blueprint, flash, render_template, redirect, request, session, url_for
from flask_login import current_user, logout_user
from secrets import token_urlsafe
from sqlalchemy import collate
from theatert import db, bcrypt
from theatert.users.members.forms import AccountInfoForm, DefaultPaymentForm, DeleteDefaultPayemnt, \
    EmailForm, MemberCheckoutForm, MemberCheckoutForm2, RegistrationForm, PasswordForm
from theatert.models import Card, Cards, Member, Movie, Purchase, Purchased_Ticket, Screening, Seat, Ticket, Watchlist
from theatert.users.utils import guest, login_required, clear_session
from werkzeug.datastructures import MultiDict

import calendar


members = Blueprint('members', __name__, url_prefix='/member')


@members.route('/<int:m_id>/add_watchlist')
@login_required(role='MEMBER')
def add_watchlist(m_id):
    ''' Add movie to member's watchlist '''
    clear_session()

    movie = Movie.query.filter_by(id = m_id, deleted=False, active=True).first_or_404()
    added = Watchlist.query.filter_by(member_id = current_user.id, movie_id = m_id).first()
    
    if not added:
        item = Watchlist(
                    member_id = current_user.id,
                    movie_id = m_id
                    )
        db.session.add(item)
        flash(f'<b><i>{movie.title}</i></b> added to Watch List', 'custom')
        db.session.commit()
    
    return redirect(request.referrer)


@members.route('/checkout', methods=['GET', 'POST'])
@login_required(role='MEMBER')
def checkout():
    ''' Checkout page'''

    form = MemberCheckoutForm()
    form2 = MemberCheckoutForm2()

    form_data = session.get('form_data')
    form2_data = session.get('form2_data')
    form_data_login = session.get('form_data_login')

    if form2_data:
        form2 = MemberCheckoutForm2(MultiDict(form2_data))

        screening = Screening.query \
            .filter(Screening.id.is_(form2.screening_id.data)) \
            .first_or_404()
        
        if screening.start_datetime < datetime.now():
            abort(404)
        
        seats = [ Seat.query.filter_by(auditorium_id = screening.auditorium.id, id = x).first()
            for x in form2.seats_selected.data.split(',') ]
        
        tickets = { 'adult': int(form2.adult_tickets.data), 
                    'child': int(form2.child_tickets.data), 
                    'senior': int(form2.senior_tickets.data) }
        
        form2.validate()

    elif form_data:
        form = MemberCheckoutForm(MultiDict(form_data))
        screening = Screening.query \
            .filter(Screening.id.is_(form.screening_id.data)) \
            .first_or_404()
        
        if screening.start_datetime < datetime.now():
            abort(404)
        
        seats = [ Seat.query.filter_by(auditorium_id = screening.auditorium.id, id = x).first()
            for x in form.seats_selected.data.split(',') ]
        
        tickets = { 'adult': int(form.adult_tickets.data), 
                    'child': int(form.child_tickets.data), 
                    'senior': int(form.senior_tickets.data) }

        form.validate()

    elif form_data_login:
        screening = Screening.query \
            .filter(Screening.id.is_(form_data_login['screening_id'])) \
            .first_or_404()
        
        if screening.start_datetime < datetime.now():
            abort(404)

        seats = [ Seat.query.filter_by(auditorium_id = screening.auditorium.id, id = x).first()
            for x in form_data_login['seats_selected'].split(',') ]

        tickets = { 'adult': int(form_data_login['adult_tickets']), 
                    'child': int(form_data_login['child_tickets']), 
                    'senior': int(form_data_login['senior_tickets']) }

        form.screening_id.data = screening.id
        form.seats_selected.data = form_data_login['seats_selected']
        form.adult_tickets.data = form_data_login['adult_tickets']
        form.child_tickets.data = form_data_login['child_tickets']
        form.senior_tickets.data = form_data_login['senior_tickets']
        
        form2.screening_id.data = screening.id
        form2.seats_selected.data = form_data_login['seats_selected']
        form2.adult_tickets.data = form_data_login['adult_tickets']
        form2.child_tickets.data = form_data_login['child_tickets']
        form2.senior_tickets.data = form_data_login['senior_tickets']

    else:
        screening = Screening.query \
            .filter(Screening.id.is_(request.form.get('screening_id'))) \
            .first_or_404()
        
        if screening.start_datetime < datetime.now():
            abort(404)

        seats = [ Seat.query.filter_by(auditorium_id = screening.auditorium.id, id = x).first()
            for x in request.form.get('seats_selected').split(',') ]

        tickets = { 'adult': int(request.form.get('adult_tickets')), 
                    'child': int(request.form.get('child_tickets')), 
                    'senior': int(request.form.get('senior_tickets')) }

        form.screening_id.data = screening.id
        form.seats_selected.data = request.form.get('seats_selected')
        form.adult_tickets.data = request.form.get('adult_tickets')
        form.child_tickets.data = request.form.get('child_tickets')
        form.senior_tickets.data = request.form.get('senior_tickets')

        form2.screening_id.data = screening.id
        form2.seats_selected.data = request.form.get('seats_selected')
        form2.adult_tickets.data = request.form.get('adult_tickets')
        form2.child_tickets.data = request.form.get('child_tickets')
        form2.senior_tickets.data = request.form.get('senior_tickets')

    saved_data = Cards.query.filter_by(member_id=current_user.id, active=True).first()
    saved_card = Card.query.filter_by(id=saved_data.card_id).first() if saved_data else None

    return render_template('member/checkout.html', screening=screening, seats=seats, tickets=tickets, form=form, form2=form2, saved_card=saved_card)


@members.route('/checkout-validate', methods=['POST'])
@login_required(role='MEMBER')
def checkout_validate():
    ''' Validate checkout data '''

    form = MemberCheckoutForm()
    form2 = MemberCheckoutForm2()

    if session.get('form_data_login'):
            session.pop('form_data_login')
    if 'form1' in request.form:
        if form.validate_on_submit():
            screening = Screening.query \
                .filter(Screening.id.is_(form.screening_id.data)) \
                .first_or_404()
            
            if screening.start_datetime < datetime.now():
                abort(404)

            if session.get('form_data') : 
                # saved data form previously submitted form because current submission failed 
                # (screening_id, adult_tickets, etc.)
                session.pop('form_data')

            day = str(calendar.monthrange(form.exp_year.data, form.exp_month.data)[1])
            exp_date = datetime.strptime(str(form.exp_month.data) + '/' + day + '/' + str(form.exp_year.data), '%m/%d/%Y').date()

            card = Card.query.filter_by(card_num = form.card_number.data, member = True).first()

            if card:
                if not (bcrypt.check_password_hash(card.sec_code, form.sec_code.data) \
                    and card.exp_date == exp_date and card.card_type == form.card_type.data \
                    and card.billing_zip == int(form.zip_code.data)): # Data does not match
                
                    flash('Invalid card.', 'danger')
                    session['form_data'] = request.form
                    return redirect(url_for('members.checkout'))

            else:
                card = Card.query.filter_by(card_num = form.card_number.data, member = False).first()
                
                # Cards with the same card number's must have the same data (sec_code, exp_date, and billing_zip)
                # A card can be saved in the Card table at most twice (once for member's and once for guests)
                if card:
                    if not (bcrypt.check_password_hash(card.sec_code, form.sec_code.data) \
                        and card.exp_date == exp_date and card.card_type == form.card_type.data \
                        and card.billing_zip == int(form.zip_code.data)):

                        flash('Invalid card.', 'danger')
                        session['form_data'] = request.form
                        return redirect(url_for('members.checkout'))
                
                card = Card(
                    card_num = form.card_number.data,
                    sec_code = bcrypt.generate_password_hash(form.sec_code.data).decode('utf-8'),
                    exp_date = exp_date,
                    card_type = form.card_type.data,
                    billing_zip = form.zip_code.data,
                    member = True
                )
                db.session.add(card)

            if form.save.data:
                cards = Cards.query.filter_by(card_id = card.id, member_id=current_user.id).first()

                if cards and cards.active:
                    if not cards.active:
                        cards.active = True
                else:
                    cards = Cards(
                        card_id = card.id,
                        member_id = current_user.id
                    )
                    db.session.add(cards)

            seat_ids = list(form.seats_selected.data.split(","))
            tickets, ticket_ids = '', []

            for s in seat_ids:
                ticket = Ticket.query \
                    .filter( db.and_(Ticket.seat_id.is_(s),
                                     Ticket.screening_id.is_(form.screening_id.data))).first()
                
                tickets += ticket.seat.row_name + str(ticket.seat.col) + ' '
                purchased_ticket = Purchased_Ticket.query.filter_by(ticket_id = ticket.id).first()
                
                if purchased_ticket:
                    flash(ticket.seat.row_name + str(ticket.seat.col) + ' is unavailable.', 'danger')
                    return redirect(url_for('users.ticket_seat_map', showtime_id = form.screening_id.data))
                
                ticket_ids.append(ticket.id)

            db.session.commit() # commit card data
            purchase = Purchase(
                email = current_user.email,
                member_id = current_user.id,
                adult_tickets = form.adult_tickets.data,
                child_tickets = form.child_tickets.data,
                senior_tickets = form.senior_tickets.data,
                card_id = card.id,
                confirmation = token_urlsafe(12)
            )
            db.session.add(purchase)
            db.session.commit()

            for t in ticket_ids:
                purchased_ticket = Purchased_Ticket(
                    ticket_id = t,
                    purchase_id = purchase.id
                )
                db.session.add(purchased_ticket)

            db.session.commit()
            return redirect(url_for('users.receipt', confirmation=purchase.confirmation))
        
        else:
            session['form_data'] = request.form
            return redirect(url_for('members.checkout'))
    else: 
        if form2.validate_on_submit():
            screening = Screening.query \
                .filter(Screening.id.is_(form2.screening_id.data)) \
                .first_or_404()
            
            if screening.start_datetime < datetime.now():
                abort(404)

            if session.get('form2_data'): 
                # saved data form previously submitted form because current submission failed 
                # (screening_id, adult_tickets, etc.)
                session.pop('form2_data')

            saved_data = Cards.query.filter_by(member_id=current_user.id, active=True).first_or_404()
            saved_card = Card.query.filter_by(id=saved_data.card_id).first() if saved_data else None

            if bcrypt.check_password_hash(saved_card.sec_code, form2.sec_code.data):
                seat_ids = list(form.seats_selected.data.split(","))
                tickets, ticket_ids = '', []

                for s in seat_ids:
                    ticket = Ticket.query \
                        .filter(db.and_(Ticket.seat_id.is_(s),
                                        Ticket.screening_id.is_(form.screening_id.data))).first()
                    
                    tickets += ticket.seat.row_name + str(ticket.seat.col) + ' '
                    purchased_ticket = Purchased_Ticket.query.filter_by(ticket_id = ticket.id).first()
                    
                    if purchased_ticket:
                        flash(ticket.seat.row_name + str(ticket.seat.col) + ' is unavailable.', 'danger')
                        return redirect(url_for('users.ticket_seat_map', showtime_id = form.screening_id.data)) 
                    ticket_ids.append(ticket.id)

                purchase = Purchase(
                    email = current_user.email,
                    member_id = current_user.id,
                    adult_tickets = form2.adult_tickets.data,
                    child_tickets = form2.child_tickets.data,
                    senior_tickets = form2.senior_tickets.data,
                    card_id = saved_card.id,
                    confirmation = token_urlsafe(12)
                )
                db.session.add(purchase)
                db.session.commit()

                for t in ticket_ids:
                    purchased_ticket = Purchased_Ticket(
                        ticket_id = t,
                        purchase_id = purchase.id
                    )
                    db.session.add(purchased_ticket)

                db.session.commit()
                return redirect(url_for('users.receipt', confirmation=purchase.confirmation))

            else:
                flash('Invalid data, transaction declined.', 'danger')
                session['form2_data'] = request.form
                return redirect(url_for('members.checkout'))

        else:
            session['form2_data'] = request.form
            return redirect(url_for('members.checkout'))


@members.route('/profile', methods=['GET', 'POST'])
@login_required(role='MEMBER')
def profile():
    ''' Member's profile page '''
    clear_session()

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
            flash('Your information has been updated!', 'custom')
            return redirect(url_for('members.profile'))

    elif 'email' in request.form:
        hidden1, hidden2, hidden3, hidden4, hidden5 = 'hidden', 'hidden', '', 'hidden', 'hidden'

        info_form.fname.data = current_user.fname
        info_form.lname.data = current_user.lname
        if current_user.dob:
            info_form.dob.data = current_user.dob.strftime('%m/%d')
        info_form.zip_code.data = current_user.zip_code
        info_form.phone.data = current_user.phone

        if email_form.validate_on_submit():
            current_user.email = email_form.email.data
            current_user.username = email_form.email.data
            db.session.commit()

            hidden1, hidden2, hidden3, hidden4, hidden5 = '', 'hidden', 'hidden', 'hidden', 'hidden'
            flash('Your email has been updated!', 'custom')
            return redirect(url_for('members.profile'))

    elif 'new_password' in request.form:
        hidden1, hidden2, hidden3, hidden4, hidden5 = 'hidden', 'hidden', 'hidden', '', 'hidden'

        info_form.fname.data = current_user.fname
        info_form.lname.data = current_user.lname
        if current_user.dob:
            info_form.dob.data = current_user.dob.strftime('%m/%d')
        info_form.zip_code.data = current_user.zip_code
        info_form.phone.data = current_user.phone

        email_form.email.data = current_user.email

        if password_form.validate_on_submit():
            current_user.password = bcrypt.generate_password_hash(password_form.new_password.data).decode('utf-8')
            db.session.commit()

            hidden1, hidden2, hidden3, hidden4, hidden5 = '', 'hidden', 'hidden', 'hidden', 'hidden'
            flash('Your password has been updated!', 'custom')
            return redirect(url_for('members.profile'))
        
    elif 'card_number' in request.form:
        hidden1, hidden2, hidden3, hidden4, hidden5 = 'hidden', 'hidden', 'hidden', 'hidden', ''

        info_form.fname.data = current_user.fname
        info_form.lname.data = current_user.lname
        if current_user.dob:
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
                        sec_code = bcrypt.generate_password_hash(payment_form.sec_code.data).decode('utf-8')
                    )
                db.session.add(card)
                db.session.commit()
                
            else:
                if card_member: 
                # Cards with the same card number's must have the same data (sec_code, exp_date, and billing_zip)
                # A card can be saved in the Card table at most twice (once for member's and once for guests)
                    if not (card_member.exp_date == exp_date and card_member.card_type == payment_form.card_type.data \
                        and card_member.billing_zip == int(payment_form.zip_code.data) 
                        and bcrypt.check_password_hash(card_member.sec_code, payment_form.sec_code.data)):
                        # Card exists but data does not match
                        flash('Invalid card.', 'danger')
                        return redirect(url_for('members.profile'))
                    else: 
                        card = card_member
                    
                else:
                    if not (card_guest.exp_date == exp_date and card_guest.card_type == payment_form.card_type.data \
                        and card_guest.billing_zip == int(payment_form.zip_code.data) 
                        and bcrypt.check_password_hash(card_guest.sec_code, payment_form.sec_code.data)): # Data does not match
                    
                        flash('Invalid card.', 'danger')
                        return redirect(url_for('members.profile'))
                    else:
                        card = Card(
                            card_num = payment_form.card_number.data,
                            exp_date = exp_date,
                            card_type = payment_form.card_type.data,
                            billing_zip = payment_form.zip_code.data,
                            sec_code = bcrypt.generate_password_hash(payment_form.sec_code.data).decode('utf-8')
                        )
                        db.session.add(card)
                        db.session.commit()

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

            flash('Default payment saved!', 'custom')
            return redirect(url_for('members.profile'))

    elif 'delete' in request.form:
        hidden1, hidden2, hidden3, hidden4, hidden5 = '', 'hidden', 'hidden', 'hidden', 'hidden'
        saved_data = Cards.query.filter_by(member_id=current_user.id, active=True).first_or_404()
        saved_data.active = False
        db.session.commit()

        flash('Default payment removed!', 'custom')
        return redirect(url_for('members.profile'))

    else:
        hidden1, hidden2, hidden3, hidden4, hidden5 = '', 'hidden', 'hidden', 'hidden', 'hidden'

        info_form.fname.data = current_user.fname
        info_form.lname.data = current_user.lname
        info_form.zip_code.data = current_user.zip_code
        info_form.phone.data = current_user.phone
        if current_user.dob:
            info_form.dob.data = current_user.dob.strftime('%m/%d')

        email_form.email.data = current_user.email
    
    saved_data = Cards.query.filter_by(member_id=current_user.id, active=True).first()
    saved_card = Card.query.filter_by(id=saved_data.card_id).first() if saved_data else None

    return render_template('member/profile.html', info_form=info_form, email_form=email_form, \
                           password_form=password_form, payment_form=payment_form, delete_default=delete_default, \
                           hidden1=hidden1, hidden2=hidden2, hidden3=hidden3, hidden4=hidden4, hidden5=hidden5, saved_card=saved_card)


@members.route('/purchases')
@login_required(role='MEMBER')
def purchases():
    ''' Display member's purchases '''
    clear_session()

    ps = Purchase.query.filter_by(member_id = current_user.id)

    purchases = {'past': {
                        'purchase': [],
                        'tickets': [],
                        'screenings': [],
                        'totals': []
                            },
                 'upcoming': {
                        'purchase':[],
                        'tickets': [],
                        'screenings': [],
                        'totals': []
                        }
                }

    for p in ps:
        t = Purchased_Ticket.query.filter(Purchased_Ticket.purchase_id.is_(p.id))
        
        s = Screening.query.filter(Screening.id.is_(t.first().ticket.screening_id)).first()
        
        if s.start_datetime < datetime.now():
            purchases['past']['purchase'].append(p)
            purchases['past']['tickets'].append(t)
            purchases['past']['screenings'].append(s)
            purchases['past']['totals'].append(t.count())
        else:
            purchases['upcoming']['purchase'].append(p)
            purchases['upcoming']['tickets'].append(t)
            purchases['upcoming']['screenings'].append(s)
            purchases['upcoming']['totals'].append(t.count())
    
    return render_template('/member/purchases.html', purchases=purchases)


@members.route('/register', methods=['GET', 'POST'])
@guest()
def register():
    ''' Register associate '''
    clear_session()

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

        flash('Your account has been created! You are now able to log in.', 'custom')
        logout_user()
        return redirect(url_for('users.member_login'))
    else:
        return render_template('member/register.html', form=form)


@members.route('/<int:m_id>/remove_watchlist')
@login_required(role='MEMBER')
def remove_watchlist(m_id):
    ''' Remove movie from member's watchlist '''
    clear_session()

    movie = Movie.query.filter_by(id = m_id, deleted=False).first_or_404()
    added = Watchlist.query.filter_by(member_id = current_user.id, movie_id = m_id).first()
    
    if added:
        remove = Watchlist.query.filter_by(id = added.id).first()
        db.session.delete(remove)
        db.session.commit()
        url = url_for('members.add_watchlist', m_id=movie.id)
        flash(f'<b><i>{movie.title}</i></b> removed from Watch List <a href="{url}" class=" ms-3 info fw-bold">UNDO</a>', 'custom')

    return redirect(request.referrer)


@members.route('/watchlist')
@login_required(role='MEMBER')
def watchlist():
    '''Member's Watchlist'''
    clear_session()
    
    watchlist = Watchlist.query.join(Movie).filter(Watchlist.member_id.is_(current_user.id))
    
    now_playing = watchlist.filter(
                db.and_(Movie.deleted.is_(False), Movie.active.is_(True), \
                db.ColumnOperators.__le__(Movie.release_date, (datetime.now()))))\
                .order_by(collate(Movie.title, 'NOCASE'))

    not_playing = watchlist.filter(
                db.and_(Movie.deleted.is_(False), Movie.active.is_(False),\
                db.ColumnOperators.__le__(Movie.release_date, (datetime.now()))))\
                .order_by(collate(Movie.title, 'NOCASE'))

    coming_soon = watchlist.filter(db.and_(Movie.deleted.is_(False), \
                db.ColumnOperators.__gt__(Movie.release_date, datetime.now())))\
                .order_by(collate(Movie.title, 'NOCASE'))

    return render_template('member/watchlist.html', now_playing=now_playing, not_playing=not_playing, coming_soon=coming_soon)

