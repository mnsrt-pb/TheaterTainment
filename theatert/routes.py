import datetime
from flask import flash, render_template,  redirect, request, url_for
from flask_login import current_user, login_user, logout_user
from theatert import app, db, bcrypt
from theatert.forms import LoginForm, RegistrationForm, SearchMovieForm, AddMovieForm, ActivateForm, InactivateForm, UpdateMovieForm
from theatert.models import Employee, Change, Member, Movie
from theatert.helpers import ( add_genres, add_rating, apology, 
                                login_required, route_name, search_movie, update_choices)
import tmdbsimple as tmdb




@app.route('/add-movie', methods=['GET', 'POST'])
@login_required(role="EMPLOYEE")
def add_movie():
    '''Add movie to theater database'''

    search_form = SearchMovieForm()
    add_form =  AddMovieForm()
    movies = Movie.query.filter_by(deleted=False).all()
    tmdb_ids = []
    for m in movies:
        tmdb_ids.append(m.tmdb_id)

    if search_form.validate_on_submit():
        return render_template('employee/add-movie.html', search_result=True, form=add_form, result=search_movie(search_form.title.data, search_form.release_year.data), tmdb_ids = tmdb_ids)
    
    if add_form.validate_on_submit():
        movie = Movie.query.filter_by(tmdb_id=add_form.m_id.data).first()
        
        # Fetch movie's info from TMDB
        data = tmdb.Movies(add_form.m_id.data)
        info = data.info()

        if movie:
            # Fetch new data
            movie.status = info['status']
            movie.overview = info['overview']
            movie.runtime = info['runtime']
            movie.tagline = info['tagline']
            add_genres(movie, info)
            add_rating(movie, data)
            try:
                movie.release_date = datetime.datetime.strptime(info['release_date'], '%Y-%m-%d').date()
            except:
                pass

            # Add Employee Change
            change = Change(
                action = "fetched new data",
                table_name = "movie",
                data_id = movie.id,
                employee_id = current_user.id
            )

            if movie.deleted:
                movie.deleted = False
                movie.poster_path = info['poster_path']
                movie.backdrop_path = None
                movie.trailer_path = None
                change.action = "added"
                flash('Movie was added.', 'success')
            else:
                flash('Fetched new data.', 'success')

        else: 
            # Add Movie
            route_name(info['title'])
            movie = Movie(
                tmdb_id = add_form.m_id.data,
                title = info['title'],
                status = info['status'],
                overview = info['overview'],
                poster_path = info['poster_path'],
                runtime = info['runtime'],
                tagline = info['tagline']
            )
            try:
                movie.route = route_name(movie.title)
            except:
                movie.route = route_name(movie.title) + '-' + str(movie.id)
            db.session.add(movie)
            add_genres(movie, info)
            add_rating(movie, data)
            try:
                movie.release_date = datetime.datetime.strptime(info['release_date'], '%Y-%m-%d').date()
            except:
                pass
        
            # Add Employee Change
            change = Change(
                action = "added",
                table_name = "movie",
                data_id = movie.id,
                employee_id = current_user.id
            )
            flash('Movie was added.', 'success')

        db.session.add(change)
        db.session.commit()

        return redirect(url_for('all_movies'))
    else:
        return render_template('employee/add-movie.html', form=search_form)


@app.route('/add-showtime', methods=['GET', 'POST'])
@login_required(role="EMPLOYEE")
def add_showtime():
    '''Assign showtimes to movies'''

    return apology('TODO', 'employee/layout.html', 403)


@app.route('/all-movies', methods=['GET', 'POST'])
@login_required(role="EMPLOYEE")
def all_movies():
    '''
    Display all movies in theater database.
    Activate/Inactivate movies.
    '''

    movies = [Movie.query.filter_by(deleted=False).order_by(Movie.title).all(), 
              Movie.query.filter_by(deleted=False).order_by(Movie.release_date.desc()).all()] 

    # Create Forms
    activate_form = ActivateForm()
    # Filter for movies that are inactive AND have a poster_path, backdrop_path, and trailer_path
    inactive = Movie.query.filter(
                        db.and_(
                            Movie.release_date.is_not(None),
                            Movie.poster_path.is_not(None),
                            Movie.backdrop_path.is_not(None),
                            Movie.trailer_path.is_not(None),
                            Movie.active.is_(False), 
                            Movie.deleted.is_(False), 
                        )).order_by(Movie.title)
    choices = [(None, 'Select Movie')]
    for m in inactive:
        choices.append((m.id, m.title))
    activate_form.m_id.choices = choices

    inactivate_form = InactivateForm()
    active = Movie.query.filter_by(active=True, deleted=False).order_by(Movie.title)
    choices = [(None, 'Select Movie')]
    for m in active:
        choices.append((m.id, m.title))
    inactivate_form.m_id.choices = choices

    # Check form submissions
    if activate_form.validate_on_submit():
        # Activate movie
        movie = Movie.query.filter_by(id=activate_form.m_id.data).first()
        if movie:
            movie.active = True

        # Add Employee Change
        change = Change(
            action = "activated",
            table_name = "movie",
            data_id = movie.id,
            employee_id = current_user.id
        )
        db.session.add(change)

        db.session.commit()
        flash('Movie activated.', 'success')
        return redirect(url_for('all_movies'))

    if inactivate_form.validate_on_submit():
        # Inactivate Movie
        movie = Movie.query.filter_by(id=inactivate_form.m_id.data).first()
        if movie:
            movie.active = False

        # Add Employee Change
        change = Change(
            action = "inactivated",
            table_name = "movie",
            data_id = movie.id,
            employee_id = current_user.id
        )
        db.session.add(change)

        db.session.commit()
        flash('Movie inactivated.', 'success')
        return redirect(url_for('all_movies'))

    
    return render_template('other/movies.html', ext="employee/layout.html", title="All Movies", info=movies, activate_form=activate_form, inactivate_form=inactivate_form)


