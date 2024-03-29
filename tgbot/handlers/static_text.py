import os

welcome = "Привет!\n" \
          "Чего пожелаете?"
menu = "Посмотреть меню"
error = "Извините, что-то пошло не так. Попробуйте еще раз."
offer = "Сделать заказ"
add_to_fav_success = "Стих был успешно добавлен в избранное."
view_fav = "Просмотреть избранное"
choose_author = "Выберите первую букву фамилии автора из вашего избранного списка."
choose_author_full = "Выберите автора"
choose_poem = "Выберите стих"
todays_offer = 'Что бы вы хотели сегодня заказать?'
afisha = 'Афиша'
offer_help = ('Для того, чтобы заказать: выберете категорию,'
              + 'а затем нажмите на продукт, который хотите добавить к корзину')
is_wait = 'Вы не можете оформить заказ, так как ваш прошлый заказ {0} еще не готов'
new_offer = ('Номер заказа: {0}' + os.linesep
             + 'Посетитель: {1}' + os.linesep
             + 'Заказ: {2}' + os.linesep)
offer_ready = ('Заказ: {0} готов!' + os.linesep
               + 'Посетитель: {1}' + os.linesep
               + 'Заказ: {2}' + os.linesep)

go_back = "Вернуться"
confirm_broadcast = "Подтвердить"
decline_broadcast = "Отклонить"
secret_level = "Секретный уровень"
msg_sent = "Сообщение отослано"
share_location = "Позвольте мне узнать, откуда вы?"
thanks_for_location = "Спасибо за ваше местоположение!"
broadcast_command = '/broadcast'
broadcast_no_access = "Sorry, you don't have access to this function."
broadcast_header = "This message will be sent to all users.\n\n"
declined_message_broadcasting = "Рассылка сообщений отклонена❌\n\n"
error_with_markdown = "Невозможно обработать ваш текст в формате Markdown."
specify_word_with_error = " У вас ошибка в слове "
secret_admin_commands = "⚠️ Секретные команды администратора\n" \
                        "/stats - bot stats"
