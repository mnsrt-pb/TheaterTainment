from flask import flash, render_template,  redirect, request, url_for
from flask_login import current_user, login_user, logout_user

from theatert import app, db_cs50, db, bcrypt
from theatert.forms import RegistrationForm, LoginForm
from theatert.models import Employee, Member, Change
from theatert.helpers import (apology, database_movies, 
                    date, get_title, 
                    login_required, 
                    released, search_movie)


@app.route('/activate', methods=['GET', 'POST'])
@login_required(role="EMPLOYEE")
def activate():
    '''Activate a movie'''
    
    if request.method == 'POST':
        id = request.form.get('m-id')

        # Query the database for movie (movie must not have been deleted)
        exists = db_cs50.execute('SELECT * FROM movies WHERE deleted = FALSE AND id = ?;', id)
        
        # Ensure movie exists in database
        if not exists:
            flash('Could not activate movie.', 'danger')
            return redirect(url_for("all_movies"))
        
        else:
            if exists[0]['active']:
                flash('Movie is already active.', 'danger')
                return redirect(url_for("all_movies"))


            if not released(id):
                flash('Can only activate released movies.', 'danger')
                return redirect(url_for("all_movies"))

            # Update movies's active status
            db_cs50.execute('UPDATE movies SET active = TRUE WHERE id = ?', exists[0]['id'])

            # Insert a new change to database
            # db_cs50.execute('INSERT INTO staff_changes (staff_id, change, table_name, data_id, date_time) VALUES (?, ?, ?, ?, ?);', session['user_id'], 'activated', 'movies', exists[0]['id'], date())

            flash('Movie has been activated.', 'success')
            
    return redirect(url_for("all_movies"))


@app.route('/add-movie', methods=['GET', 'POST'])
@login_required(role="EMPLOYEE")
def add_movie():
    '''Add movie to theater database'''
    if request.method == 'POST':
        title, year, id = request.form.get('title'), request.form.get('year'), request.form.get('m-id')
        
        if not id:
            # Ensure title was submitted
            if not title:
                return render_template('employee/add-movie.html', t_feedb_cs50ack='is-invalid', y_feedb_cs50ack='is-valid', form=True)

            # Query database for all movies
            movies = db_cs50.execute('SELECT id FROM movies')

            return render_template('employee/add-movie.html', search_result=True, result=search_movie(title, year, movies))
        else:
            # Ensure movie is not in our database
            exists = db_cs50.execute('SELECT * FROM movies WHERE id = ?', id)
            if exists:
                # Movie is in database but flagged as 'deleted'
                if exists[0]['deleted']:
                    db_cs50.execute('UPDATE movies SET deleted = FALSE WHERE id = ?', exists[0]['id'])

                    flash('Movie was added to our database', 'success')
                    return redirect(url_for("all_movies"))
                # Movie is in database
                else:
                    flash('Movie is already in our database', 'danger')
                    return redirect(url_for("all_movies"))
            
            # Insert a new movie to dabase
            db_cs50.execute('INSERT INTO movies (id, title, active, deleted) values (?, ?, ?, ?);', id, get_title(id), False, False)

            # Query databse for movie's row id
            data_id = db_cs50.execute('SELECT id FROM movies WHERE id = ?', id)[0]['id']
            
            # Insert a new change to database
            # db_cs50.execute('INSERT INTO staff_changes (staff_id, change, table_name, data_id, date_time) VALUES (?, ?, ?, ?, ?);', session['user_id'], 'added', 'movies', data_id, date())
            
            flash('Movie was added to our database', 'success')
            return redirect(url_for("all_movies"))
    else:
        return render_template('employee/add-movie.html', form=True)


@app.route('/add-showtime', methods=['GET', 'POST'])
@login_required(role="EMPLOYEE")
def add_showtime():
    '''Assign showtimes to movies'''

    return apology('TODO', 'employee/layout.html', 403)


@app.after_request
def after_request(response):
    '''Ensure responses aren't cached'''
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = 0
    response.headers['Pragma'] = 'no-cache'
    return response


@app.route('/all-movies')
@login_required(role="EMPLOYEE")
def all_movies():
    '''Display all movies in theater database'''

    # Query database for all movies
    movies = db_cs50.execute('SELECT * FROM movies WHERE deleted = FALSE ORDER BY title;')
    active = db_cs50.execute('SELECT id, title FROM movies WHERE deleted = FALSE AND active = TRUE ORDER BY title;')
    inactive = db_cs50.execute('SELECT id, title FROM movies WHERE deleted = FALSE AND active = FALSE ORDER BY title;')

    return render_template('other/movies.html', ext="employee/layout.html", title="All Movies", info=database_movies(movies), active=active, inactive=inactive)


