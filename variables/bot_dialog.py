start_answer = "Этот бот поможет вам сделать заказ по каталогу товара. Нажмите кнопку 'далее', чтобы начать \n\n[ЗДЕСЬ МОЖЕТ БЫТЬ ЛЮБОЙ ТЕКСТ ЗАКАЗЧИКА]"
start_answer_buttons = {
    "В КАТАЛОГ": "main menu"
}
user_doesnt_have_registration = "Вы не зарегистрированы, пройдите регистрацию, чтобы продолжить"
server_is_not_response = "Сервер не отвечает"
registration_is_successful = "Вы успешно зарегистрированы"
registration_answer_button = {
    "РЕГИСТРАЦИЯ": "registration"
}

FSM_form_ask_email = "Введите ваш email:"
FSM_form_ask_name = "Введите ваше имя:"
FSM_form_ask_phone_number = "Введите ваш номер телефона:"

# API URLS
domain = "http://127.0.0.1:8000/"
app_ver = "api/v1/"
user_url = domain + app_ver + "user/"
categories_url = domain + app_ver + "categories/"
items_url = domain + app_ver + "items/"
shopping_cart_url = domain + app_ver + "shopping-cart/"

# Database
empty_base = "Ничего не нашлось по вашему запросу"
category_choose = "Выберите категорию:"
empty_shopping_cart = "У Вас не выбрано ни одного товара"

# CARDS
skip_callback = "1"
number_row = "1"
amount_row = "2"

button_left = {'text': "<<", 'callback': 'left'}
button_number_empty = {'text': "Number", 'callback': skip_callback}
button_right = {'text': ">>", 'callback': 'right'}
button_less_10 = {'text': "-10", 'callback': 'less10'}
button_less = {'text': "-", 'callback': 'less'}
button_amount_empty = {'text': "Amount", 'callback': skip_callback}
button_more = {'text': "+", 'callback': 'more'}
button_more_10 = {'text': "+10", 'callback': 'more10'}
button_to_cart = {'text': "🛒 Добавить в корзину", 'callback': 'add to cart'}
button_catalog = {'text': "📕 Каталог", 'callback': 'main menu'}
button_show_shopping_cart = {'text': "Перейти в корзину", 'callback': 'show shopping cart'}


text_empty_to_change_values, callback_empty_to_change_values = [button_number_empty['text'], button_amount_empty['text']], [button_number_empty['callback'], button_amount_empty['callback']]

card_buttons_raw = {
    number_row: {
        button_left['text']: button_left['callback'],
        button_number_empty['text']: button_number_empty['callback'],
        button_right['text']: button_right['callback'],
    },
    amount_row: {
        button_less_10['text']: button_less_10['callback'],
        button_less['text']: button_less['callback'],
        button_amount_empty['text']: button_amount_empty['callback'],
        button_more['text']: button_more['callback'],
        button_more_10['text']: button_more_10['callback'],
    },
    "3": {
        button_to_cart['text']: button_to_cart['callback'],
    },
    "4": {
        button_catalog['text']: button_catalog['callback'],
    },
    "5": {
        button_show_shopping_cart['text']: button_show_shopping_cart['callback'],
    }
}
card_buttons = card_buttons_raw.copy()

menu_callbacks = []
for key in card_buttons:
    for next_key, value in card_buttons[key].items():
        menu_callbacks.append(value)

menu_callbacks.pop(menu_callbacks.index(button_catalog['callback']))
amount_cannot_be_empty = "Количество не может быть равным нулю"
items_on_the_cart = "Товар добавлен в корзину"
item_was_delete_from_shopping_cart = "Товар удален из корзины"
amount_has_been_updated = "Количество обновлено"
have_nothing = "Ничего не нашлось"

# SHOPPING CART
empty_shopping_cart_buttons = {
    button_catalog['text']: button_catalog['callback']
}

confirm_callback = 'confirm'
confirm_shopping_cart_buttons = {
    "Отправить заявку": confirm_callback,
    button_catalog['text']: button_catalog['callback'],

}
shopping_cart_view = "КОРЗИНА\n\n"
