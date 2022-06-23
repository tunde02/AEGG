import os

from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect, secure_filename

from app import db
from app.forms import CardForm, MageForm
from app.models import Card, CardEN, CardReview, Mage, MageEN, MageReview, MageSpecificCard, MageSpecificObject, MageStartingDeck, MageStartingHand, Nemesis, NemesisEN, related_mage, related_nemesis
from app.views.auth_views import login_required
from config.default import UPLOAD_FOLDER


bp = Blueprint('wiki', __name__, url_prefix='/wiki')


@bp.before_request
def load_navbar_tab():
    g.navbar_tab = 'wiki'


@bp.route('/list')
def wiki_list():
    wiki_type = request.args.get('wiki_type', type=str, default='mage')
    wiki, wiki_en, join_condition, order_condition = None, None, None, None

    if wiki_type == 'mage':
        wiki = Mage
        wiki_en = MageEN
        join_condition = Mage.id == MageEN.mage_id
        order_condition = (MageEN.name, MageEN.name)
    elif wiki_type == 'card':
        wiki = Card
        wiki_en = CardEN
        join_condition = Card.id == CardEN.card_id
        order_condition = (Card.cost, CardEN.name)
    else:
        wiki = Nemesis
        wiki_en = NemesisEN
        join_condition = Nemesis.id == NemesisEN.nemesis_id
        order_condition = (Nemesis.tier, NemesisEN.name)

    wiki_info_list = wiki.query.join(wiki_en, join_condition).order_by(order_condition[0], order_condition[1]).all()
    wiki_info_en_list = wiki_en.query.join(wiki, join_condition).order_by(order_condition[0], order_condition[1]).all()

    return render_template('wiki/wiki_list.html',
                           wiki_type=wiki_type,
                           wiki_list=wiki_info_list, wiki_en_list=wiki_info_en_list)


@bp.route('/list/card')
def card_list():
    card_list = Card.query.join(CardEN, Card.id == CardEN.card_id).order_by(Card.cost, CardEN.name).all()
    card_en_list = CardEN.query.join(Card, CardEN.card_id == Card.id).order_by(Card.cost, CardEN.name).all()

    return render_template('wiki/wiki_card_list.html', tab='card', card_list=card_list, card_en_list=card_en_list)


@bp.route('/detail/mage/<int:mage_id>')
def mage_detail(mage_id):
    mage = Mage.query.get_or_404(mage_id)
    mage_en = MageEN.query.filter(MageEN.mage_id == mage.id).first()
    mage_review_list = MageReview.query.filter(MageReview.mage_id == mage.id).order_by(MageReview.create_date.asc()).all()

    # 각 균열 마법사에 대한 리뷰는 계정당 한 번씩만 가능하도록 제한
    already_reviewed = True if g.user and MageReview.query.filter(MageReview.mage_id == mage.id, MageReview.user == g.user).first() else False

    starting_hand = MageStartingHand.query.filter(MageStartingHand.mage_id == mage.id).order_by(MageStartingHand.order.asc()).all()
    starting_deck = MageStartingDeck.query.filter(MageStartingDeck.mage_id == mage.id).order_by(MageStartingDeck.order.asc()).all()

    specific_card_list = MageSpecificCard.query.filter(MageSpecificCard.mage_id == mage.id).order_by(MageSpecificCard.label.asc()).all()
    specific_obj_list = MageSpecificObject.query.filter(MageSpecificObject.mage_id == mage.id).order_by(MageSpecificObject.label.asc()).all()

    return render_template('wiki/wiki_mage_detail.html',
                           mage=mage, mage_en=mage_en,
                           starting_hand=starting_hand, starting_deck=starting_deck,
                           specific_card_list=specific_card_list, specific_obj_list=specific_obj_list,
                           review_list=mage_review_list, already_reviewed=already_reviewed)


