from flask import Blueprint, render_template, request, g, url_for
from werkzeug.utils import redirect

from app import db
from app.models import User, PostNotification, CommentNotification


bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.before_request
def load_navbar_tab():
    g.navbar_tab = 'profile'
    if g.user:
        g.num_notifications = len(PostNotification.query.filter_by(user=g.user, is_checked=False).all()) + len(CommentNotification.query.filter_by(user=g.user, is_checked=False).all())


@bp.route('/info/<string:username>')
def info(username):
    g.profile_tab = request.args.get('profile_tab', type=str, default='info')

    user = User.query.filter_by(username=username).first()

    post_notification_list = PostNotification.query.filter_by(user=user).order_by(PostNotification.create_date.desc()).paginate(1, per_page=20)
    comment_notification_list = CommentNotification.query.filter_by(user=user).order_by(CommentNotification.create_date.desc()).paginate(1, per_page=20)

    return render_template('profile/profile_base.html', user=user, post_notification_list=post_notification_list, comment_notification_list=comment_notification_list)


@bp.route('/notifications/<string:username>', methods=['POST'])
def notifications(username):
    selected_post_notification_id_list = request.form.get('selectedPostNotifications', type=str, default='').split('|')[:-1]
    selected_comment_notification_id_list = request.form.get('selectedCommentNotifications', type=str, default='').split('|')[:-1]

    for id in selected_post_notification_id_list:
        notification = PostNotification.query.get_or_404(id)
        db.session.delete(notification)

    for id in selected_comment_notification_id_list:
        notification = CommentNotification.query.get_or_404(id)
        db.session.delete(notification)

    db.session.commit()

    return redirect(url_for('profile.info', username=username, profile_tab='notifications'))


@bp.route('/check/postnotification/<int:notification_id>')
def check_post_notification(notification_id):
    notification = PostNotification.query.get_or_404(notification_id)
    notification.is_checked = True

    db.session.commit()

    return redirect(url_for('post.detail', post_id=notification.post.id))


@bp.route('/check/commentnotification/<int:notification_id>')
def check_comment_notification(notification_id):
    notification = CommentNotification.query.get_or_404(notification_id)
    notification.is_checked = True

    db.session.commit()

    return redirect(url_for('post.detail', post_id=notification.comment.post.id))
