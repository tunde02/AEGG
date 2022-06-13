from datetime import datetime

from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect

from app import db
from app.models import Card, CardEN, CardReview, Mage, MageEN, Nemesis, NemesisEN, related_mage, related_nemesis
from app.views.auth_views import login_required


bp = Blueprint('wiki', __name__, url_prefix='/wiki')


@bp.before_request
def load_navbar_tab():
    g.navbar_tab = 'wiki'


@bp.route('/list/mage')
def mage_list():
    return render_template('wiki/wiki_mage_list.html', tab='mage')


@bp.route('/list/card')
def card_list():
    card_list = Card.query.all()

    return render_template('wiki/wiki_card_list.html', tab='card', card_list=card_list)


@bp.route('/list/nemesis')
def nemesis_list():
    return render_template('wiki/wiki_nemesis_list.html', tab='nemesis')


@bp.route('/detail/mage/<int:mage_id>')
def mage_detail(mage_id):
    return render_template('wiki/wiki_mage_detail.html')


@bp.route('/detail/card/<int:card_id>')
def card_detail(card_id):
    card = Card.query.get_or_404(card_id)
    card_en = CardEN.query.filter(CardEN.card_id == card.id).first()
    card_review_list = CardReview.query.filter(CardReview.card_id == card.id)

    related_mage_list = Mage.query.join(related_mage, related_mage.c.mage_id == Mage.id).filter(related_mage.c.card_id == card.id).all()

    return render_template('wiki/wiki_card_detail.html', card=card, card_en=card_en, card_review_list=card_review_list, related_list=related_mage_list)


@bp.route('/detail/nemesis/<int:nemesis_id>')
def nemesis_detail(nemesis_id):
    return render_template('wiki/wiki_nemesis_detail.html')
