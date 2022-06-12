import os, uuid, shutil
from datetime import datetime

from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect, secure_filename
from sqlalchemy.sql import text

from app import db
from app.forms import CommentForm, PostForm
from app.models import Post, Comment
from app.views.auth_views import login_required
from config.default import UPLOAD_FOLDER, ALLOWED_EXTENSIONS


bp = Blueprint('post', __name__, url_prefix='/post')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_post_images_path(post):
    return os.path.join(UPLOAD_FOLDER, 'posts', post.create_date.strftime("%Y-%m-%d"), str(post.id))


def save_uploaded_images(request, post):
    # 게시글에 쓰인 이미지 파일 저장
    uploaded_images_path = os.path.join(UPLOAD_FOLDER, 'temp')
    post_images_path = get_post_images_path(post)

    if not os.path.exists(post_images_path):
        os.makedirs(post_images_path)

    if request.form.get('upload_images'):
        _filenames = request.form.get('upload_images')[:-1].split('|')

        for filename in _filenames:
            before = os.path.join(uploaded_images_path, filename)
            destination = os.path.join(post_images_path, filename)
            shutil.move(before, destination)


def remove_temp_uploaded_images(content, post):
    # 게시글 폴더의 이미지들 중 content에 없는 것 삭제
    post_images_path = get_post_images_path(post)

    for filename in os.listdir(post_images_path):
        if filename not in content:
            os.remove(os.path.join(post_images_path, filename))


@bp.before_request
def load_navbar_tab():
    g.navbar_tab = 'board'


@bp.route('/')
def post_list():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    category = request.args.get('category', type=str, default='')

    post_list = Post.query.filter(Post.category.ilike(f'%%{category}%%')).order_by(Post.create_date.desc()).paginate(page, per_page=per_page)

    return render_template('post/post_list.html', post_list=post_list, page=page, per_page=per_page, category=category)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()

    if request.method == 'POST' and form.validate_on_submit():
        post = Post(
            subject=form.subject.data,
            category=form.category.data,
            content=form.content.data if form.content.data else 'ㅈㄱㄴ',
            user=g.user,
            create_date=datetime.now()
        )

        db.session.add(post)
        db.session.commit()

        # 이미지 경로 변경
        post.content = post.content.replace('/temp/', f'/posts/{post.create_date.strftime("%Y-%m-%d")}/{post.id}/')
        db.session.commit()

        save_uploaded_images(request, post)
        remove_temp_uploaded_images(form.content.data, post)

        return redirect(url_for('post.post_list'))

    return render_template('post/post_form.html', form=form)


@bp.route('/upload', methods=['GET', 'POST'])
def image_upload():
    if request.method == "POST":
        file = request.files["image"]

        if file.filename == '':
            return "error.png"

        if file and allowed_file(file.filename):
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"{str(uuid.uuid4())}.{file_extension}")

            # 파일 이름 중복을 피하기 위해
            # 같은 이름이 존재하지 않을 때까지 uudi 새로 생성
            while os.path.exists(UPLOAD_FOLDER + "/" + filename):
                filename = secure_filename(f"{str(uuid.uuid4())}.{file_extension}")

            temp_path = os.path.join(UPLOAD_FOLDER, 'temp')
            file.save(os.path.join(temp_path, filename))

            return filename

    return "error.png"


@bp.route('/<int:post_id>')
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    comment_list = Comment.query.filter(Comment.post_id == post_id) \
        .order_by(text('if(isnull(parent_id), id, parent_id)')) \
        .paginate(page=1, per_page=20)

    # 조회수 증가
    post.num_views += 1
    db.session.commit()

    return render_template('post/post_detail.html', form=form, post=post, comment_list=comment_list)


@bp.route('/modify/<int:post_id>', methods=['GET', 'POST'])
@login_required
def modify(post_id):
    post = Post.query.get_or_404(post_id)

    if g.user != post.user:
        flash('수정 권한이 없습니다.')

        return redirect(url_for('post.detail', post_id=post_id))

    if request.method == 'POST':
        form = PostForm()

        if form.validate_on_submit():
            if form.content.data and form.content.data != "<p><br></p>":
                form.content.data = form.content.data.replace('/temp/', f'/posts/{post.create_date.strftime("%Y-%m-%d")}/{post.id}/')
            else:
                form.content.data = 'ㅈㄱㄴ'

            form.populate_obj(post)
            post.modify_date = datetime.now()

            save_uploaded_images(request, post)
            remove_temp_uploaded_images(form.content.data, post)

            db.session.commit()

            return redirect(url_for('post.detail', post_id=post_id))
    else:
        form = PostForm(obj=post)

    return render_template('post/post_form.html', form=form)


@bp.route('/delete/<int:post_id>')
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)

    if g.user != post.user:
        flash('삭제 권한이 없습니다.')

        return redirect(url_for('post.detail', post_id=post_id))

    # 게시글에 쓰인 이미지 폴더째로 삭제
    post_images_path = get_post_images_path(post)
    shutil.rmtree(post_images_path)

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('post.post_list'))


@bp.route('/vote/<int:post_id>')
@login_required
def vote(post_id):
    post = Post.query.get_or_404(post_id)

    if g.user in post.voter:
        flash('이미 추천한 게시글입니다.')
    else:
        post.voter.append(g.user)

        db.session.commit()

    return redirect(url_for('post.detail', post_id=post_id))


@bp.route('/unvote/<int:post_id>')
@login_required
def unvote(post_id):
    post = Post.query.get_or_404(post_id)

    if g.user not in post.voter:
        flash('추천하지 않은 게시글입니다.')
    else:
        post.voter.remove(g.user)

        db.session.commit()

    return redirect(url_for('post.detail', post_id=post_id))
