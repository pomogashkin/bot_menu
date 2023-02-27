import logging
import telegram
import os
from collections import Counter

from functools import wraps
from dtb.settings import ENABLE_DECORATOR_LOGGING, TELEGRAM_TOKEN
from django.utils import timezone
from tgbot.models import UserActionLog, User, ShoppingCart
from telegram import MessageEntity

logger = logging.getLogger('default')


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


def handler_logging(action_name=None):
    """ Turn on this decorator via ENABLE_DECORATOR_LOGGING variable in dtb.settings """
    def decor(func):
        def handler(update, context, *args, **kwargs):
            user, _ = User.get_user_and_created(update, context)
            action = f"{func.__module__}.{func.__name__}" if not action_name else action_name
            try:
                text = update.message['text'] if update.message else ''
            except AttributeError:
                text = ''
            UserActionLog.objects.create(
                user_id=user.user_id, action=action, text=text, created_at=timezone.now())
            return func(update, context, *args, **kwargs)
        return handler if ENABLE_DECORATOR_LOGGING else func
    return decor


def products_in_card(user):
    offer = ''
    shopping_cart = ShoppingCart.objects.filter(
        user=user)
    in_cart = [cart.product.name for cart in shopping_cart]
    counter = Counter(in_cart)
    for product, count in counter.items():
        offer += '•' + ' ' + product + ' - ' + f'{count}x' + os.linesep
    offer += (
        f'Сумма заказа: {sum(cart.product.cost for cart in shopping_cart)}р'
    )
    return os.linesep + offer


def send(user_id, media=None, text=None, document=None, img=None, parse_mode=None, reply_markup=None, reply_to_message_id=None,
         disable_web_page_preview=None, entities=None, tg_token=TELEGRAM_TOKEN, m_id=None):
    bot = telegram.Bot(tg_token)
    m = None
    try:
        if entities:
            entities = [
                MessageEntity(type=entity['type'],
                              offset=entity['offset'],
                              length=entity['length']
                              )
                for entity in entities
            ]
        if img:
            m = bot.send_photo(
                chat_id=user_id,
                photo=img,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        if document:
            m = bot.send_document(
                chat_id=user_id,
                document=document,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
            )
        if text:
            m = bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id,
                disable_web_page_preview=disable_web_page_preview,
                entities=entities,
            )
        if media:
            m = bot.send_media_group(chat_id=user_id, media=media)
        m_id = m.message_id
    except telegram.error.Unauthorized:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = False
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = False
    else:
        success = True
        User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    if m_id:
        return m_id
    return success
