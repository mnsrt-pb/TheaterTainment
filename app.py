from cs50 import SQL
from datetime import datetime 
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session

from helpers import apology, member_login_required, staff_login_required, validate_password, date, check_password_hash, generate_password_hash, database_movies, search_movie, get_title, released


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL('sqlite:///database/theater.db')

# Employee Key: Required to create an employee account.
employee_key = 'ASDF123!!45'


@app.route('/activate', methods=['GET', 'POST'])
@staff_login_required
def activate():
    '''Activate a movie'''
    
    if request.method == 'POST':
        tmdb_id = request.form.get('m-id')

        # Query the database for movie (movie must not have been deleted)
        exists = db.execute('SELECT * FROM movies WHERE deleted = FALSE AND tmdb_id = ?;', tmdb_id)
        
        # Ensure movie exists in database
        if not exists:
            session['failure'] = True
            flash('Could not activate movie.')
            return redirect(url_for("all_movies"))
        
        else:
            if exists[0]['active']:
                session['failure'] = True
                flash('Movie is already active.')
                return redirect(url_for("all_movies"))


            if not released(tmdb_id):
                session['failure'] = True
                flash('Can only activate released movies.')
                return redirect(url_for("all_movies"))

            # Update movies's active status
            db.execute('UPDATE movies SET active = TRUE WHERE id = ?', exists[0]['id'])

            # Insert a new change to database
            db.execute('INSERT INTO staff_changes (staff_id, change, table_name, data_id, date_time) VALUES (?, ?, ?, ?, ?);', session['user_id'], 'activated', 'movies', exists[0]['id'], date())

            session['failure'] = False
            flash('Movie has been activated.')
            
    return redirect(url_for("all_movies"))


@app.route('/add-movie', methods=['GET', 'POST'])
@staff_login_required
def add_movie():
    '''Add movie to theater database'''
    if request.method == 'POST':
        title, year, tmdb_id = request.form.get('title'), request.form.get('year'), request.form.get('m-id')
        
        if not tmdb_id:
            # Ensure title was submitted
            if not title:
                return render_template('employee/add-movie.html', t_feedback='is-invalid', y_feedback='is-valid', form=True)

            # Query database for all movies
            movies = db.execute('SELECT tmdb_id FROM movies')

            return render_template('employee/add-movie.html', search_result=True, result=search_movie(title, year, movies))
        else:
            # Ensure movie is not in our database
            exists = db.execute('SELECT * FROM movies WHERE tmdb_id = ?', tmdb_id)
            if exists:
                # Movie is in database but flagged as 'deleted'
                if exists[0]['deleted']:
                    db.execute('UPDATE movies SET deleted = FALSE WHERE id = ?', exists[0]['id'])

                    session['failure'] = False
                    flash('Movie was added to our database')
                    return redirect(url_for("all_movies"))
                # Movie is in database
                else:
                    flash('Movie is already in our database')
                    session['failure'] = True
                    return redirect(url_for("all_movies"))
            
            # Insert a new movie to dabase
            db.execute('INSERT INTO movies (tmdb_id, title, active, deleted) values (?, ?, ?, ?);', tmdb_id, get_title(tmdb_id), False, False)

            # Query databse for movie's row id
            data_id = db.execute('SELECT id FROM movies WHERE tmdb_id = ?', tmdb_id)[0]['id']
            
            # Insert a new change to database
            db.execute('INSERT INTO staff_changes (staff_id, change, table_name, data_id, date_time) VALUES (?, ?, ?, ?, ?);', session['user_id'], 'added', 'movies', data_id, date())
            
            session['failure'] = False
            flash('Movie was added to our database')
            return redirect(url_for("all_movies"))
    else:
        return render_template('employee/add-movie.html', form=True)


@app.route('/add-showtime', methods=['GET', 'POST'])
@staff_login_required
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
@staff_login_required
def all_movies():
    '''Display all movies in theater database'''

    # Query database for all movies
    movies = db.execute('SELECT * FROM movies WHERE deleted = FALSE ORDER BY title;')
    active = db.execute('SELECT tmdb_id, title FROM movies WHERE deleted = FALSE AND active = TRUE ORDER BY title;')
    inactive = db.execute('SELECT tmdb_id, title FROM movies WHERE deleted = FALSE AND active = FALSE ORDER BY title;')

    return render_template('other/movies.html', ext="employee/layout.html", title="All Movies", info=database_movies(movies), active=active, inactive=inactive, failure=session.get('failure'))