@bp.route('/detail/card/<int:card_id>')
def card_detail(card_id):
    card = Card.query.get_or_404(card_id)
    card_en = CardEN.query.filter(CardEN.card_id == card.id).first()
    card_review_list = CardReview.query.filter(CardReview.card_id == card.id).order_by(CardReview.create_date.asc()).all()

    # 각 카드에 대한 리뷰는 계정당 한 번씩만 가능하도록 제한
    already_reviewed = True if g.user and CardReview.query.filter(CardReview.card_id == card.id, CardReview.user == g.user).first() else False

    related_mage_list = Mage.query.join(related_mage, related_mage.c.mage_id == Mage.id).filter(related_mage.c.card_id == card.id).all()
    related_nemesis_list = Nemesis.query.join(related_nemesis, related_nemesis.c.nemesis_id == Nemesis.id).filter(related_nemesis.c.card_id == card.id).all()

    return render_template('wiki/wiki_card_detail.html',
                           card=card, card_en=card_en,
                           review_list=card_review_list, already_reviewed=already_reviewed,
                           related_mage_list=related_mage_list, related_nemesis_list=related_nemesis_list)


@bp.route('/detail/nemesis/<int:nemesis_id>')
def nemesis_detail(nemesis_id):
    # TODO
    print('NEMESIS DETAIL')
    return render_template('wiki/wiki_nemesis_detail.html')


@bp.route('/append/mage', methods=['GET', 'POST'])
def append_mage():
    form = MageForm()
    card_list = Card.query.order_by(Card.cost, Card.name)

    if request.method == 'POST' and form.validate_on_submit():
        mage = Mage(
            name=form.name.data,
            series=form.series.data,
            ability_name=form.ability_name.data,
            ability=form.ability.data,
            activation_time=form.activation_time.data,
            required_charges=form.required_charges.data
        )
        mage_en = MageEN(
            mage=mage,
            name=form.name_en.data,
            series=form.series_en.data,
            ability_name=form.ability_name_en.data,
            ability=form.ability_en.data,
            activation_time=form.activation_time_en.data
        )

        # 아이콘 이미지 저장
        if form.image.data is not None:
            file_extension = form.image.data.filename.rsplit('.', 1)[1].lower()
            file_name = secure_filename(f"{form.name_en.data.lower()}_{form.series_en.data.lower()}.{file_extension}")
            file_path = os.path.join(UPLOAD_FOLDER, 'mage/icon', file_name)

            form.image.data.save(file_path)
            mage.image = f"images/mage/icon/{file_name}"

        # 보드 이미지 저장
        if form.board_image.data is not None:
            file_extension = form.board_image.data.filename.rsplit('.', 1)[1].lower()
            file_name = secure_filename(f"{form.name_en.data.lower()}_{form.series_en.data.lower()}.{file_extension}")
            file_path = os.path.join(UPLOAD_FOLDER, 'mage/board', file_name)

            form.board_image.data.save(file_path)
            mage.board_image = f"images/mage/board/{file_name}"

        # 시작 패
        for i in range(5):
            card_name = request.form.get(f'starting_hand_{i}', type=str, default='')
            if card_name == '':
                continue

            card = Card.query.filter(Card.name == card_name).first()
            hand = MageStartingHand(mage=mage, card=card, order=i)
            db.session.add(hand)

        # 시작 덱
        for i in range(5):
            card_name = request.form.get(f'starting_deck_{i}', type=str, default='')
            if card_name == '':
                continue

            card = Card.query.filter(Card.name == card_name).first()
            deck = MageStartingDeck(mage=mage, card=card, order=i)
            db.session.add(deck)

        # 특수 카드
        specific_card_name_list = request.form.get('specific_card_str', type=str, default='').split('|')[:-1]
        for card_name in specific_card_name_list:
            card = Card.query.filter(Card.name == card_name).first()
            specific_card = MageSpecificCard(mage=mage, card=card)
            db.session.add(specific_card)

        db.session.add(mage)
        db.session.add(mage_en)
        db.session.commit()

        return redirect(url_for('wiki.wiki_list', wiki_type='mage'))

    return render_template('wiki/wiki_mage_form.html', form=form, card_list=card_list)


