import os

from flask import Blueprint, render_template, request, url_for, g
from werkzeug.utils import redirect, secure_filename

from app import db
from app.forms import CardForm, MageForm, NemesisForm
from app.models import *
from app.views.auth_views import login_required
from config.default import UPLOAD_FOLDER


bp = Blueprint('wiki', __name__, url_prefix='/wiki')


def update_related_mage(mage):
    prev_related_cards = mage.related_card_list
    actual_related_cards = Card.query.outerjoin(NemesisCardInfo, NemesisCardInfo.card_id == Card.id) \
                                     .filter(NemesisCardInfo.card_id == None) \
                                     .outerjoin(MageStartingHand, MageStartingHand.card_id == Card.id) \
                                     .outerjoin(MageStartingDeck, MageStartingDeck.card_id == Card.id) \
                                     .outerjoin(MageSpecificCard, MageSpecificCard.card_id == Card.id) \
                                     .filter((MageStartingHand.mage_id == mage.id) |
                                             (MageStartingDeck.mage_id == mage.id) |
                                             (MageSpecificCard.mage_id == mage.id)).all()
    related_card_union = list(set(prev_related_cards + actual_related_cards))

    for card in related_card_union:
        if card.name in ['크리스탈', '스파크']:
            continue

        if card not in prev_related_cards:
            card.related_mage.append(mage)
        elif card not in actual_related_cards:
            card.related_mage.remove(mage)


def save_image(image_data, file_name, save_folder):
    file_extension = image_data.filename.rsplit('.', 1)[1].lower()
    full_file_name = secure_filename(f"{file_name}.{file_extension}")
    file_path = os.path.join(UPLOAD_FOLDER, save_folder, full_file_name)

    image_data.save(file_path)

    return f"images/{save_folder}/{full_file_name}"


def modify_image_name(prev_file_path, file_name, save_folder):
    prev_file_extension = os.path.basename(prev_file_path).rsplit('.', 1)[1].lower()
    new_full_file_name = secure_filename(f"{file_name}.{prev_file_extension}")

    os.rename(os.path.join('./app/static', prev_file_path), os.path.join(UPLOAD_FOLDER, save_folder, new_full_file_name))

    return f"images/{save_folder}/{new_full_file_name}"