@app.route('/all-showtimes')
@staff_login_required
def all_showtimes():
    '''Display showtimes'''

    return apology('TODO', 'employee/layout.html', 403)


@app.route('/auditoriums')
@staff_login_required
def auditoriums():
    '''Display auditoriums'''

    return apology('TODO', 'employee/layout.html', 403)


@app.route('/coming-soon')
def coming_soon():
    '''Display movies that have not been released'''

    # Query database for movies
    movies = db.execute('SELECT * FROM movies WHERE deleted = FALSE AND active = FALSE ORDER BY title;')

    if session.get('user_id') is None:
        return apology('TODO', 'member/layout.html', 403)
    
    elif session['user_type'] == 'staff':
        return render_template('other/movies.html', ext="employee/layout.html", title="Coming Soon", info=database_movies(movies, True))
    
    else:
        return apology('TODO', 'member/layout.html', 403)
    

@app.route('/e-login', methods=['GET', 'POST'])
def employee_login():
    '''Login employee'''
    
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':

        # Ensure username was submitted
        if not request.form.get('username'):
            flash('The Username field is required.')
            return render_template('employee/login.html', failure=True)

        # Ensure password was submitted
        elif not request.form.get('password'):
            flash('The Password field is required.')
            return render_template('employee/login.html', failure=True)

        # Query database for username
        rows = db.execute('SELECT * FROM staff WHERE username = ?', request.form.get('username'))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]['hash'], request.form.get('password')):
            flash('Invalid Username or Password.')
            return render_template('employee/login.html', failure=True)

        # Remember which user has logged in
        session['user_id'] = rows[0]['id']
        session['user_type'] = 'staff'

        # Redirect user to home page
        return redirect('/')

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('employee/login.html')


@app.route('/e-register', methods=['GET', 'POST'])
def employee_register():
    '''Register associate'''

    # Forget any user id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        username, password, confirmation, e_key = (
            request.form.get('username'),
            request.form.get('password'),
            request.form.get('confirmation'),
            request.form.get('e-key')
        )

        # Ensure username was submitted
        if not username:
            flash('The Username field is required.')
            return render_template('employee/register.html', failure=True)

        # Ensure password was submitted
        elif not password:
            flash('The Password field is required.')
            return render_template('employee/register.html', failure=True)
        
        # Ensure password was submitted
        elif not e_key:
            flash('The Employee Key field is required.')
            return render_template('employee/register.html', failure=True)

        # Ensure passwords match
        elif password != confirmation:
            flash('The passwords you enter must match.')
            return render_template('employee/register.html', failure=True)
        
        # Ensure user is an employee
        elif employee_key != e_key:
            flash('Invalid Employee Key.')
            return render_template('employee/register.html', failure=True)
        
        # Ensure password requirements are met
        elif not validate_password(password):
            flash('Password must meet password requirements.')
            return render_template('employee/register.html', failure=True)

        # Query database for username
        rows = db.execute('SELECT * FROM staff WHERE username = ?', username)

        # Ensure username does not exist
        if len(rows) != 0:
            flash('Username already exists.')
            return render_template('employee/register.html', failure=True, link=True)

        # Insert a new user to database
        db.execute(
            'INSERT INTO staff (username, hash) VALUES (?, ?);',
            username,
            generate_password_hash(password)
        )
        flash('Registered!')

        # Query database for user id
        row = db.execute('SELECT id FROM staff WHERE username = ?', username)

        # Log in user
        session['user_id'] = row[0]['id']
        session['user_type'] = 'employee'

        # Redirect user to home page
        return redirect('/')

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('employee/register.html')


