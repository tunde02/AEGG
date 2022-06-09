from flask import Blueprint, render_template, g


bp = Blueprint('main', __name__, url_prefix='/')


@bp.before_request
def load_navbar_tab():
    g.navbar_tab = 'home'


@bp.route('/')
def index():
    return render_template('index.html')
