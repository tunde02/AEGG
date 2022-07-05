from datetime import datetime

from flask import Blueprint, flash, render_template, request, url_for, g
from werkzeug.utils import redirect

from app import db
from app.forms import ReviewForm
from app.models import User, Card, Mage, Nemesis, Record, RecordUser, supply_pile, RecordReview
from app.views.auth_views import login_required


bp = Blueprint('record', __name__, url_prefix='/record')


@bp.before_request
def load_navbar_tab():
    g.navbar_tab = 'record'


@bp.route('/list')
def record_list():
    record_list = []
    for record in Record.query.all():
        record_info = {
            'record': record,
            'result': record.result,
            'nemesis': record.nemesis,
            'date': record.date,
            'player_list': []
        }

        record_user_list = RecordUser.query.filter(RecordUser.record_id == record.id).all()
        for record_user in record_user_list:
            record_info['player_list'].append({
                'user': User.query.get_or_404(record_user.user_id),
                'mage': Mage.query.get_or_404(record_user.mage_id)
            })

        record_list.append(record_info)

    return render_template('record/record_list.html', record_list=record_list)


@bp.route('/detail/<int:record_id>')
def record_detail(record_id):
    record = Record.query.get_or_404(record_id)
    record_supply_pile = Card.query.join(supply_pile, supply_pile.c.card_id == Card.id) \
                                   .filter(supply_pile.c.record_id == record.id) \
                                   .order_by(Card.type, Card.cost).all()
    player_list = []
    user_list = RecordUser.query.filter(RecordUser.record_id == record.id).all()
    for user in user_list:
        player_list.append({
            'user': User.query.get_or_404(user.user_id),
            'mage': Mage.query.get_or_404(user.mage_id)
        })

    return render_template('record/record_detail.html', record=record,
                           record_supply_pile=record_supply_pile, player_list=player_list)


@bp.route('/append', methods=['GET', 'POST'])
@login_required
def append_record():
    return render_template('record/record_form.html')
