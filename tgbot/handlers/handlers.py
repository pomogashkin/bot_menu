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
from tgbot.handlers.utils import handler_logging, products_in_card
from tgbot.models import User, Product, ShoppingCart
from tgbot.poetry import Poetry
from tgbot.tasks import broadcast_message, send_offer, send_ready
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
    logger.info('Начинаем процесс добавления в избранное')
    user_id = extract_user_data_from_update(update)['user_id']
    user = User.get_user(update, context)

    categories = [product.category for product in Product.objects.all()]
    categories = list(set(categories))

    # Извлекаем ID стиха из колбека

    context.bot.edit_message_text(
        text='Целое меню',
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=kb.build_menu(user=user, categories=categories, n_cols=2),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


# @handler_logging()
# def product_offer(update, context):
#     user_id = extract_user_data_from_update(update)['user_id']
#     user = User.get_user(update, context)

#     query = update.callback_query
#     query.answer()
#     query_data = query.data.split('#')
#     category = query_data[1]
#     products = [product for product in Product.objects.filter(
#         category=category)]

#     context.bot.edit_message_text(
#         text='Продукты',
#         chat_id=user_id,
#         message_id=update.callback_query.message.message_id,
#         reply_markup=kb.build_menu(
#             category=category, products=products, n_cols=2),
#         parse_mode=telegram.ParseMode.MARKDOWN,
#     )


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
    in_cart = [cart.product.name for cart in ShoppingCart.objects.filter(
        user=user)]

    context.bot.edit_message_text(
        text=f'Продукты в корзине: {products_in_card(user)}',
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=kb.build_menu(
            user=user,
            category=query_data[1],
            products=products,
            n_cols=2),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


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


def checkout(update, context):
    user_id = extract_user_data_from_update(update)['user_id']
    user = User.get_user(update, context)

    in_cart = [cart.product.name for cart in ShoppingCart.objects.filter(
        user=user)]

    context.bot.edit_message_text(
        text=f'Продукты в корзине: {products_in_card(user)}',
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=kb.checkout_buttons(n_cols=2),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


def wait(update, context):
    user = User.get_user(update, context)
    user_id = extract_user_data_from_update(update)['user_id']
    numbers = [random.randint(0, 9) for i in range(4)]
    code = ''.join(str(number) for number in numbers)
    text = (f'Номер заказа: {code}' + os.linesep +
            f'Посетитель: {user}' + os.linesep +
            f'Заказ: {products_in_card(user)}' + os.linesep)

    context.bot.edit_message_text(
        text=(
            f'Ваш заказ номер {code} готовится. ' +
            f'Ожидайте вы заказали: {products_in_card(user)}'),
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        # reply_markup=kb.checkout_buttons(n_cols=2),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )

    send_offer(text, user_id, code)


def ready(update, context):
    query = update.callback_query
    query.answer()
    query_data = query.data.split('#')

    ShoppingCart.objects.filter(
        user=User.objects.get(user_id=query_data[1])).delete()

    text = f'Ваш заказ {query_data[2]} готов!'
    send_ready(
        text, chat_id=query_data[1], update=update, context=context, code=query_data[2])


@handler_logging()
def show_authors(update, context):
    user_id = extract_user_data_from_update(update)['user_id']
    user = User.get_user(update, context)

    query = update.callback_query
    query.answer()
    query_data = query.data.split('#')
    selected_char = query_data[1]

    poetry = Poetry(user)
    authors = poetry.get_authors(
        only_first_chars=False, last_name_first_char=selected_char)

    context.bot.edit_message_text(
        text=st.choose_author_full,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=kb.make_authors_keyboard(authors),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


@handler_logging()
def show_author_poems(update, context):
    user_id = extract_user_data_from_update(update)['user_id']
    user = User.get_user(update, context)

    query = update.callback_query
    query.answer()
    query_data = query.data.split('#')
    author = query_data[1]

    poetry = Poetry(user)
    poems = poetry.get_poems(author)
    logger.info(poems)

    context.bot.edit_message_text(
        text=st.choose_poem,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=kb.make_poems_keyboard(poems),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


@handler_logging()
def show_poem_by_id(update, context):
    user_id = extract_user_data_from_update(update)['user_id']
    user = User.get_user(update, context)

    query = update.callback_query
    query.answer()
    query_data = query.data.split('#')
    poem_id = query_data[1]

    poetry = Poetry(user)
    poem = poetry.get_poem_by_id(poem_id)

    context.bot.edit_message_text(
        text=poetry.format_poem(poem),
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=kb.make_btn_keyboard(),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


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


@handler_logging()
# callback_data: SECRET_LEVEL_BUTTON variable from manage_data.py
def secret_level(update, context):
    """ Pressed 'secret_level_button_text' after /start command"""
    user_id = extract_user_data_from_update(update)['user_id']
    text = "Congratulations! You've opened a secret room👁‍🗨. There is some information for you:\n" \
           "*Users*: {user_count}\n" \
           "*24h active*: {active_24}".format(
               user_count=User.objects.count(),
               active_24=User.objects.filter(
                   updated_at__gte=timezone.now() - datetime.timedelta(hours=24)).count()
           )

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
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
