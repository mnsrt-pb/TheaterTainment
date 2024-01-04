import datetime
from flask import Blueprint, flash, render_template,  redirect, request, url_for
from flask_login import current_user
from theatert import db, bcrypt
from theatert.users.employees.forms import RegistrationForm, SearchMovieForm, AddMovieForm, ActivateForm, InactivateForm, UpdateMovieForm
from theatert.models import Employee, Change, Movie
from theatert.users.employees.utils import ( add_genres, add_rating, route_name, search_movie, update_choices)
from theatert.users.utils import apology, login_required

import tmdbsimple as tmdb


employees = Blueprint('employees', __name__, url_prefix='/employee', template_folder='../../templates')


@employees.route('/add-movie', methods=['GET', 'POST'])
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

        return redirect(url_for('employees.all_movies'))
    else:
        return render_template('employee/add-movie.html', form=search_form)


@employees.route('/add-showtime', methods=['GET', 'POST'])
@login_required(role="EMPLOYEE")
def add_showtime():
    '''Assign showtimes to movies'''

    return apology('TODO', 'employee/layout.html', 403)


@employees.route('/all-movies', methods=['GET', 'POST'])
@login_required(role="EMPLOYEE")
def all_movies():
    '''
    Display all movies in theater database.
    Activate/Inactivate movies.
    '''
    page = request.args.get('page', 1, type=int)
    movies = [Movie.query.filter_by(deleted=False).order_by(Movie.title)\
                .paginate(page=page, per_page=5), 
              Movie.query.filter_by(deleted=False).order_by(Movie.release_date.desc())\
                .paginate(page=page, per_page=5)] 

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
        return redirect(url_for('employees.all_movies'))

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
        return redirect(url_for('employees.all_movies'))

    
    return render_template('other/movies.html', ext="employee/layout.html", title="All Movies", info=movies, activate_form=activate_form, inactivate_form=inactivate_form)


@employees.route('/coming-soon')
def coming_soon():
    '''Display movies that have not been released'''

    page = request.args.get('page', 1, type=int)

    movies = [Movie.query.filter(db.and_(Movie.deleted.is_(False), db.ColumnOperators.__ge__(Movie.release_date, datetime.datetime.now())))\
                .order_by(Movie.title)\
                .paginate(page=page, per_page=5),
            Movie.query.filter(db.and_(Movie.deleted.is_(False), db.ColumnOperators.__ge__(Movie.release_date, datetime.datetime.now())))\
                .order_by(Movie.release_date.desc())\
                .paginate(page=page, per_page=5)]
        
    return render_template('other/movies.html', ext="employee/layout.html", title="Coming Soon", info=movies)


@login_required(role="EMPLOYEE")
@employees.route('/movie/<int:movie_id>/delete', methods=['POST'])
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
    return redirect (url_for('employees.all_movies'))


@employees.route('/')
@employees.route('/home')
def home():
    '''Show home page'''
    
    # FIXME: should be something else
    if not current_user.is_authenticated:
        return apology('TODO', 'member/layout.html', 403)
    else:
        page = request.args.get('page', 1, type=int)
        data = Change.query.filter_by(employee_id = current_user.id)\
            .order_by(Change.date.desc())\
            .paginate(page=page, per_page=10)
        
        changes = []
        for c in data.items:
            if c.table_name == 'movie':
                temp = {'change' : c.action,
                        'table_name' : 'Movie',
                        'date_time' : c.date - datetime.timedelta(hours=5),
                        'item': Movie.query.filter_by(id = c.data_id).first().title}
                changes.append(temp)

    return render_template('employee/home.html', changes=changes, data=data)


@employees.route('/now-playing')
@login_required(role="EMPLOYEE")
def now_playing():
    '''Display movies that are now playing'''
    
    page = request.args.get('page', 1, type=int)

    movies = [Movie.query.filter(
                db.and_(Movie.deleted.is_(False), Movie.active.is_(True)))\
                    .order_by(Movie.title)\
                    .paginate(page=page, per_page=5), 
            Movie.query.filter(
                db.and_(Movie.deleted.is_(False), Movie.active.is_(True)))\
                    .order_by(Movie.release_date.desc())\
                .paginate(page=page, per_page=5)]

    return render_template('other/movies.html', ext="employee/layout.html", title="Now Playing", info=movies)
    

@employees.route('/movie/<string:movie_route>')
@login_required(role="EMPLOYEE")
def movie(movie_route):
    movie = Movie.query.filter_by(route = movie_route, deleted=False).first_or_404()
    return render_template('other/movie.html', ext="employee/layout.html", Movie=movie)


@employees.route('/register', methods=['GET', 'POST'])
def register():
    '''Register associate'''

    if current_user.is_authenticated:
        return redirect(url_for('employees.home'))

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
        return redirect(url_for('employees.login'))
    else:
        return render_template('employee/register.html', form=form)


@employees.route('/movie/<string:movie_route>/update', methods=['GET', 'POST'])
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
        return redirect(url_for('employees.movie', movie_route = movie.route))
    
    return render_template('employee/update-movie.html', ext="employee/layout.html", Movie=movie, images=images, videos=videos, form=form)

