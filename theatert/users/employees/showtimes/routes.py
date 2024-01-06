import datetime
from flask import Blueprint, flash, render_template,  redirect, request, url_for
from flask_login import current_user
from theatert import db
from theatert.users.employees.movies.forms import SearchMovieForm, AddMovieForm, ActivateForm, InactivateForm, UpdateMovieForm
from theatert.models import Change, Movie
from theatert.users.employees.movies.utils import add_genres, add_rating, route_name, search_movie, update_choices
from theatert.users.utils import apology, login_required

import tmdbsimple as tmdb

showtimes = Blueprint('showtimes', __name__, url_prefix='/showtimes')


@showtimes.route('/add-showtime', methods=['GET', 'POST'])
@login_required(role="EMPLOYEE")
def add_showtime():
    '''Assign showtimes to movies'''

    return apology('TODO', 'employee/layout.html', 403)