@app.route('/inactivate', methods=['GET', 'POST'])
@staff_login_required
def inactivate():
    '''Inactivate a movie'''
    
    if request.method == 'POST':
        tmdb_id = request.form.get('m-id')

        # Query the database for movie (movie must not have been deleted)
        exists = db.execute('SELECT * FROM movies WHERE deleted = FALSE AND tmdb_id = ?;', tmdb_id)
        
        # Ensure movie exists in database
        if not exists:
            session['failure'] = True
            flash('Could not inactivate movie.')
            return redirect(url_for("all_movies"))
        
        elif not exists[0]['active']:
            session['failure'] = True
            flash('Movie is already inactive.')
            return redirect(url_for("all_movies"))

        # Update movies's active status
        db.execute('UPDATE movies SET active = FALSE WHERE id = ?', exists[0]['id'])

        # Insert a new change to database
        db.execute('INSERT INTO staff_changes (staff_id, change, table_name, data_id, date_time) VALUES (?, ?, ?, ?, ?);', session['user_id'], 'inactivated', 'movies', exists[0]['id'], date())

        session['failure'] = False
        flash('Movie has been inactivated.')
            
    return redirect(url_for("all_movies"))


@app.route('/')
def index():
    '''Show home page'''

    if session.get('user_id') is None:
        return apology('TODO', 'member/layout.html', 403)
    elif session['user_type'] == 'staff':
        rows = db.execute('SELECT * FROM staff_changes WHERE staff_id = ? ORDER BY date_time DESC;', session['user_id'])
        
        changes = []
        for c in rows:
            if c['table_name'] == 'movies':
                temp = {k:v for k,v in c.items() if k in ['change', 'table_name', 'date_time']}
                temp['item'] = db.execute('SELECT title FROM movies WHERE id = ?;', c['data_id'])[0]['title']
                changes.append(temp)

        return render_template('employee/employee.html', changes=changes)
    else: # session['user_type'] == 'member'
        return apology('TODO', 'member/layout.html', 403)


@app.route('/logout')
def logout():
    '''Log user out'''

    # Forget any user_id
    session.clear()

    # Redirect user to login form 
    return redirect('/')


@app.route('/m-login', methods=['GET', 'POST'])
def member_login():
    '''Log user in'''

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        # Ensure username was submitted
        if not request.form.get('username'):
            return apology('must provide username', 'employee/layout.html', 403)

        # Ensure password was submitted
        elif not request.form.get('password'):
            return apology('must provide password', 'employee/layout.html', 403)

        # Query database for username
        rows = db.execute(
            'SELECT * FROM users WHERE username = ?', request.form.get('username')
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]['hash'], request.form.get('password')
        ):
            return apology('invalid username and/or password', 'employee/layout.html', 403)

        # Remember which user has logged in
        session['user_id'] = rows[0]['id']
        session['user_type'] = 'member'
        session['failure'] = False

        # Redirect user to home page
        return redirect('/')

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('member/login.html')


@app.route('/m-register', methods=['GET', 'POST'])
def member_register():
    '''Register user'''

    # Forget any user_id
    session.clear()
    return render_template('member/register.html')


@app.route('/movies')
def movies():
    '''Display available movies'''

    return apology('TODO', 'member/layout.html', 403)


@app.route('/now-playing')
def now_playing():
    '''Display movies that are now playing'''

    if session.get('user_id') is None:
        return apology('TODO', 'member/layout.html', 403)
    
    elif session['user_type'] == 'staff':
        # Query database for movies that are now playing
        movies = db.execute('SELECT * FROM movies WHERE deleted = FALSE AND active = TRUE ORDER BY title')

        return render_template('other/movies.html', ext="employee/layout.html", title="Now Playing", info=database_movies(movies))
    
    else:
        return apology('TODO', 'member/layout.html', 403)


@app.route('/past-showtimes')
@staff_login_required
def past_showtimes():
    '''Display available showtimes'''

    return apology('TODO', 'employee/layout.html', 403)


@app.route('/showtimes')
def showtimes():
    '''Display available showtimes'''

    return apology('TODO', 'member/layout.html', 403)


@app.route('/showtimes-now')
@staff_login_required
def showtimes_now():
    '''Display available showtimes'''

    return apology('TODO', 'employee/layout.html', 403)


@app.route('/tickets')
@staff_login_required
def tickets():
    '''Display tickets data'''

    return apology('TODO', 'employee/layout.html', 403)

