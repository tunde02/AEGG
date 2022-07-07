from datetime import datetime, date

from flask import Blueprint, flash, render_template, request, url_for, g
from werkzeug.utils import redirect

from app import db
from app.forms import RecordForm, ReviewForm
from app.models import *
from app.views.auth_views import login_required


bp = Blueprint('record', __name__, url_prefix='/record')


@bp.before_request
def load_navbar_tab():
    g.navbar_tab = 'record'


@bp.route('/list')
def record_list():
    record_list = []
    for record in Record.query.order_by(Record.date.desc()):
        record_info = {
            'record': record,
            'result': record.result,
            'nemesis': record.nemesis,
            'date': record.date,
            'player_list': []
        }

        record_user_list = RecordPlayer.query.filter(RecordPlayer.record_id == record.id).all()
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
                                   .order_by(Card.type.asc(), Card.cost.asc()).all()
    player_list = []
    user_list = RecordPlayer.query.filter(RecordPlayer.record_id == record.id).all()
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
    form = RecordForm(date=date.today().strftime('%Y-%m-%d'))

    if request.method == 'POST' and form.validate_on_submit():
        date_info = [int(info) for info in form.date.data.split('-')]
        record_date = datetime(date_info[0], date_info[1], date_info[2])
        record_nemesis = Nemesis.query.filter(Nemesis.name == form.nemesis.data).first()

        record = Record(
            result=form.result.data,
            nemesis=record_nemesis,
            date=record_date
        )

        # 공급처
        for i in range(9):
            card_name = request.form.get(f'supply_card_{i}', type=str, default='')
            card = Card.query.filter(Card.name == card_name).first()

            if card is not None:
                record.supply_pile.append(card)

        # 플레이어
        for i in range(5):
            username = request.form.get(f'player_{i}_user', type=str, default='')
            user = User.query.filter(User.username == username).first()
            magename = request.form.get(f'player_{i}_mage', type=str, default='')
            mage = Mage.query.filter(Mage.name == magename).first()

            if user is not None and mage is not None:
                db.session.add(RecordPlayer(record=record, user=user, mage=mage))

        if len(record.player_list) <= 0:
            flash('최소 한 명의 플레이어 정보를 입력해야 합니다.')
        else:
            db.session.add(record)
            db.session.commit()
            return redirect(url_for('record.record_list'))

    nemesis_list = Nemesis.query.order_by(Nemesis.tier.asc(), Nemesis.difficulty.asc()).all()
    user_list = User.query.order_by(User.nickname.asc()).all()
    mage_list = Mage.query.join(MageEN, MageEN.mage_id == Mage.id) \
                          .order_by(MageEN.name.asc()).all()
    supply_card_list = Card.query.join(CardEN, CardEN.card_id == Card.id) \
                                 .outerjoin(NemesisCardInfo, NemesisCardInfo.card_id == Card.id) \
                                 .filter(NemesisCardInfo.card_id == None) \
                                 .outerjoin(related_mage, related_mage.c.card_id == Card.id) \
                                 .filter(related_mage.c.card_id == None) \
                                 .filter((Card.name != '크리스탈') & (Card.name != '스파크')) \
                                 .order_by(Card.cost.asc(), CardEN.name.asc()).all()

    return render_template('record/record_form.html', form=form,
                           nemesis_list=nemesis_list, supply_card_list=supply_card_list,
                           user_list=user_list, mage_list=mage_list,)


@bp.route('/modify/<int:record_id>', methods=['GET', 'POST'])
@login_required
def modify_record(record_id):
    record = Record.query.get_or_404(record_id)

    if request.method == 'POST':
        form = RecordForm(date=date.today().strftime('%Y-%m-%d'))

        if form.validate_on_submit():
            date_info = [int(info) for info in form.date.data.split('-')]
            record_date = datetime(date_info[0], date_info[1], date_info[2])
            record_nemesis = Nemesis.query.filter(Nemesis.name == form.nemesis.data).first()

            record.result = form.result.data
            record.date = record_date
            record.nemesis = record_nemesis

            # 공급처
            record.supply_pile.clear()
            for i in range(9):
                card_name = request.form.get(f'supply_card_{i}', type=str, default='')
                card = Card.query.filter(Card.name == card_name).first()

                if card is not None:
                    record.supply_pile.append(card)

            # 플레이어
            prev_record_player_list = RecordPlayer.query.filter(RecordPlayer.record_id == record.id).all()
            for i in range(5):
                username = request.form.get(f'player_{i}_user', type=str, default='')
                user = User.query.filter(User.username == username).first()
                magename = request.form.get(f'player_{i}_mage', type=str, default='')
                mage = Mage.query.filter(Mage.name == magename).first()

                if user is not None and mage is not None:
                    if len(prev_record_player_list) > i:
                        prev_record_player_list[i].user = user
                        prev_record_player_list[i].mage = mage
                    else:
                        db.session.add(RecordPlayer(record=record, user=user, mage=mage))
                elif len(prev_record_player_list) > i:
                    db.session.delete(prev_record_player_list[i])

            if len(record.player_list) > 0:
                db.session.commit()
                return redirect(url_for('record.record_detail', record_id=record_id))
            else:
                flash('최소 한 명의 플레이어 정보를 입력해야 합니다.')
    else:
        form = RecordForm(
            result=record.result,
            date=record.date.strftime('%Y-%m-%d'),
            nemesis=record.nemesis.name
        )

    nemesis_list = Nemesis.query.order_by(Nemesis.tier.asc(), Nemesis.difficulty.asc()).all()

    supply_card_list = Card.query.join(CardEN, CardEN.card_id == Card.id) \
                                 .outerjoin(NemesisCardInfo, NemesisCardInfo.card_id == Card.id) \
                                 .filter(NemesisCardInfo.card_id == None) \
                                 .outerjoin(related_mage, related_mage.c.card_id == Card.id) \
                                 .filter(related_mage.c.card_id == None) \
                                 .filter((Card.name != '크리스탈') & (Card.name != '스파크')) \
                                 .order_by(Card.cost.asc(), CardEN.name.asc()).all()
    record_supply_pile = Card.query.join(supply_pile, supply_pile.c.card_id == Card.id) \
                                   .filter(supply_pile.c.record_id == record.id) \
                                   .order_by(Card.type.asc(), Card.cost.asc()).all()

    user_list = User.query.order_by(User.nickname.asc()).all()
    mage_list = Mage.query.join(MageEN, MageEN.mage_id == Mage.id) \
                          .order_by(MageEN.name.asc()).all()
    player_list = []
    record_player_list = RecordPlayer.query.filter(RecordPlayer.record_id == record.id).all()
    for user in record_player_list:
        player_list.append({
            'user': User.query.get_or_404(user.user_id),
            'mage': Mage.query.get_or_404(user.mage_id)
        })

    return render_template('record/record_form.html', form=form, nemesis_list=nemesis_list,
                           supply_card_list=supply_card_list, record_supply_pile=record_supply_pile,
                           user_list=user_list, mage_list=mage_list, player_list=player_list)
