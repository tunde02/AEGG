import os

from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect, secure_filename

from app import db
from app.forms import CardForm
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
    # TODO
    print('APPEND MAGE')
    return redirect(url_for('wiki.wiki_list', wiki_type='mage'))


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


@bp.route('/modify/card/<int:card_id>', methods=['GET', 'POST'])
@login_required
def modify_card(card_id):
    card = Card.query.get_or_404(card_id)
    card_en = CardEN.query.filter(CardEN.card_id == card.id).first()

    if request.method == 'POST':
        form = CardForm()

        if form.validate_on_submit():
            # 카드의 영어 이름이 바뀌면 이전 이미지 파일 이름도 변경
            if form.name_en.data != card_en.name:
                prev_file_extension = os.path.basename(card.image).rsplit('.', 1)[1].lower()
                prev_file_name = secure_filename(f"{form.name_en.data.lower()}.{prev_file_extension}")
                os.rename(os.path.join('./app/static', card.image), os.path.join(UPLOAD_FOLDER, 'card', prev_file_name))

                card.image = f"images/card/{prev_file_name}"

            if form.image.data is not None:
                file_extension = form.image.data.filename.rsplit('.', 1)[1].lower()
                file_name = secure_filename(f"{form.name_en.data.lower()}.{file_extension}")
                file_path = os.path.join(UPLOAD_FOLDER, 'card', file_name)

                form.image.data.save(file_path)
                form.image.data = f"images/card/{file_name}"
            else:
                form.image.data = card.image

            card.name = form.name.data
            card.type = form.type.data
            card.cost = form.cost.data
            card.effect = form.effect.data
            card.image = form.image.data

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

            db.session.add(card)
            db.session.add(card_en)
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
