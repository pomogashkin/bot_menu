"""
    Celery tasks. Some of them will be launched periodically from admin panel via django-celery-beat
"""

import datetime
import telegram
import time

from django.db.models import Q
from django.utils import timezone
from dtb.celery import app
from celery.utils.log import get_task_logger

from tgbot.handlers import keyboard_utils as kb
from tgbot.handlers.utils import send_message
from tgbot.models import (
    Arcgis,
    Poem,
    User
)
from tgbot.poetry import Poetry

logger = get_task_logger(__name__)


@app.task(name='send_offer', ignore_result=True)
def send_offer(text, user_id, code):
    """Рассылка новых стихов пользователям."""

    # Находим пользователей, которым будем слать стихи
    moders = User.objects.filter(is_moderator=True)
    for moder in moders:
        send_message(
            user_id=moder.user_id,
            text=text,
            reply_markup=kb.offer_ready(n_cols=2, user_id=user_id, code=code),
            parse_mode=telegram.ParseMode.MARKDOWN,
        )


def send_ready(text, chat_id, context, update, code):
    moders = User.objects.filter(is_moderator=True)
    for moder in moders:
        context.bot.edit_message_text(
            text=f'Отлично {code} - готов',
            chat_id=moder.user_id,
            message_id=update.callback_query.message.message_id)

    send_message(
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
            send_message(user_id=user_id, text=message,
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
