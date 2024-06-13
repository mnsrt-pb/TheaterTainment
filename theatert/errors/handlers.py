from flask import Blueprint, render_template
from flask_login import current_user

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    if  current_user.is_authenticated:
        if current_user.role == 'EMPLOYEE':
            return render_template('errors/404.html', layout='employee/layout.html'), 404
    return render_template('errors/404.html', layout='member/layout.html'), 404

    
@errors.app_errorhandler(403)
def error_403(error):
    if  current_user.is_authenticated:
        if current_user.role == 'EMPLOYEE':
            return render_template('errors/403.html', layout='employee/layout.html'), 403
    return render_template('errors/403.html', layout='member/layout.html'), 403


@errors.app_errorhandler(500)
def error_500(error):
    if  current_user.is_authenticated:
        if current_user.role == 'EMPLOYEE':
            return render_template('errors/500.html', layout='employee/layout.html'), 500
    return render_template('errors/500.html', layout='member/layout.html'), 500

