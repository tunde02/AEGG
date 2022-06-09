from flask import Blueprint, render_template, request, g, url_for
from werkzeug.utils import redirect

from app.models import User


bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.before_request
def load_navbar_tab():
    g.navbar_tab = 'profile'


@bp.route('/info/<string:username>')
def info(username):
    g.profile_tab = 'info'

    user = User.query.filter_by(username=username).first()

    return render_template('profile/profile_base.html', user=user)
