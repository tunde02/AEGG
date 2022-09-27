from datetime import datetime, date

from flask import Blueprint, flash, render_template, request, url_for, g
from werkzeug.utils import redirect
from sqlalchemy.sql import text

from app import db
from app.forms import CommentForm, RecordForm
from app.models import *
from app.views.auth_views import login_required


bp = Blueprint('record', __name__, url_prefix='/record')


def get_record_info(record):
    record_info = {}

    record_info['comment_list'] = RecordComment.query.filter(RecordComment.record_id == record.id) \
                                               .order_by(text('if(isnull(parent_id), id, parent_id)')).all()
    record_info['supply_pile'] = Card.query.join(supply_pile, supply_pile.c.card_id == Card.id) \
                                           .filter(supply_pile.c.record_id == record.id) \
                                           .order_by(Card.type.asc(), Card.cost.asc()).all()
    record_info['player_list'] = []
    user_list = RecordPlayer.query.filter(RecordPlayer.record_id == record.id).all()
    for user in user_list:
        record_info['player_list'].append({
            'user': User.query.get_or_404(user.user_id),
            'mage': Mage.query.get_or_404(user.mage_id)
        })

    return record_info


def has_keyword(record, keyword):
    check = False
    record_info = {}

    record_info['nemesis_name'] = record.nemesis.name
    record_info['nemesis_name_en'] = record.nemesis.nemesis_en[0].name
    record_info['date'] = record.date
    record_info['user_name_list'] = [user.nickname for user in User.query.join(RecordPlayer, RecordPlayer.user_id == User.id).filter(RecordPlayer.record == record).all()]
    record_info['mage_name_list'] = [mage.name for mage in Mage.query.join(RecordPlayer, RecordPlayer.mage_id == Mage.id).filter(RecordPlayer.record == record).all()]
    record_info['mage_name_en_list'] = [mage.name for mage in MageEN.query.join(RecordPlayer, RecordPlayer.mage_id == MageEN.mage_id).filter(RecordPlayer.record == record).all()]
    record_info['supply_pile_name_list'] = [card.name for card in record.supply_pile]
    record_info['supply_pile_name_en_list'] = [card.card_en[0].name for card in record.supply_pile]

    check = check or keyword in record_info['nemesis_name']
    check = check or keyword in record_info['nemesis_name_en'] or keyword in record_info['nemesis_name_en'].lower()
    check = check or keyword in record_info['date'].strftime('%Y%m%d')

    for user_name in record_info['user_name_list']:
        check = check or keyword in user_name or keyword in user_name.lower()

    for mage_name in record_info['mage_name_list']:
        check = check or keyword in mage_name

    for mage_name_en in record_info['mage_name_en_list']:
        check = check or keyword in mage_name_en or keyword in mage_name_en.lower()

    for card_name in record_info['supply_pile_name_list']:
        check = check or keyword in card_name

    for card_name_en in record_info['supply_pile_name_en_list']:
        check = check or keyword in card_name_en or keyword in card_name_en.lower()

    return check


@bp.before_request
def load_navbar_tab():
    g.navbar_tab = 'record'
    if g.user:
        g.num_notifications = len(PostNotification.query.filter_by(user=g.user, is_checked=False).all()) + len(CommentNotification.query.filter_by(user=g.user, is_checked=False).all())


