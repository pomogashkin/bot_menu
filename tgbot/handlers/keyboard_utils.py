# -*- coding: utf-8 -*-

import copy

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Iterable

from tgbot.handlers import manage_data as md
from tgbot.handlers import static_text as st
from tgbot.models import Favourite, ShoppingCart


def make_btn_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                st.go_back, callback_data=f'{md.BUTTON_BACK_IN_PLACE}'),
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_start_command():
    buttons = [
        [
            InlineKeyboardButton(st.menu, callback_data=f'{md.MENU}'),
            InlineKeyboardButton(
                st.offer, callback_data=f'{md.OFFER}'),
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def keyboard_confirm_decline_broadcasting():
    buttons = [[
        InlineKeyboardButton(
            st.confirm_broadcast, callback_data=f'{md.CONFIRM_DECLINE_BROADCAST}{md.CONFIRM_BROADCAST}'),
        InlineKeyboardButton(
            st.decline_broadcast, callback_data=f'{md.CONFIRM_DECLINE_BROADCAST}{md.DECLINE_BROADCAST}')
    ]]

    return InlineKeyboardMarkup(buttons)


def make_alphabetical_keyboard(alphabet: [str], selected_char: str = None):
    """Получает список букв сортированных по алфавиту и делает из них клавиатуру."""

    buttons = []
    char_index = 0
    button_row = []
    for cur_char in alphabet:
        out_char = f'-{cur_char}-' if cur_char == selected_char else cur_char
        button_row.append(InlineKeyboardButton(
            out_char, callback_data=f'{md.AUTHOR_BTN}#{cur_char}'))
        char_index += 1
        if char_index % 10 == 0:
            buttons.append(button_row)
            button_row = []
    if button_row:
        buttons.append(button_row)

    buttons.append([
        InlineKeyboardButton(
            st.go_back, callback_data=f'{md.BUTTON_BACK_IN_PLACE}')
    ])

    return InlineKeyboardMarkup(buttons)


def make_authors_keyboard(authors: [str]):
    """Получает списк авторов и делает из них клавиатуру."""

    buttons = []
    btn_row = []
    i = 1
    for author in authors:
        callback_key = author
        label = author if len(author) <= 30 else f'{author[0:27]}...'
        btn_row.append(InlineKeyboardButton(
            label, callback_data=f'{md.POEMS_BY_AUTHOR}#{callback_key}'))

        if not i % 3:
            buttons.append(btn_row)
            btn_row = []

        i += 1
    if btn_row:
        buttons.append(btn_row)

    buttons.append([
        InlineKeyboardButton(
            st.go_back, callback_data=f'{md.BUTTON_BACK_IN_PLACE}')
    ])

    return InlineKeyboardMarkup(buttons)


def make_poems_keyboard(favourites: Iterable[Favourite]):
    """Получает список названий стихов и делает из них клавиатуру."""

    buttons = []
    btn_row = []
    i = 1
    for favourite in favourites:
        label = favourite.poem.header if len(
            favourite.poem.header) <= 30 else f'{favourite.poem.header[0:27]}...'
        callback_key = favourite.poem.id
        btn_row.append(InlineKeyboardButton(
            label, callback_data=f'{md.POEM_BY_NAME}#{callback_key}'))

        if not i % 3:
            buttons.append(btn_row)
            btn_row = []

        i += 1
    if btn_row:
        buttons.append(btn_row)

    buttons.append([
        InlineKeyboardButton(
            st.go_back, callback_data=f'{md.BUTTON_BACK_IN_PLACE}')
    ])

    return InlineKeyboardMarkup(buttons)


def build_menu(
        n_cols,
        user=None,
        category=None,
        products=None,
        categories=None,
        header_buttons=None,
        footer_buttons=None):
    menu = []
    if categories:
        buttons = [
            InlineKeyboardButton(
                f'{category}',
                callback_data=(
                    f'{md.PRODUCT_IN_CART}#{category}#None')
            ) for category in categories
        ]
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if products:
        buttons = [
            InlineKeyboardButton(
                f'{product.name} - {product.cost}р',
                callback_data=(
                    f'{md.PRODUCT_IN_CART}#{category}#{product.pk}'
                )) for product in products
        ]
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        menu.append([InlineKeyboardButton('К началу меню',
                     callback_data=md.BACK_TO_MENU)])
    if ShoppingCart.objects.filter(user=user).exists():
        menu.append([InlineKeyboardButton('Оформить заказ',
                                          callback_data=f'{md.CHECKHOUT}'),
                     InlineKeyboardButton('Удалить',
                                          callback_data=f'{md.DELETE}#None')])
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return InlineKeyboardMarkup(menu)


def delete_buttons(n_cols, products, user):
    buttons = [
        InlineKeyboardButton(
            f'{product.name} - {product.cost}р',
            callback_data=(
                f'{md.DELETE}#{product.pk}'
            )) for product in products
    ]

    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    menu.append([InlineKeyboardButton('К началу меню',
                                      callback_data=md.BACK_TO_MENU)])
    if ShoppingCart.objects.filter(user=user).exists():
        menu.append([InlineKeyboardButton('Оформить заказ',
                                          callback_data=f'{md.CHECKHOUT}')])
    return InlineKeyboardMarkup(menu)


def checkout_buttons(n_cols):
    buttons = [InlineKeyboardButton('К началу меню',
                                    callback_data=md.BACK_TO_MENU),
               InlineKeyboardButton('Оформить заказ',
                                    callback_data=md.WAIT)]
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return InlineKeyboardMarkup(menu)


def offer_ready(n_cols, user_id, code):
    buttons = [InlineKeyboardButton('Заказ готов',
                                    callback_data=f'{md.READY}#{user_id}#{code}'),
               InlineKeyboardButton('Отменить заказ',
                                    callback_data=f'{md.CANCEL}#{user_id}#{code}')]
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return InlineKeyboardMarkup(menu)


def thanks(n_cols):
    buttons = [InlineKeyboardButton('Заказать еще',
                                    callback_data=md.OFFER)]
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return InlineKeyboardMarkup(menu)
