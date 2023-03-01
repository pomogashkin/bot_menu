# -*- coding: utf-8 -*-
import os
import datetime
import logging
import telegram
import random

from django.utils import timezone

from tgbot.handlers import commands
from tgbot.handlers import static_text as st
from tgbot.handlers import manage_data as md
from tgbot.handlers import keyboard_utils as kb
from tgbot.handlers.utils import handler_logging, products_in_card, send
from tgbot.models import User, Product, ShoppingCart
from tgbot.tasks import broadcast_message, send_offer, send_ready, send_menu, send_afisha
from tgbot.utils import convert_2_user_time, extract_user_data_from_update, get_chat_id

logger = logging.getLogger('default')


@handler_logging()
def menu(update, context):
    user_id = extract_user_data_from_update(update)['user_id']
    user = User.get_user(update, context)

    context.bot.edit_message_text(
        text='Меню',
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=kb.make_keyboard_for_start_command(),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


@handler_logging()
def start_offer(update, context):
    logger.info('Старт заказа')
    user_id = extract_user_data_from_update(update)['user_id']
    user = User.get_user(update, context)
    text = ''

    categories = [product.category for product in Product.objects.all()]
    categories = list(set(categories))

    if ShoppingCart.objects.filter(user=user).exists():
        text = f'Продукты в корзине: {products_in_card(user)}'
    else:
        text = st.todays_offer
    send(
        text=text,
        user_id=user_id,
        reply_markup=kb.build_menu(user=user, categories=categories,
                                   n_cols=2),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


@handler_logging()
def product_in_cart(update, context):
    user_id = extract_user_data_from_update(update)['user_id']
    user = User.get_user(update, context)
    query = update.callback_query
    query.answer()
    query_data = query.data.split('#')

    if query_data[2] != 'None':
        ShoppingCart.objects.create(
            user=user, product=Product.objects.get(pk=query_data[2]))
    products = [product for product in Product.objects.filter(
        category=query_data[1])]

    context.bot.edit_message_text(
        text=f'Продукты в корзине: {products_in_card(user)}',
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=kb.build_menu(
            user=user,
            category=query_data[1],
            products=products,
            n_cols=1),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


@handler_logging()
def delete(update, context):
    user_id = extract_user_data_from_update(update)['user_id']
    user = User.get_user(update, context)
    query = update.callback_query
    query.answer()
    query_data = query.data.split('#')

    if query_data[1] != 'None':
        a = ShoppingCart.objects.filter(
            user=user, product=Product.objects.get(pk=int(query_data[1])))
        a[0].delete()
    in_cart = [cart.product for cart in ShoppingCart.objects.filter(
        user=user)]
    in_cart = list(set(in_cart))

    context.bot.edit_message_text(
        text=('Чтобы удалить продукт, нажмите на него,' + os.linesep +
              f' Продукты в корзине: {products_in_card(user)}'),
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=kb.delete_buttons(
            products=in_cart,
            user=user,
            n_cols=2),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


@handler_logging()
def back_to_menu(update, context):
    user_id = extract_user_data_from_update(update)['user_id']
    user = User.get_user(update, context)

    categories = [product.category for product in Product.objects.all()]
    categories = list(set(categories))

    in_cart = [cart.product.name for cart in ShoppingCart.objects.filter(
        user=user)]

    context.bot.edit_message_text(
        text=f'Продукты в корзине: {products_in_card(user)}',
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=kb.build_menu(user=user, categories=categories, n_cols=2),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


@handler_logging()
def checkout(update, context):
    user_id = extract_user_data_from_update(update)['user_id']
    user = User.get_user(update, context)

    if user.is_wait:
        context.bot.edit_message_text(
            text=st.is_wait.format(user.code),
            chat_id=user_id,
            message_id=update.callback_query.message.message_id,
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
    else:
        context.bot.edit_message_text(
            text=f'Продукты в корзине: {products_in_card(user)}',
            chat_id=user_id,
            message_id=update.callback_query.message.message_id,
            reply_markup=kb.checkout_buttons(n_cols=2),
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        User.objects.filter(user_id=user_id).update(is_wait=True)


@handler_logging()
def wait(update, context):
    user = User.get_user(update, context)
    user_id = extract_user_data_from_update(update)['user_id']
    numbers = [random.randint(0, 9) for i in range(4)]
    code = ''.join(str(number) for number in numbers)
    text = st.new_offer.format(code, user, products_in_card(user))

    context.bot.edit_message_text(
        text=(
            f'Ваш заказ номер {code} готовится. ' +
            f'Ожидайте вы заказали: {products_in_card(user)}'),
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        # reply_markup=kb.checkout_buttons(n_cols=2),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )
    User.objects.filter(user_id=user_id).update(code=int(code))

    send_offer(text, user_id, code)


@handler_logging()
def ready(update, context):
    query = update.callback_query
    query.answer()
    query_data = query.data.split('#')

    User.objects.filter(user_id=int(query_data[1])).update(
        code=None, is_wait=False)

    text = f'Ваш заказ {query_data[2]} готов!'
    send_ready(
        text, chat_id=query_data[1], update=update, context=context, code=query_data[2])


@handler_logging()
# callback_data: BUTTON_BACK_IN_PLACE variable from manage_data.py
def back_to_main_menu_handler(update, context):
    user, created = User.get_user_and_created(update, context)

    # if empty payload, check what was stored in DB
    payload = context.args[0] if context.args else user.deep_link
    text = st.welcome

    user_id = extract_user_data_from_update(update)['user_id']
    context.bot.edit_message_text(
        chat_id=user_id,
        text=text,
        message_id=update.callback_query.message.message_id,
        reply_markup=kb.make_keyboard_for_start_command(),
        parse_mode=telegram.ParseMode.MARKDOWN
    )


# callback_data: CONFIRM_DECLINE_BROADCAST variable from manage_data.py
def broadcast_decision_handler(update, context):
    """ Entered /broadcast <some_text>.
        Shows text in Markdown style with two buttons:
        Confirm and Decline
    """
    broadcast_decision = update.callback_query.data[len(
        md.CONFIRM_DECLINE_BROADCAST):]
    entities_for_celery = update.callback_query.message.to_dict().get('entities')
    entities = update.callback_query.message.entities
    text = update.callback_query.message.text
    if broadcast_decision == md.CONFIRM_BROADCAST:
        admin_text = st.msg_sent,
        user_ids = list(User.objects.all().values_list('user_id', flat=True))
        broadcast_message.delay(
            user_ids=user_ids, message=text, entities=entities_for_celery)
    else:
        admin_text = text

    context.bot.edit_message_text(
        text=admin_text,
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        entities=None if broadcast_decision == md.CONFIRM_BROADCAST else entities
    )


def what(update, context):
    user_id = extract_user_data_from_update(update)['user_id']
    text = update.message.text
    if text == st.menu:
        send_menu(user_id=user_id)
    if text == st.offer:
        start_offer(update, context)
    if text == st.afisha:
        send_afisha(user_id=user_id)
