from flask import Blueprint, render_template, g, current_app, request

from app.models import Mage, MageEN, Card, CardEN, Nemesis, NemesisEN, Post, PostNotification, CommentNotification

bp = Blueprint('main', __name__, url_prefix='/')


@bp.before_request
def load_navbar_tab():
    g.navbar_tab = 'home'
    if g.user:
        g.num_notifications = len(PostNotification.query.filter_by(user=g.user, is_checked=False).all()) + len(CommentNotification.query.filter_by(user=g.user, is_checked=False).all())


@bp.route('/')
def index():
    current_app.logger.info(f"User ({request.environ.get('HTTP_X_REAL_IP', request.remote_addr)}) entered.")

    mage_list = Mage.query.join(MageEN).order_by(Mage.avg_score.desc(), MageEN.name.asc()).paginate(1, per_page=5)
    card_list = Card.query.join(CardEN).order_by(Card.avg_score.desc(), CardEN.name.asc()).paginate(1, per_page=5)
    nemesis_list = Nemesis.query.join(NemesisEN).order_by(Nemesis.avg_score.desc(), NemesisEN.name.asc()).paginate(1, per_page=5)
    post_list = Post.query.order_by(Post.create_date.desc()).paginate(1, per_page=15)

    return render_template('index.html',
                           mage_list=mage_list, card_list=card_list, nemesis_list=nemesis_list,
                           post_list=post_list)
