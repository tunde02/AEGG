from datetime import datetime
from flask import Blueprint, flash, render_template, request, url_for, g
from werkzeug.utils import redirect
from sqlalchemy.sql import text

from app import db
from app.forms import CommentForm
from app.models import Post, Comment
from app.views.auth_views import login_required


bp = Blueprint('comment', __name__, url_prefix='/comment')


@bp.before_request
def load_navbar_tab():
    g.navbar_tab = 'board'


@bp.route('/create/<int:post_id>', methods=['POST'])
@login_required
def create(post_id):
    form = CommentForm()
    post = Post.query.get_or_404(post_id)

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user=g.user,
            post=post,
            create_date=datetime.now()
        )

        db.session.add(comment)
        db.session.commit()

        return redirect(url_for('post.detail', post_id=post_id, _anchor=f'comment_{comment.id}'))

    comment_list = Comment.query.filter(Comment.post_id == post_id) \
        .order_by(text('if(isnull(parent_id), id, parent_id)')) \
        .paginate(page=1, per_page=20)

    return render_template('post/post_detail.html', form=form, post=post, comment_list=comment_list)


@bp.route('/reply/<int:comment_id>', methods=['POST'])
@login_required
def reply(comment_id):
    form = CommentForm()
    parent_comment = Comment.query.get_or_404(comment_id)
    post = Post.query.get_or_404(parent_comment.post_id)

    if form.validate_on_submit():
        reply = Comment(
            content=form.content.data,
            user=g.user,
            post=post,
            parent_id=parent_comment.id,
            create_date=datetime.now()
        )

        db.session.add(reply)
        db.session.commit()

        return redirect(url_for('post.detail', post_id=post.id, _anchor=f'comment_{parent_comment.id}'))

    comment_list = Comment.query.filter(Comment.post_id == post.id) \
        .order_by(text('if(isnull(parent_id), id, parent_id)')) \
        .paginate(page=1, per_page=20)

    return render_template('post/post_detail.html', form=form, post=post, comment_list=comment_list)


@bp.route('/delete/<int:comment_id>')
@login_required
def delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if g.user != comment.user:
        flash('삭제 권한이 없습니다.')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('post.detail', post_id=comment.post_id))


@bp.route('/modify/<int:comment_id>', methods=['POST'])
@login_required
def modify(comment_id):
    form = CommentForm()
    comment = Comment.query.get_or_404(comment_id)

    if g.user != comment.user:
        flash('수정 권한이 없습니다.')

        return redirect(url_for('post.detail', post_id=comment.post_id))

    if form.validate_on_submit():
        form.populate_obj(comment)
        comment.modify_date = datetime.now()

        db.session.commit()

        return redirect(url_for('post.detail', post_id=comment.post_id))

    comment_list = Comment.query.filter(Comment.post_id == comment.post_id) \
        .order_by(text('if(isnull(parent_id), id, parent_id)')) \
        .paginate(page=1, per_page=20)

    return render_template('post/post_detail.html', form=form, post=comment.post, comment_list=comment_list)