@app.route('/all-showtimes')
@login_required(role="EMPLOYEE")
def all_showtimes():
    '''Display showtimes'''

    return apology('TODO', 'employee/layout.html', 403)


@app.route('/auditoriums')
@login_required(role="EMPLOYEE")
def auditoriums():
    '''Display auditoriums'''

    return apology('TODO', 'employee/layout.html', 403)


@app.route('/coming-soon')
def coming_soon():
    '''Display movies that have not been released'''

    # Query database for movies
    movies = db_cs50.execute('SELECT * FROM movies WHERE deleted = FALSE AND active = FALSE ORDER BY title;')

    return render_template('other/movies.html', ext="employee/layout.html", title="Coming Soon", info=database_movies(movies, True))
    

@app.route('/inactivate', methods=['GET', 'POST'])
@login_required(role="EMPLOYEE")
def inactivate():
    '''Inactivate a movie'''
    
    if request.method == 'POST':
        id = request.form.get('m-id')

        # Query the database for movie (movie must not have been deleted)
        exists = db_cs50.execute('SELECT * FROM movies WHERE deleted = FALSE AND id = ?;', id)
        
        # Ensure movie exists in database
        if not exists:
            flash('Could not inactivate movie.', 'danger')
            return redirect(url_for("all_movies"))
        
        elif not exists[0]['active']:
            flash('Movie is already inactive.', 'danger')
            return redirect(url_for("all_movies"))

        # Update movies's active status
        db_cs50.execute('UPDATE movies SET active = FALSE WHERE id = ?', exists[0]['id'])

        # Insert a new change to database
        # db_cs50.execute('INSERT INTO staff_changes (staff_id, change, table_name, data_id, date_time) VALUES (?, ?, ?, ?, ?);', session['user_id'], 'inactivated', 'movies', exists[0]['id'], date())

        flash('Movie has been inactivated.', 'success')
            
    return redirect(url_for("all_movies"))


@app.route('/')
def home():
    '''Show home page'''
    
    if not current_user.is_authenticated:
            return apology('TODO', 'member/layout.html', 403) 
    #     rows = db_cs50.execute('SELECT * FROM staff_changes WHERE staff_id = ? ORDER BY date_time DESC;', session['user_id'])
        
    #     changes = []
    #     for c in rows:
    #         if c['table_name'] == 'movies':
    #             temp = {k:v for k,v in c.items() if k in ['change', 'table_name', 'date_time']}
    #             temp['item'] = db_cs50.execute('SELECT title FROM movies WHERE id = ?;', c['data_id'])[0]['title']
    #             changes.append(temp)

    return render_template('employee/employee.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Login employee'''

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Employee.query.filter_by(username=form.username.data).first()

        # Ensure username exists and password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            return redirect(next_page) if next_page else redirect(url_for('home'))
        
        flash('Invalid Username or Password.', 'danger')

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template('employee/login.html', form=form)


@app.route('/logout')
def logout():
    '''Log user out'''

    logout_user()

    # Redirect user to login form 
    return apology('TODO', 'member/layout.html', 403)


@app.route('/now-playing')
@login_required(role="EMPLOYEE")
def now_playing():
    '''Display movies that are now playing'''
    
    # Query database for movies that are now playing
    movies = db_cs50.execute('SELECT * FROM movies WHERE deleted = FALSE AND active = TRUE ORDER BY title')

    return render_template('other/movies.html', ext="employee/layout.html", title="Now Playing", info=database_movies(movies))
    

@app.route('/past-showtimes')
@login_required(role="EMPLOYEE")
def past_showtimes():
    '''Display available showtimes'''

    return apology('TODO', 'employee/layout.html', 403)


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''Register associate'''

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Insert a new user to database
        user = Employee(
            username = form.username.data,
            password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        )
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    else:
        return render_template('employee/register.html', form=form)


@app.route('/showtimes-now')
@login_required(role="EMPLOYEE")
def showtimes_now():
    '''Display available showtimes'''

    return apology('TODO', 'employee/layout.html', 403)


@app.route('/tickets')
@login_required(role="EMPLOYEE")
def tickets():
    '''Display tickets data'''

    return apology('TODO', 'employee/layout.html', 403)

