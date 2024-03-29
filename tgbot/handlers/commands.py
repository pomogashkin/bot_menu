# -*- coding: utf-8 -*-

import datetime
import logging
import re
import telegram
import os

from django.utils import timezone
from tgbot.handlers import static_text
from tgbot.models import User, Product
from tgbot.utils import extract_user_data_from_update
from tgbot.handlers import static_text as st
from tgbot.handlers import manage_data as md
from tgbot.handlers.keyboard_utils import make_keyboard_for_start_command, keyboard_confirm_decline_broadcasting
from tgbot.handlers.utils import handler_logging, send
from django.db.models import Q

logger = logging.getLogger('default')
logger.info("Command handlers check!")


@handler_logging()
def command_start(update, context):
    user, created = User.get_user_and_created(update, context)

    # if empty payload, check what was stored in DB
    payload = context.args[0] if context.args else user.deep_link

    text = f'{st.welcome}'

    user_id = extract_user_data_from_update(update)['user_id']
    context.bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=make_keyboard_for_start_command(),
        parse_mode=telegram.ParseMode.MARKDOWN
    )


@handler_logging()
def command_go(update, context):
    user_id = extract_user_data_from_update(update)['user_id']
    if context.args[0] == md.PASSWORD_ADMIN:
        User.objects.filter(user_id=user_id).update(is_admin=True)
        send(user_id=user_id, text='Теперь вы Администратор')
    if context.args[0] == md.PASSWORD_MODER:
        User.objects.filter(user_id=user_id).update(is_moderator=True)
        send(user_id=user_id, text='Теперь вы Модератор')


@handler_logging()
def view_products(update, context):
    print('go')
    user_id = extract_user_data_from_update(update)['user_id']
    products = ''
    if User.objects.filter(
        Q(is_admin=True) | Q(is_moderator=True), user_id=user_id
    ).exists():
        for product in Product.objects.all():
            products += (
                '•' +
                f' {product.name} {product.amount}' +
                f'{product.measurement_unit} - {product.cost}р' +
                f' (id:{product.pk})' + os.linesep
            )
        send(user_id=user_id, text=products)


def stats(update, context):
    """ Show help info about all secret admins commands """
    u = User.get_user(update, context)
    if not u.is_admin:
        return

    text = f"""
*Users*: {User.objects.count()}
*24h active*: {User.objects.filter(updated_at__gte=timezone.now() - datetime.timedelta(hours=24)).count()}
    """

    return update.message.reply_text(
        text,
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


def broadcast_command_with_message(update, context):
    """ Type /broadcast <some_text>. Then check your message in Markdown format and broadcast to users."""
    u = User.get_user(update, context)
    user_id = extract_user_data_from_update(update)['user_id']

    if not u.is_admin:
        text = static_text.broadcast_no_access
        markup = None

    else:
        text = f"{update.message.text.replace(f'{static_text.broadcast_command} ', '')}"
        markup = keyboard_confirm_decline_broadcasting()

    try:
        context.bot.send_message(
            text=text,
            chat_id=user_id,
            parse_mode=telegram.ParseMode.MARKDOWN,
            reply_markup=markup
        )
    except telegram.error.BadRequest as e:
        place_where_mistake_begins = re.findall(r"offset (\d{1,})$", str(e))
        text_error = static_text.error_with_markdown
        if len(place_where_mistake_begins):
            text_error += f"{static_text.specify_word_with_error}'{text[int(place_where_mistake_begins[0]):].split(' ')[0]}'"
        context.bot.send_message(
            text=text_error,
            chat_id=user_id
        )