@bp.route('/append/card', methods=['GET', 'POST'])
@login_required
def append_card():
    form = CardForm()
    mage_list = Mage.query.all()
    nemesis_list = Nemesis.query.all()

    if request.method == 'POST' and form.validate_on_submit():
        card = Card(
            name=form.name.data,
            type=form.type.data,
            cost=form.cost.data,
            effect=form.effect.data
        )
        card_en = CardEN(
            card=card,
            name=form.name_en.data,
            type=form.type_en.data,
            effect=form.effect_en.data
        )

        if form.image.data is not None:
            file_extension = form.image.data.filename.rsplit('.', 1)[1].lower()
            file_name = secure_filename(f"{form.name_en.data.lower()}.{file_extension}")
            file_path = os.path.join(UPLOAD_FOLDER, 'card', file_name)

            form.image.data.save(file_path)
            card.image = f"images/card/{file_name}"

        related_mage_name_list = request.form.get('mage_relations', type=str, default='').split('|')[:-1]
        related_nemesis_name_list = request.form.get('nemesis_relations', type=str, default='').split('|')[:-1]

        for mage_name in related_mage_name_list:
            mage = Mage.query.filter(Mage.name == mage_name).first()
            card.related_mage.append(mage)

        for nemesis_name in related_nemesis_name_list:
            nemesis = Nemesis.query.filter(Nemesis.name == nemesis_name).first()
            card.related_nemesis.append(nemesis)

        db.session.add(card)
        db.session.add(card_en)
        db.session.commit()

        return redirect(url_for('wiki.wiki_list', wiki_type='card'))

    return render_template('wiki/wiki_card_form.html', form=form, mage_list=mage_list, nemesis_list=nemesis_list)


@bp.route('/append/nemesis', methods=['GET', 'POST'])
def append_nemesis():
    # TODO
    print('APPEND NEMESIS')
    return redirect(url_for('wiki.wiki_list', wiki_type='nemesis'))