@app.route('/coming-soon')
def coming_soon():
    '''Display movies that have not been released'''

    def coming_soon(movies):
        '''Returns a list of  movies that have not been released'''

        ms = []
        for movie in movies:
            if not movie.release_date:
                ms.append(movie)
            elif movie.release_date > datetime.datetime.now():
                ms.append(movie)
        return ms
                
    info = []

    movies = Movie.query.filter(Movie.deleted.is_(False)).order_by(Movie.title)
    info.append(coming_soon(movies))

    movies = Movie.query.filter(Movie.deleted.is_(False)).order_by(Movie.release_date.desc())
    info.append(coming_soon(movies))

    return render_template('other/movies.html', ext="employee/layout.html", title="Coming Soon", info=info)


@login_required(role="EMPLOYEE")
@app.route('/movie/<int:movie_id>/delete', methods=['POST'])
def delete_movie(movie_id):
    movie = Movie.query.filter_by(id = movie_id, deleted=False).first_or_404()
    movie.deleted = True
    movie.active = False

    change = Change(
        action = "deleted",
        table_name = "movie",
        data_id = movie.id,
        employee_id = current_user.id
    )
    db.session.add(change)

    db.session.commit()
    flash(f'{movie.title} has been deleted!', 'success')
    return redirect (url_for('all_movies'))


@app.route('/')
@app.route('/home')
def home():
    '''Show home page'''
    
    if not current_user.is_authenticated:
            return apology('TODO', 'member/layout.html', 403)
    else:
        data = Change.query.filter_by(employee_id = current_user.id).order_by(Change.date).all()
        
        changes = []
        for c in data:
            if c.table_name == 'movie':
                temp = {'change' : c.action,
                        'table_name' : 'Movie',
                        'date_time' : c.date - datetime.timedelta(hours=5),
                        'item': Movie.query.filter_by(id = c.data_id).first().title}
                changes.append(temp)

    return render_template('employee/employee.html', changes=changes)


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
    movies = [Movie.query.filter(
                db.and_(Movie.deleted.is_(False),
                        Movie.active.is_(True))).order_by(Movie.title), 
            Movie.query.filter(
                db.and_(Movie.deleted.is_(False),
                        Movie.active.is_(True))).order_by(Movie.release_date.desc())]

    return render_template('other/movies.html', ext="employee/layout.html", title="Now Playing", info=movies)
    

@app.route('/movie/<string:movie_route>')
@login_required(role="EMPLOYEE")
def movie(movie_route):
    movie = Movie.query.filter_by(route = movie_route, deleted=False).first_or_404()
    return render_template('other/movie.html', ext="employee/layout.html", Movie=movie)


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


@app.route('/movie/<string:movie_route>/update', methods=['GET', 'POST'])
@login_required(role="EMPLOYEE")
def update_movie(movie_route):
    movie = Movie.query.filter_by(route = movie_route, deleted=False).first_or_404()
    data = tmdb.Movies(movie.tmdb_id)
    images = data.images(language='en')
    videos = list(filter(lambda v: ('type', 'Trailer') in v.items(), data.videos(language='en')['results']))[::-1]

    form = UpdateMovieForm()
    form.poster.choices, form.backdrop.choices, form.trailer.choices = update_choices(images, videos)

    if form.validate_on_submit():
        if form.poster.data != None and form.poster.data != 'None':
            movie.poster_path = form.poster.data
        
        if form.backdrop.data != None and form.backdrop.data != 'None':
            movie.backdrop_path = form.backdrop.data
        
        if form.trailer.data != None and form.trailer.data != 'None':
            movie.trailer_path = form.trailer.data
    
        # Add Employee Change
        change = Change(
            action = "updated",
            table_name = "movie",
            data_id = movie.id,
            employee_id = current_user.id
        )
        db.session.add(change)

        db.session.commit()
        flash('Movie updated.', 'success')
        return redirect(url_for('movie', movie_route = movie.route))
    
    return render_template('employee/update-movie.html', ext="employee/layout.html", Movie=movie, images=images, videos=videos, form=form)

