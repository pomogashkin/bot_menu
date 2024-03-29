"""
    Celery tasks. Some of them will be launched periodically from admin panel via django-celery-beat
"""

import datetime
from tgbot.handlers.keyboard_utils import checkout_buttons
import telegram
import time
import os

from django.db.models import Q
from django.utils import timezone
from tgbot.models import ShoppingCart
from tgbot.handlers.utils import products_in_card
from dtb.celery import app
from celery.utils.log import get_task_logger

from tgbot.handlers import keyboard_utils as kb
from tgbot.handlers import static_text as st
from tgbot.handlers.utils import send
from tgbot.models import (
    Arcgis,
    User
)
from dtb.settings import TELEGRAM_TOKEN, BANK_TOKEN
import tgbot.handlers.manage_data as md

moders_m_id = []

logger = get_task_logger(__name__)


@app.task(name='send_offer', ignore_result=True)
def send_offer(text, user_id, code):
    """Рассылка модераторам инфы о заказе"""

    moders = User.objects.filter(is_moderator=True)
    global moders_m_id
    for moder in moders:
        m = send(
            user_id=moder.user_id,
            text=text,
            reply_markup=kb.offer_ready(n_cols=2, user_id=user_id, code=code),
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        a = (moder.user_id, m, code)
        if a[1] is not False:
            moders_m_id.append(a)
        print(a)


@app.task(name='send_ready', ignore_result=True)
def send_ready(text, chat_id, context, update, code, token=TELEGRAM_TOKEN):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    global moders_m_id
    user = User.objects.get(
        user_id=chat_id)
    for element in moders_m_id:
        if element[2] == code:
            bot.edit_message_text(
                text=st.offer_ready.format(code, user, products_in_card(user)),
                chat_id=element[0],
                message_id=element[1])
    ShoppingCart.objects.filter(
        user=User.objects.get(user_id=chat_id)).delete()
    moders_m_id = []
    send(
        user_id=chat_id,
        text=text,
        reply_markup=kb.thanks(n_cols=2),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


@app.task(ignore_result=True)
def broadcast_message(user_ids, message, entities=None, sleep_between=0.4, parse_mode=None):
    """ It's used to broadcast message to big amount of users """
    logger.info(f"Going to send message: '{message}' to {len(user_ids)} users")

    for user_id in user_ids:
        try:
            send(user_id=user_id, text=message,
                 entities=entities, parse_mode=parse_mode)
            logger.info(f"Broadcast message was sent to {user_id}")
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}, reason: {e}")
        time.sleep(max(sleep_between, 0.1))

    logger.info("Broadcast finished!")


@app.task(ignore_result=True)
def save_data_from_arcgis(latitude, longitude, location_id):
    Arcgis.from_json(Arcgis.reverse_geocode(
        latitude, longitude), location_id=location_id)


@app.task(ignore_result=True)
def send_menu(user_id):
    media = []
    menu_list = [md.MENU_IMG_1, md.MENU_IMG_2]
    for number, file_id in enumerate(menu_list):
        media.append(telegram.InputMediaPhoto(
            media=file_id, caption="Афиша №" + str(number + 1)))

    send(user_id=user_id, media=media)


@app.task(ignore_result=True)
def send_afisha(user_id):
    media = []
    for number, file_id in enumerate(md.AFISHA):
        media.append(telegram.InputMediaPhoto(
            media=file_id, caption="Меню №" + str(number + 1)))

    send(user_id=user_id, media=media)


@app.task(ignore_result=True)
def send_pay(chat_id,
             title,
             description,
             payload,
             currency,
             prices,
             cost,
             provider_token=BANK_TOKEN,
             sleep_between=0.4):
    print('??')
    bot = telegram.Bot(TELEGRAM_TOKEN)
    try:
        bot.send_invoice(chat_id=chat_id,
                         title=title,
                         description=description,
                         payload=payload,
                         provider_token=provider_token,
                         currency=currency, prices=prices,
                         reply_markup=checkout_buttons(n_cols=1, cost=cost)
                         )
    except Exception as e:
        print(f"Failed to send message to {chat_id}, reason: {e}")
    time.sleep(max(sleep_between, 0.1))


def pre_checkout_query(query, sleep_between=0.4):
    bot = telegram.Bot(TELEGRAM_TOKEN)
    try:
        if query.invoice_payload != "Custom-Payload":
            print('???')
            bot.answer_pre_checkout_query(
                ok=False,
                error_message="Something went wrong...",
                pre_checkout_query_id=query.id,
            )
        else:
            bot.answer_pre_checkout_query(
                ok=True, pre_checkout_query_id=query.id)
    except Exception as e:
        print(f"Failed to send message to , reason: {e}")
    time.sleep(max(sleep_between, 0.1))