@bp.route('/modify/mage/<int:mage_id>', methods=['GET', 'POST'])
@login_required
def modify_mage(mage_id):
    mage = Mage.query.get_or_404(mage_id)
    mage_en = MageEN.query.filter(MageEN.mage_id == mage.id).first()

    if request.method == 'POST':
        form = MageForm()

        if form.validate_on_submit():
            file_name = f"{form.name_en.data.lower()}_{form.series_en.data.lower()}"

            # 아이콘 이미지 이름 변경
            if 'defaults' not in mage.image and (form.name_en.data != mage_en.name or form.series_en.data != mage_en.series):
                prev_file_extension = os.path.basename(mage.image).rsplit('.', 1)[1].lower()
                new_file_name = secure_filename(f"{file_name}.{prev_file_extension}")
                os.rename(os.path.join('./app/static', mage.image), os.path.join(UPLOAD_FOLDER, 'mage/icon', new_file_name))

                mage.image = f"images/mage/icon/{new_file_name}"

            # 보드 이미지 이름 변경
            if 'defaults' not in mage.board_image and (form.name_en.data != mage_en.name or form.series_en.data != mage_en.series):
                prev_file_extension = os.path.basename(mage.board_image).rsplit('.', 1)[1].lower()
                new_file_name = secure_filename(f"{file_name}.{prev_file_extension}")
                os.rename(os.path.join('./app/static', mage.board_image), os.path.join(UPLOAD_FOLDER, 'mage/board', new_file_name))

                mage.board_image = f"images/mage/board/{new_file_name}"

            if form.image.data is not None:
                file_extension = form.image.data.filename.rsplit('.', 1)[1].lower()
                _file_name = secure_filename(f"{file_name}.{file_extension}")
                file_path = os.path.join(UPLOAD_FOLDER, 'mage/icon', _file_name)

                form.image.data.save(file_path)
                mage.image = f"images/mage/icon/{_file_name}"

            if form.board_image.data is not None:
                file_extension = form.board_image.data.filename.rsplit('.', 1)[1].lower()
                _file_name = secure_filename(f"{file_name}.{file_extension}")
                file_path = os.path.join(UPLOAD_FOLDER, 'mage/board', _file_name)

                form.board_image.data.save(file_path)
                mage.board_image = f"images/mage/board/{_file_name}"

            mage.name = form.name.data
            mage.series = form.series.data
            mage.ability_name = form.ability_name.data
            mage.ability = form.ability.data
            mage.activation_time = form.activation_time.data
            mage.required_charges = form.required_charges.data

            mage_en.name = form.name_en.data
            mage_en.series = form.series_en.data
            mage_en.ability_name = form.ability_name_en.data
            mage_en.ability = form.ability_en.data
            mage_en.activation_time = form.activation_time_en.data

            # 시작 패 수정
            for i in range(5):
                card_name = request.form.get(f'starting_hand_{i}', type=str, default='')
                prev_hand = MageStartingHand.query.filter(MageStartingHand.mage_id == mage.id, MageStartingHand.order == i).first()

                if prev_hand is not None:
                    if card_name == '': # delete hand
                        db.session.delete(prev_hand)
                    elif card_name != prev_hand.card.name: # modify hand
                        card = Card.query.filter(Card.name == card_name).first()
                        prev_hand.card = card
                elif card_name != '': # append hand
                    card = Card.query.filter(Card.name == card_name).first()
                    hand = MageStartingHand(mage=mage, card=card, order=i)
                    db.session.add(hand)

            # 시작 덱 수정
            for i in range(5):
                card_name = request.form.get(f'starting_deck_{i}', type=str, default='')
                prev_deck = MageStartingDeck.query.filter(MageStartingDeck.mage_id == mage.id, MageStartingDeck.order == i).first()

                if prev_deck is not None:
                    if card_name == '': # delete deck
                        db.session.delete(prev_deck)
                    elif card_name != prev_deck.card.name: # modify deck
                        card = Card.query.filter(Card.name == card_name).first()
                        prev_deck.card = card
                elif card_name != '': # append deck
                    card = Card.query.filter(Card.name == card_name).first()
                    deck = MageStartingDeck(mage=mage, card=card, order=i)
                    db.session.add(deck)

            # 특수 카드 수정
            prev_specific_card_list = [specific.card.name for specific in mage.specific_card_list]
            modified_specific_card_list = request.form.get('specific_card_str', type=str, default='').split('|')[:-1]
            specific_card_union = list(set(prev_specific_card_list + modified_specific_card_list))

            for card_name in specific_card_union:
                card = Card.query.filter(Card.name == card_name).first()

                if card_name not in prev_specific_card_list:
                    specific = MageSpecificCard(mage=mage, card=card)
                    db.session.add(specific)
                elif card_name not in modified_specific_card_list:
                    specific = MageSpecificCard.query.filter(MageSpecificCard.mage == mage, MageSpecificCard.card == card).first()
                    db.session.delete(specific)

            db.session.commit()

            return redirect(url_for('wiki.mage_detail', mage_id=mage.id))
    else:
        form = MageForm(
            name=mage.name,
            name_en=mage_en.name,
            series=mage.series,
            series_en=mage_en.series,
            ability_name=mage.ability_name,
            ability_name_en=mage_en.ability_name,
            ability=mage.ability,
            ability_en=mage_en.ability,
            activation_time=mage.activation_time,
            activation_time_en=mage_en.activation_time,
            required_charges=mage.required_charges
        )

    card_list = Card.query.order_by(Card.cost, Card.name)
    specific_card_str = '|'.join([specific.card.name for specific in mage.specific_card_list]) + '|' if len(mage.specific_card_list) > 0 else ''
    starting_hand_dict, starting_deck_dict = {}, {}

    for hand in mage.starting_hand:
        starting_hand_dict[hand.order] = hand.card
    for deck in mage.starting_deck:
        starting_deck_dict[deck.order] = deck.card

    return render_template('wiki/wiki_mage_form.html',
                           form=form,
                           starting_hand_dict=starting_hand_dict, starting_deck_dict=starting_deck_dict,
                           card_list=card_list, specific_card_str=specific_card_str)


