# -*- coding: utf-8 -*-

import copy

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from typing import Iterable

from tgbot.handlers import manage_data as md
from tgbot.handlers import static_text as st
from tgbot.models import ShoppingCart


def make_btn_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                st.go_back, callback_data=f'{md.BUTTON_BACK_IN_PLACE}'),
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_start_command():
    buttons = ReplyKeyboardMarkup([
        [st.menu, st.offer],
        [st.afisha]
    ], resize_keyboard=True)

    return buttons


def keyboard_confirm_decline_broadcasting():
    buttons = [[
        InlineKeyboardButton(
            st.confirm_broadcast, callback_data=f'{md.CONFIRM_DECLINE_BROADCAST}{md.CONFIRM_BROADCAST}'),
        InlineKeyboardButton(
            st.decline_broadcast, callback_data=f'{md.CONFIRM_DECLINE_BROADCAST}{md.DECLINE_BROADCAST}')
    ]]

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
                     callback_data=f'{md.BACK_TO_MENU}#None')])
    if ShoppingCart.objects.filter(user=user).exists():
        menu.append([InlineKeyboardButton('ОФОРМИТЬ ЗАКАЗ',
                                          callback_data=f'{md.CHECKHOUT}')])
        menu.append([InlineKeyboardButton('УДАЛИТЬ ПРОДУКТЫ ИЗ КОРЗИНЫ',
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
    menu.append([InlineKeyboardButton('В НАЧАЛО МЕНЮ',
                                      callback_data=f'{md.BACK_TO_MENU}#None')])
    if ShoppingCart.objects.filter(user=user).exists():
        menu.append([InlineKeyboardButton('Оформить заказ',
                                          callback_data=f'{md.CHECKHOUT}')])
    return InlineKeyboardMarkup(menu)


def checkout_buttons(n_cols, cost):
    buttons = [InlineKeyboardButton(f'Заплатить {cost}р', pay=True),
               InlineKeyboardButton('В начало меню',
                                    callback_data=f'{md.BACK_TO_MENU}#delete')]
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
