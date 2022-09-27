import os

from flask import Blueprint, render_template, request, g, url_for, flash
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect, secure_filename

from app import db
from app.forms import ProfileModifyForm
from app.models import User, PostNotification, CommentNotification
from config.default import UPLOAD_FOLDER


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


@bp.route('/modify/<int:user_id>', methods=['GET', 'POST'])
def modify(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        form = ProfileModifyForm()

        if form.validate_on_submit():
            error = ""

            if form.username.data != user.username and User.query.filter_by(username=form.username.data).first():
                error = "이미 존재하는 아이디입니다."
            elif form.nickname.data != user.nickname and User.query.filter_by(nickname=form.nickname.data).first():
                error = "이미 존재하는 닉네임입니다."
            elif form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
                error = "이미 존재하는 이메일입니다."

            if not error:
                # 아이디가 변경되었을 경우 프로필 사진 파일 이름도 같이 변경
                if form.username.data != user.username and user.profile_image != "images/defaults/profile_image.png":
                    file_extension = user.profile_image.split('.')[1]
                    changed_profile_image = secure_filename(f'{form.username.data}.{file_extension}')

                    before = os.path.join(UPLOAD_FOLDER, 'profile', f"{user.username}.{file_extension}")
                    after = os.path.join(UPLOAD_FOLDER, 'profile', changed_profile_image)
                    os.rename(before, after)

                    user.profile_image = f"images/profile/{changed_profile_image}"

                if form.profile_image.data is not None:
                    file_extension = form.profile_image.data.filename.rsplit('.', 1)[1].lower()
                    file_name = secure_filename(f"{form.username.data}.{file_extension}")
                    file_path = os.path.join(UPLOAD_FOLDER, 'profile', file_name)

                    form.profile_image.data.save(file_path)
                    form.profile_image.data = f"images/profile/{file_name}"

                    # 이전 프로필 사진 파일과 확장자가 달라졌다면 이전 프로필 사진 파일 삭제
                    if file_extension != user.profile_image.rsplit('.', 1)[1].lower():
                        os.remove(os.path.join(UPLOAD_FOLDER, 'profile', user.profile_image.split('/')[2]))
                else:
                    form.profile_image.data = user.profile_image

                if form.password.data != "":
                    form.password.data = generate_password_hash(form.password.data)
                else:
                    form.password.data = user.password

                form.populate_obj(user)

                db.session.commit()

                return redirect(url_for('profile.info', username=user.username))
            else:
                flash(error)
    else:
        form = ProfileModifyForm(obj=user)

    return render_template('profile/profile_modify.html', user=user, form=form)
