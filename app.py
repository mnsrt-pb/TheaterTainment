from cs50 import SQL
from datetime import datetime 
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
# from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, member_login_required, staff_login_required, validate_password, check_password_hash, generate_password_hash, movie_info

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


# This should only be executed once to get our movies table started
def add_starting_data():
    db.execute('INSERT INTO movies (tmdb_id, title, active) VALUES (?, ?, ?);', 787699, 'Wonka', True)
    db.execute('INSERT INTO movies (tmdb_id, title, active) VALUES (?, ?, ?);', 572802, 'Aquaman and the Lost Kingdom', True)
    db.execute('INSERT INTO movies (tmdb_id, title, active) VALUES (?, ?, ?);', 695721, 'The Hunger Games: The Ballad of Songbirds & Snakes', True)
    db.execute('INSERT INTO movies (tmdb_id, title, active) VALUES (?, ?, ?);', 901362, 'Trolls Band Together', True)
    db.execute('INSERT INTO movies (tmdb_id, title, active) VALUES (?, ?, ?);', 507089, 'Five Nights at Freddy\'s', True)
    db.execute('INSERT INTO movies (tmdb_id, title, active) VALUES (?, ?, ?);', 940551, 'Migration', True)
    db.execute('INSERT INTO movies (tmdb_id, title, active) VALUES (?, ?, ?);', 748783, 'The Garfield Movie', False)

@app.route('/add-movie', methods=['GET', 'POST'])
@staff_login_required
def add_movie():
    '''Add movie to theater database'''
    if request.method == 'POST':
        title = request.form.get('title')
        
         # Ensure title was submitted
        if not title:
            return render_template('employee/add-movie.html', t_feedback='is-invalid', form=True)

        return render_template('employee/add-movie.html', search_result=True)
    else:
        return render_template('employee/add-movie.html', form=True)


@app.route('/add-auditorium', methods=['GET', 'POST'])
@staff_login_required
def add_auditorium():
    '''Add auditorium to theater database'''

    return apology('TODO', 'employee/layout.html', 403)


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
    movies = db.execute('SELECT * FROM movies ORDER BY title;')
    return render_template('other/movies.html', ext="employee/layout.html", title="All Movies", info=movie_info(movies))


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
    movies = db.execute('SELECT * FROM movies WHERE active = FALSE ORDER BY title;')

    if session.get('user_id') is None:
        return apology('TODO', 'member/layout.html', 403)
    
    elif session['user_type'] == 'staff':
        return render_template('other/movies.html', ext="employee/layout.html", title="Coming Soon", info=movie_info(movies, True))

        return apology('TODO', 'employee/layout.html', 403)
    
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
        rows = db.execute(
            'SELECT * FROM staff WHERE username = ?', request.form.get('username')
        )

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


@app.route('/')
def index():
    '''Show home page'''

    if session.get('user_id') is None:
        return apology('TODO', 'member/layout.html', 403)
    elif session['user_type'] == 'staff':
        employee = db.execute('SELECT * FROM staff WHERE id = ?;', session['user_id'])[0]
        return render_template('employee/employee.html', username = employee['username'])
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
        session['user_type'] == 'member'

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
        movies = db.execute('SELECT * FROM movies WHERE active = TRUE ORDER BY title')

        return render_template('other/movies.html', ext="employee/layout.html", title="Now Playing", info=movie_info(movies))
    
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

