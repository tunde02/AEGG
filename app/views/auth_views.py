import os, functools

from flask import Blueprint, url_for, render_template, flash, request, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect, secure_filename

from app import db
from app.forms import SignUpForm, LoginForm
from app.models import User
from config.default import UPLOAD_FOLDER


bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            _next = request.url if request.method == 'GET' else ''

            return redirect(url_for('auth.login', next=_next))

        return view(*args, **kwargs)

    return wrapped_view


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if request.method == 'POST' and form.validate_on_submit():
        error = None

        if User.query.filter_by(username=form.username.data).first():
            error = '이미 존재하는 아이디입니다.'
        elif User.query.filter_by(nickname=form.nickname.data).first():
            error = '이미 존재하는 닉네임입니다.'
        elif User.query.filter_by(email=form.email.data).first():
            error = '이미 존재하는 이메일입니다.'

        if error is None:
            user = User(username=form.username.data,
                password=generate_password_hash(form.password.data),
                nickname=form.nickname.data,
                email=form.email.data,
                about_me=form.about_me.data)

            if form.profile_image.data is not None:
                file_extension = form.profile_image.data.filename.rsplit('.', 1)[1].lower()
                file_name = secure_filename(f"{form.username.data}.{file_extension}")
                file_path = os.path.join(UPLOAD_FOLDER, 'profile', file_name)

                form.profile_image.data.save(file_path)
                user.profile_image = f"images/profile/{file_name}"

            db.session.add(user)
            db.session.commit()

            return redirect(url_for('main.index'))
        else:
            flash(error)

    return render_template('auth/signup.html', form=form)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(username=form.username.data).first()

        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."

        if error is None:
            session.clear()
            session['user_id'] = user.id
            _next = request.args.get('next', '')

            return redirect(_next if _next else url_for('main.index'))
        else:
            flash(error)

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    session.clear()

    return redirect(url_for('main.index'))
