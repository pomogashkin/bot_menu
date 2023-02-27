# -*- coding: utf-8 -*-

"""Telegram event handlers."""

import telegram

from telegram.ext import (
    Updater, Dispatcher, Filters,
    CommandHandler, MessageHandler,
    InlineQueryHandler, CallbackQueryHandler,
    ChosenInlineResultHandler, PollAnswerHandler,
)

from celery.decorators import task  # event processing in async mode

from dtb.settings import TELEGRAM_TOKEN

from tgbot.handlers import admin, commands, files, location
from tgbot.handlers.commands import broadcast_command_with_message
from tgbot.handlers import handlers as hnd
from tgbot.handlers import manage_data as md
from tgbot.handlers.static_text import broadcast_command


def setup_dispatcher(dp):
    """
    Adding handlers for events from Telegram
    """

    dp.add_handler(CommandHandler("start", commands.command_start))

    # admin commands
    dp.add_handler(CommandHandler("admin", admin.admin))
    dp.add_handler(CommandHandler("stats", admin.stats))
    dp.add_handler(
        CommandHandler(
            "become_an_admin",
            commands.command_go
        )
    )
    dp.add_handler(
        CommandHandler(
            "view_products",
            commands.view_products
        )
    )

    dp.add_handler(MessageHandler(
        Filters.animation, files.show_file_id,
    ))

    # base buttons

    dp.add_handler(CallbackQueryHandler(hnd.menu, pattern=f'^{md.MENU}'))
    dp.add_handler(CallbackQueryHandler(
        hnd.start_offer, pattern=f'^{md.OFFER}'))
    dp.add_handler(CallbackQueryHandler(
        hnd.ready, pattern=f'^{md.READY}'))
    dp.add_handler(CallbackQueryHandler(
        hnd.product_in_cart, pattern=f'^{md.PRODUCT_IN_CART}'))
    dp.add_handler(CallbackQueryHandler(
        hnd.back_to_menu, pattern=f'^{md.BACK_TO_MENU}'))
    dp.add_handler(CallbackQueryHandler(
        hnd.checkout, pattern=f'^{md.CHECKHOUT}'))
    dp.add_handler(CallbackQueryHandler(
        hnd.wait, pattern=f'^{md.WAIT}'))
    dp.add_handler(CallbackQueryHandler(
        hnd.delete, pattern=f'^{md.DELETE}'))
    dp.add_handler(MessageHandler(Filters.text, hnd.what))

    # location
    dp.add_handler(CommandHandler("ask_location", location.ask_for_location))
    dp.add_handler(MessageHandler(Filters.location, location.location_handler))

    dp.add_handler(MessageHandler(Filters.regex(
        rf'^{broadcast_command} .*'), broadcast_command_with_message))
    dp.add_handler(CallbackQueryHandler(
        hnd.broadcast_decision_handler, pattern=f"^{md.CONFIRM_DECLINE_BROADCAST}"))
    dp.add_handler(MessageHandler(
        Filters.document, files.show_file_id,
    ))
    dp.add_handler(MessageHandler(
        Filters.photo, files.show_file_id,
    ))

    # EXAMPLES FOR HANDLERS
    # dp.add_handler(MessageHandler(Filters.text, <function_handler>))
    # dp.add_handler(MessageHandler(
    #     Filters.document, <function_handler>,
    # ))
    # dp.add_handler(CallbackQueryHandler(<function_handler>, pattern="^r\d+_\d+"))
    # dp.add_handler(MessageHandler(
    #     Filters.chat(chat_id=int(TELEGRAM_FILESTORAGE_ID)),
    #     # & Filters.forwarded & (Filters.photo | Filters.video | Filters.animation),
    #     <function_handler>,
    # ))

    return dp


def run_pooling():
    """ Run bot in pooling mode """
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = telegram.Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f"https://t.me/" + bot_info["username"]

    print(f"Pooling of '{bot_link}' started")
    updater.start_polling(timeout=123)
    updater.idle()


@task(ignore_result=True)
def process_telegram_event(update_json):
    update = telegram.Update.de_json(update_json, bot)
    dispatcher.process_update(update)


# Global variable - best way I found to init Telegram bot
bot = telegram.Bot(TELEGRAM_TOKEN)
dispatcher = setup_dispatcher(Dispatcher(
    bot, None, workers=0, use_context=True))
TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