@bp.before_request
def load_navbar_tab():
    g.navbar_tab = 'wiki'
    if g.user:
        g.num_notifications = len(PostNotification.query.filter_by(user=g.user, is_checked=False).all()) + len(CommentNotification.query.filter_by(user=g.user, is_checked=False).all())


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

    return render_template('wiki/wiki_list.html', wiki_type=wiki_type,
                           wiki_list=wiki_info_list, wiki_en_list=wiki_info_en_list)


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

    return render_template('wiki/mage_detail.html', wiki_type='mage',
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

    # 네메시스 카드 여부
    is_nemesis_card = True if NemesisCardInfo.query.filter(NemesisCardInfo.card_id == card.id).first() else False

    related_mage_list = Mage.query.join(related_mage, related_mage.c.mage_id == Mage.id).filter(related_mage.c.card_id == card.id).all()
    related_nemesis_list = Nemesis.query.join(related_nemesis, related_nemesis.c.nemesis_id == Nemesis.id).filter(related_nemesis.c.card_id == card.id).all()

    return render_template('wiki/card_detail.html', wiki_type='card',
                           card=card, card_en=card_en, is_nemesis_card=is_nemesis_card,
                           review_list=card_review_list, already_reviewed=already_reviewed,
                           related_mage_list=related_mage_list, related_nemesis_list=related_nemesis_list)


@bp.route('/detail/nemesis/<int:nemesis_id>')
def nemesis_detail(nemesis_id):
    nemesis = Nemesis.query.get_or_404(nemesis_id)
    nemesis_en = NemesisEN.query.filter(NemesisEN.nemesis_id == nemesis.id).first()
    nemesis_review_list = NemesisReview.query.filter(NemesisReview.nemesis_id == nemesis.id).order_by(NemesisReview.create_date.asc()).all()

    # 각 네메시스에 대한 리뷰는 계정당 한 번씩만 가능하도록 제한
    already_reviewed = True if g.user and NemesisReview.query.filter(NemesisReview.nemesis_id == nemesis.id, NemesisReview.user == g.user).first() else False

    # 네메시스 전용 카드 목록
    nemesis_private_card_list = Card.query.join(CardEN, CardEN.card_id == Card.id) \
                                  .join(NemesisCardInfo, NemesisCardInfo.card_id == Card.id) \
                                  .join(related_nemesis, related_nemesis.c.card_id == Card.id) \
                                  .outerjoin(NemesisSpecificCard, NemesisSpecificCard.card_id == Card.id) \
                                  .filter(NemesisSpecificCard.nemesis_id == None) \
                                  .filter(related_nemesis.c.nemesis_id == nemesis.id) \
                                  .order_by(NemesisCardInfo.tier.asc(), CardEN.name.asc()).all()

    # 네메시스 특수 카드 목록
    nemesis_specific_card_list = Card.query.join(CardEN, CardEN.card_id == Card.id) \
                                           .join(NemesisCardInfo, NemesisCardInfo.card_id == Card.id) \
                                           .join(NemesisSpecificCard, NemesisSpecificCard.card_id == Card.id) \
                                           .filter(NemesisSpecificCard.nemesis_id == nemesis.id) \
                                           .order_by(NemesisCardInfo.tier.asc(), CardEN.name.asc()).all()

    return render_template('wiki/nemesis_detail.html', wiki_type='nemesis',
                           nemesis=nemesis, nemesis_en=nemesis_en,
                           nemesis_private_card_list=nemesis_private_card_list, nemesis_specific_card_list=nemesis_specific_card_list,
                           review_list=nemesis_review_list, already_reviewed=already_reviewed)


@bp.route('/append/mage', methods=['GET', 'POST'])
@login_required
def append_mage():
    form = MageForm()

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

        # 이미지 파일 저장
        file_name = f"{form.name_en.data.lower()}_{form.series_en.data.lower()}"
        if form.image.data is not None:
            mage.image = save_image(form.image.data, file_name, 'mage/icon')

        if form.board_image.data is not None:
            mage.board_image = save_image(form.board_image.data, file_name, 'mage/board')

        if form.back_board_image.data is not None:
            mage.back_board_image = save_image(form.back_board_image.data, f"{file_name}_back", 'mage/board')

        # 시작 패
        for i in range(5):
            card_name = request.form.get(f'starting_hand_{i}', type=str, default='')
            if card_name != '':
                card = Card.query.filter(Card.name == card_name).first()
                card.related_mage.append(mage)
                hand = MageStartingHand(mage=mage, card=card, order=i)
                db.session.add(hand)

        # 시작 덱
        for i in range(5):
            card_name = request.form.get(f'starting_deck_{i}', type=str, default='')
            if card_name == '':
                card = Card.query.filter(Card.name == card_name).first()
                card.related_mage.append(mage)
                deck = MageStartingDeck(mage=mage, card=card, order=i)
                db.session.add(deck)

        # 특수 카드
        specific_card_name_list = request.form.get('specific_card_str', type=str, default='').split('|')[:-1]
        for card_name in specific_card_name_list:
            card = Card.query.filter(Card.name == card_name).first()
            card.related_mage.append(mage)
            specific_card = MageSpecificCard(mage=mage, card=card)
            db.session.add(specific_card)

        db.session.add(mage)
        db.session.add(mage_en)
        db.session.commit()

        return redirect(url_for('wiki.wiki_list', wiki_type='mage'))

    card_list = Card.query.join(CardEN, CardEN.card_id == Card.id) \
                          .outerjoin(NemesisCardInfo, NemesisCardInfo.card_id == Card.id) \
                          .filter(NemesisCardInfo.card_id == None) \
                          .order_by(Card.cost, CardEN.name).all()

    return render_template('wiki/mage_form.html', form=form, card_list=card_list)


@bp.route('/append/card', methods=['GET', 'POST'])
@login_required
def append_card():
    form = CardForm()

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

        # 네메시스 카드 정보
        if request.form.get('is_nemesis_card', type=str, default='false') == 'true':
            nemesis_card_info = NemesisCardInfo(card=card, tier=form.tier.data, hp=form.hp.data)
            db.session.add(nemesis_card_info)

        # 이미지 파일 저장
        if form.image.data is not None:
            card.image = save_image(form.image.data, form.name_en.data.lower(), 'card')

        db.session.add(card)
        db.session.add(card_en)
        db.session.commit()

        return redirect(url_for('wiki.wiki_list', wiki_type='card'))

    return render_template('wiki/card_form.html', form=form)


@bp.route('/append/nemesis', methods=['GET', 'POST'])
@login_required
def append_nemesis():
    form = NemesisForm()
    card_list = Card.query.join(NemesisCardInfo, NemesisCardInfo.card_id == Card.id) \
                          .outerjoin(related_nemesis, related_nemesis.c.card_id == Card.id) \
                          .filter(related_nemesis.c.nemesis_id == None) \
                          .order_by(NemesisCardInfo.tier.asc(), Card.name.asc()).all()

    if request.method == 'POST' and form.validate_on_submit():
        nemesis = Nemesis(
            name=form.name.data,
            series=form.series.data,
            tier=form.tier.data,
            difficulty=form.difficulty.data,
            hp=form.hp.data,
            setup=form.setup.data,
            additional_rules=form.additional_rules.data,
            unleash=form.unleash.data,
            increased_diff=form.increased_diff.data
        )
        nemesis_en = NemesisEN(
            nemesis=nemesis,
            name=form.name_en.data,
            series=form.series_en.data,
            setup=form.setup_en.data,
            additional_rules=form.additional_rules_en.data,
            unleash=form.unleash_en.data,
            increased_diff=form.increased_diff_en.data
        )

        # 이미지 파일 저장
        file_name = form.name_en.data.lower()
        if form.image.data is not None:
            nemesis.image = save_image(form.image.data, file_name, 'nemesis/icon')

        if form.board_image.data is not None:
            nemesis.board_image = save_image(form.board_image.data, file_name, 'nemesis/board')

        if form.back_board_image.data is not None:
            nemesis.back_board_image = save_image(form.back_board_image.data, f"{file_name}_back", 'nemesis/board')

        # 전용 카드
        private_card_list = request.form.get('private_card_str', type=str, default='').split('|')[:-1]
        for card_name in private_card_list:
            card = Card.query.filter(Card.name == card_name).first()
            card.related_nemesis.append(nemesis)

        # 특수 카드
        specific_card_list = request.form.get('specific_card_str', type=str, default='').split('|')[:-1]
        for card_name in specific_card_list:
            card = Card.query.filter(Card.name == card_name).first()
            card.related_nemesis.append(nemesis)
            specific_card = NemesisSpecificCard(nemesis=nemesis, card=card)
            db.session.add(specific_card)

        db.session.add(nemesis)
        db.session.add(nemesis_en)
        db.session.commit()

        return redirect(url_for('wiki.wiki_list', wiki_type='nemesis'))

    return render_template('wiki/nemesis_form.html', form=form, card_list=card_list)


@bp.route('/modify/mage/<int:mage_id>', methods=['GET', 'POST'])
@login_required
def modify_mage(mage_id):
    mage = Mage.query.get_or_404(mage_id)
    mage_en = MageEN.query.filter(MageEN.mage_id == mage.id).first()

    if request.method == 'POST':
        form = MageForm()

        if form.validate_on_submit():
            same_name_mage = MageEN.query.filter((MageEN.name == form.name_en.data) &
                                                 (MageEN.mage != mage)).first()
            if same_name_mage and '(' not in form.name_en.data:
                form.name.data = f"{form.name.data} ({form.series_en.data})"
                form.name_en.data = f"{form.name_en.data} ({form.series_en.data})"

            # 균열 마법사 이름 (English)이 바뀌면 이미지 파일 이름들도 수정
            file_name = form.name_en.data.lower()
            if form.name_en.data != mage_en.name or form.series_en.data != mage_en.series:
                mage.board_image = modify_image_name(mage.board_image, file_name, 'mage/board')
                if 'defaults' not in mage.image:
                    mage.image = modify_image_name(mage.image, file_name, 'mage/icon')

                if 'defaults' not in mage.board_image:
                    mage.board_image = modify_image_name(mage.board_image, file_name, 'mage/board')

                if 'defaults' not in mage.back_board_image:
                    mage.back_board_image = modify_image_name(mage.back_board_image, f"{file_name}_back", 'mage/board')

            # 이미지 파일 수정
            if form.image.data is not None:
                mage.image = save_image(form.image.data, file_name, 'mage/icon')

            if form.board_image.data is not None:
                mage.board_image = save_image(form.board_image.data, file_name, 'mage/board')

            if form.back_board_image.data is not None:
                mage.back_board_image = save_image(form.back_board_image.data, f"{file_name}_back", 'mage/board')

            mage.name               = form.name.data
            mage.series             = form.series.data
            mage.ability_name       = form.ability_name.data
            mage.ability            = form.ability.data
            mage.activation_time    = form.activation_time.data
            mage.required_charges   = form.required_charges.data

            mage_en.name            = form.name_en.data
            mage_en.series          = form.series_en.data
            mage_en.ability_name    = form.ability_name_en.data
            mage_en.ability         = form.ability_en.data
            mage_en.activation_time = form.activation_time_en.data

            # 시작 패 수정
            for i in range(5):
                card_name = request.form.get(f'starting_hand_{i}', type=str, default='')
                card = Card.query.filter(Card.name == card_name).first()
                prev_hand = MageStartingHand.query.filter(MageStartingHand.mage_id == mage.id, MageStartingHand.order == i).first()

                if prev_hand is not None:
                    if card_name == '': # delete hand
                        db.session.delete(prev_hand)
                    elif card_name != prev_hand.card.name: # modify hand
                        prev_hand.card = card
                elif card_name != '': # append hand
                    hand = MageStartingHand(mage=mage, card=card, order=i)
                    db.session.add(hand)

            # 시작 덱 수정
            for i in range(5):
                card_name = request.form.get(f'starting_deck_{i}', type=str, default='')
                card = Card.query.filter(Card.name == card_name).first()
                prev_deck = MageStartingDeck.query.filter(MageStartingDeck.mage_id == mage.id, MageStartingDeck.order == i).first()

                if prev_deck is not None:
                    if card_name == '': # delete deck
                        db.session.delete(prev_deck)
                    elif card_name != prev_deck.card.name: # modify deck
                        prev_deck.card = card
                elif card_name != '': # append deck
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

            update_related_mage(mage)
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

    card_list = Card.query.join(CardEN, CardEN.card_id == Card.id) \
                          .outerjoin(NemesisCardInfo, NemesisCardInfo.card_id == Card.id) \
                          .filter(NemesisCardInfo.card_id == None) \
                          .order_by(Card.cost, CardEN.name).all()
    specific_card_str = '|'.join([specific.card.name for specific in mage.specific_card_list]) + ('|' if len(mage.specific_card_list) > 0 else '')

    starting_hand_dict, starting_deck_dict = {}, {}
    for hand in mage.starting_hand:
        starting_hand_dict[hand.order] = hand.card
    for deck in mage.starting_deck:
        starting_deck_dict[deck.order] = deck.card

    return render_template('wiki/mage_form.html',
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
            # 카드 이름 (English)이 바뀌면 이전 이미지 파일 이름도 수정
            if 'defaults' not in card.image and form.name_en.data != card_en.name:
                card.image = modify_image_name(card.image, form.name_en.data.lower(), 'card')

            # 이미지 파일 수정
            if form.image.data is not None:
                card.image = save_image(form.image.data, form.name_en.data.lower(), 'card')

            card.name = form.name.data
            card.type = form.type.data
            card.cost = form.cost.data
            card.effect = form.effect.data

            card_en.name = form.name_en.data
            card_en.type = form.type_en.data
            card_en.effect = form.effect_en.data

            # 네메시스 카드 정보
            prev_nemesis_card_info = NemesisCardInfo.query.filter(NemesisCardInfo.card_id == card.id).first()
            _is_nemesis_card = request.form.get('is_nemesis_card', type=str, default='false') == 'true'

            if prev_nemesis_card_info and _is_nemesis_card: # modify NemesisCardInfo
                prev_nemesis_card_info.tier = form.tier.data
                prev_nemesis_card_info.hp = form.hp.data
            elif prev_nemesis_card_info and not _is_nemesis_card: # delete NemesisCardInfo
                db.session.delete(prev_nemesis_card_info)
            elif not prev_nemesis_card_info and _is_nemesis_card: # create NemesisCardInfo
                nemesis_card_info = NemesisCardInfo(card=card, tier=form.tier.data, hp=form.hp.data)
                db.session.add(nemesis_card_info)

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

    # 네메시스 카드 여부
    is_nemesis_card = 'true' if NemesisCardInfo.query.filter(NemesisCardInfo.card_id == card.id).first() else 'false'

    if is_nemesis_card == 'true':
        form.tier.data = card.nemesis_card_info[0].tier
        form.hp.data = card.nemesis_card_info[0].hp

    return render_template('wiki/card_form.html', form=form, is_nemesis_card=is_nemesis_card)


@bp.route('/modify/nemesis/<int:nemesis_id>', methods=['GET', 'POST'])
@login_required
def modify_nemesis(nemesis_id):
    nemesis = Nemesis.query.get_or_404(nemesis_id)
    nemesis_en = NemesisEN.query.filter(NemesisEN.nemesis_id == nemesis.id).first()
    private_card_list = Card.query.join(NemesisCardInfo, NemesisCardInfo.card_id == Card.id) \
                                  .join(related_nemesis, related_nemesis.c.card_id == Card.id) \
                                  .outerjoin(NemesisSpecificCard, NemesisSpecificCard.card_id == Card.id) \
                                  .filter(NemesisSpecificCard.nemesis_id == None) \
                                  .filter(related_nemesis.c.nemesis_id == nemesis.id).all()

    if request.method == 'POST':
        form = NemesisForm()

        if form.validate_on_submit():
            file_name = f"{form.name_en.data.lower()}"

            # 네메시스 이름 (English)이 바뀌면 이미지 파일 이름들도 수정
            if form.name_en.data != nemesis_en.name:
                if 'defaults' not in nemesis.image:
                    nemesis.image = modify_image_name(nemesis.image, file_name, 'nemesis/icon')

                if 'defaults' not in nemesis.board_image:
                    nemesis.board_image = modify_image_name(nemesis.board_image, file_name, 'nemesis/board')

                if 'defaults' not in nemesis.back_board_image:
                    nemesis.board_image = modify_image_name(nemesis.board_image, f"{file_name}_back", 'nemesis/board')

            # 이미지 파일 수정
            if form.image.data is not None:
                nemesis.image = save_image(form.image.data, file_name, 'nemesis/icon')

            if form.board_image.data is not None:
                nemesis.board_image =save_image(form.board_image.data, file_name, 'nemesis/board')

            if form.back_board_image.data is not None:
                nemesis.back_board_image = save_image(form.back_board_image, f"{file_name}_back", 'nemesis/board')

            nemesis.name                = form.name.data
            nemesis.series              = form.series.data
            nemesis.tier                = form.tier.data
            nemesis.difficulty          = form.difficulty.data
            nemesis.hp                  = form.hp.data
            nemesis.setup               = form.setup.data
            nemesis.additional_rules    = form.additional_rules.data
            nemesis.unleash             = form.unleash.data
            nemesis.increased_diff      = form.increased_diff.data

            nemesis_en.name             = form.name_en.data
            nemesis_en.series           = form.series_en.data
            nemesis_en.setup            = form.setup_en.data
            nemesis_en.additional_rules = form.additional_rules_en.data
            nemesis_en.unleash          = form.unleash_en.data
            nemesis_en.increased_diff   = form.increased_diff_en.data

            # 전용 카드 수정
            prev_private_card_list = [private_card.name for private_card in private_card_list]
            modified_private_card_list = request.form.get('private_card_str', type=str, default='').split('|')[:-1]
            private_card_union = list(set(prev_private_card_list + modified_private_card_list))

            for card_name in private_card_union:
                card = Card.query.filter(Card.name == card_name).first()

                if card_name not in prev_private_card_list:
                    card.related_nemesis.append(nemesis)
                elif card_name not in modified_private_card_list:
                    card.related_nemesis.remove(nemesis)

            # 특수 카드 수정
            prev_specific_card_list = [specific.card.name for specific in nemesis.specific_card_list]
            modified_specific_card_list = request.form.get('specific_card_str', type=str, default='').split('|')[:-1]
            specific_card_union = list(set(prev_specific_card_list + modified_specific_card_list))

            for card_name in specific_card_union:
                card = Card.query.filter(Card.name == card_name).first()

                if card_name not in prev_specific_card_list:
                    specific = NemesisSpecificCard(nemesis=nemesis, card=card)
                    card.related_nemesis.append(nemesis)
                    db.session.add(specific)
                elif card_name not in modified_specific_card_list:
                    specific = NemesisSpecificCard.query.filter(NemesisSpecificCard.nemesis == nemesis, NemesisSpecificCard.card == card).first()
                    card.related_nemesis.remove(nemesis)
                    db.session.delete(specific)

            db.session.commit()

            return redirect(url_for('wiki.nemesis_detail', nemesis_id=nemesis.id))
    else:
        form = NemesisForm(
            name=nemesis.name,
            name_en=nemesis_en.name,
            series=nemesis.series,
            series_en=nemesis_en.series,
            tier=nemesis.tier,
            difficulty=nemesis.difficulty,
            hp=nemesis.hp,
            setup=nemesis.setup,
            setup_en=nemesis_en.setup,
            additional_rules=nemesis.additional_rules,
            additional_rules_en=nemesis_en.additional_rules,
            unleash=nemesis.unleash,
            unleash_en=nemesis_en.unleash,
            increased_diff=nemesis.increased_diff,
            increased_diff_en=nemesis_en.increased_diff
        )

    card_list = Card.query.join(CardEN, CardEN.card_id == Card.id) \
                          .join(NemesisCardInfo, NemesisCardInfo.card_id == Card.id) \
                          .outerjoin(related_nemesis, related_nemesis.c.card_id == Card.id) \
                          .filter((related_nemesis.c.nemesis_id == nemesis.id) |
                                  (related_nemesis.c.nemesis_id == None)) \
                          .order_by(NemesisCardInfo.tier.asc(), CardEN.name.asc()).all()

    private_card_str = '|'.join([private_card.name for private_card in private_card_list]) +('|' if len(private_card_list) > 0 else '')
    specific_card_str = '|'.join([specific.card.name for specific in nemesis.specific_card_list]) + ('|' if len(nemesis.specific_card_list) > 0 else '')

    return render_template('wiki/nemesis_form.html',
                           form=form, card_list=card_list,
                           private_card_str=private_card_str, specific_card_str=specific_card_str)