@bp.route('/modify/card/<int:card_id>', methods=['GET', 'POST'])
@login_required
def modify_card(card_id):
    card = Card.query.get_or_404(card_id)
    card_en = CardEN.query.filter(CardEN.card_id == card.id).first()

    if request.method == 'POST':
        form = CardForm()

        if form.validate_on_submit():
            # 카드의 영어 이름이 바뀌면 이전 이미지 파일 이름도 변경
            if 'defaults' not in card.image and form.name_en.data != card_en.name:
                prev_file_extension = os.path.basename(card.image).rsplit('.', 1)[1].lower()
                new_file_name = secure_filename(f"{form.name_en.data.lower()}.{prev_file_extension}")
                os.rename(os.path.join('./app/static', card.image), os.path.join(UPLOAD_FOLDER, 'card', new_file_name))

                card.image = f"images/card/{new_file_name}"

            if form.image.data is not None:
                file_extension = form.image.data.filename.rsplit('.', 1)[1].lower()
                file_name = secure_filename(f"{form.name_en.data.lower()}.{file_extension}")
                file_path = os.path.join(UPLOAD_FOLDER, 'card', file_name)

                form.image.data.save(file_path)
                card.image = f"images/card/{file_name}"

            card.name = form.name.data
            card.type = form.type.data
            card.cost = form.cost.data
            card.effect = form.effect.data

            card_en.name = form.name_en.data
            card_en.type = form.type_en.data
            card_en.effect = form.effect_en.data

            # 관련된 균열 마법사 목록 수정
            prev_related_mage_name_list = [mage.name for mage in card.related_mage]
            modified_related_mage_name_list = request.form.get('mage_relations', type=str, default='').split('|')[:-1]
            related_mage_name_union = prev_related_mage_name_list + modified_related_mage_name_list

            for mage_name in related_mage_name_union:
                mage = Mage.query.filter(Mage.name == mage_name).first()

                if mage_name not in modified_related_mage_name_list:
                    card.related_mage.remove(mage)
                elif mage_name not in prev_related_mage_name_list:
                    card.related_mage.append(mage)

            # 관련된 네메시스 목록 수정
            prev_related_nemesis_name_list = [nemesis.name for nemesis in card.related_nemesis]
            modified_related_nemesis_name_list = request.form.get('nemesis_relations', type=str, default='').split('|')[:-1]
            related_nemesis_name_union = list(set(prev_related_nemesis_name_list + modified_related_nemesis_name_list))

            for nemesis_name in related_nemesis_name_union:
                nemesis = Nemesis.query.filter(Nemesis.name == nemesis_name).first()

                if nemesis_name not in modified_related_nemesis_name_list:
                    card.related_nemesis.remove(nemesis)
                elif nemesis_name not in prev_related_nemesis_name_list:
                    card.related_nemesis.append(nemesis)

            db.session.commit()

            return redirect(url_for('wiki.card_detail', card_id=card_id))
    else:
        form = CardForm(
            name=card.name,
            name_en=card_en.name,
            type=card.type,
            type_en=card_en.type,
            cost=card.cost,
            effect=card.effect,
            effect_en=card_en.effect,
            image=card.image
        )

    mage_list = Mage.query.all()
    mage_list_str = '|'.join(mage.name for mage in card.related_mage) + '|' if len(card.related_mage) > 0 else ''
    nemesis_list = Nemesis.query.all()
    nemesis_list_str = '|'.join(nemesis.name for nemesis in card.related_nemesis) + '|' if len(card.related_nemesis) > 0 else ''

    return render_template('wiki/wiki_card_form.html',
                           form=form,
                           mage_list=mage_list, mage_list_str=mage_list_str,
                           nemesis_list=nemesis_list, nemesis_list_str=nemesis_list_str)