@bp.route('/list')
def record_list():
    sort_type = request.args.get('sort_type', type=str, default='newest')
    keyword = request.args.get('keyword', type=str, default='')
    target_records = Record.query.order_by(Record.date.desc() if sort_type == 'newest' else Record.date.asc()).all()

    record_list = []
    index = 0
    for record in target_records:
        if not has_keyword(record, keyword):
            continue

        record_info = {
            'index': index,
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
        index += 1

    return render_template('record/record_list.html', record_list=record_list, sort_type=sort_type, keyword=keyword)


@bp.route('/detail/<int:record_id>')
def record_detail(record_id):
    form = CommentForm()
    record = Record.query.get_or_404(record_id)
    record_info = get_record_info(record)

    return render_template('record/record_detail.html', form=form,
                           record=record, record_comment_list=record_info['comment_list'],
                           record_supply_pile=record_info['supply_pile'], player_list=record_info['player_list'])


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
                                 .order_by(CardEN.name.asc()).all()

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

    record_info = get_record_info(record)
    nemesis_list = Nemesis.query.order_by(Nemesis.tier.asc(), Nemesis.difficulty.asc()).all()
    supply_card_list = Card.query.join(CardEN, CardEN.card_id == Card.id) \
                                 .outerjoin(NemesisCardInfo, NemesisCardInfo.card_id == Card.id) \
                                 .filter(NemesisCardInfo.card_id == None) \
                                 .outerjoin(related_mage, related_mage.c.card_id == Card.id) \
                                 .filter(related_mage.c.card_id == None) \
                                 .filter((Card.name != '크리스탈') & (Card.name != '스파크')) \
                                 .order_by(CardEN.name.asc()).all()
    user_list = User.query.order_by(User.nickname.asc()).all()
    mage_list = Mage.query.join(MageEN, MageEN.mage_id == Mage.id) \
                          .order_by(MageEN.name.asc()).all()

    return render_template('record/record_form.html', form=form, nemesis_list=nemesis_list,
                           supply_card_list=supply_card_list, record_supply_pile=record_info['supply_pile'],
                           user_list=user_list, mage_list=mage_list, player_list=record_info['player_list'])


@bp.route('/comment/create/<int:record_id>', methods=['POST'])
@login_required
def create_record_comment(record_id):
    form = CommentForm()
    record = Record.query.get_or_404(record_id)

    if form.validate_on_submit():
        record_comment = RecordComment(
            content=form.content.data,
            user=g.user,
            record=record,
            create_date=datetime.now()
        )

        db.session.add(record_comment)
        db.session.commit()

        return redirect(url_for('record.record_detail', record_id=record_id))

    record_info = get_record_info(record)

    return render_template('record/record_detail.html', form=form,
                           record=record, record_comment_list=record_info['comment_list'],
                           record_supply_pile=record_info['supply_pile'], player_list=record_info['player_list'])


@bp.route('/comment/modify/<int:record_comment_id>', methods=['POST'])
@login_required
def modify_record_comment(record_comment_id):
    form = CommentForm()
    record_comment = RecordComment.query.get_or_404(record_comment_id)
    record = Record.query.get_or_404(record_comment.record_id)

    if g.user != record_comment.user:
        flash('수정 권한이 없습니다.')
        return redirect(url_for('record.record_detail', record_id=record.id))

    if form.validate_on_submit():
        form.populate_obj(record_comment)
        record_comment.modify_date = datetime.now()

        db.session.commit()

        return redirect(url_for('record.record_detail', record_id=record.id))

    record_info = get_record_info(record)

    return render_template('record/record_detail.html', form=form,
                           record=record, record_comment_list=record_info['comment_list'],
                           record_supply_pile=record_info['supply_pile'], player_list=record_info['player_list'])


@bp.route('/comment/delete/<int:record_comment_id>')
@login_required
def delete_record_comment(record_comment_id):
    record_comment = RecordComment.query.get_or_404(record_comment_id)
    record_id = record_comment.record_id

    if g.user != record_comment.user:
        flash('삭제 권한이 없습니다.')
    else:
        db.session.delete(record_comment)
        db.session.commit()

    return redirect(url_for('record.record_detail', record_id=record_id))


@bp.route('/comment/reply/<int:record_comment_id>', methods=['POST'])
@login_required
def reply_record_comment(record_comment_id):
    form = CommentForm()
    parent_comment = RecordComment.query.get_or_404(record_comment_id)
    record = Record.query.get_or_404(parent_comment.record_id)

    if form.validate_on_submit():
        reply = RecordComment(
            content=form.content.data,
            user=g.user,
            record=record,
            parent_id=parent_comment.id,
            create_date=datetime.now()
        )

        db.session.add(reply)
        db.session.commit()

        return redirect(url_for('record.record_detail', record_id=record.id))

    record_info = get_record_info(record)

    return render_template('record/record_detail.html', form=form,
                           record=record, record_comment_list=record_info['comment_list'],
                           record_supply_pile=record_info['supply_pile'], player_list=record_info['player_list'])
