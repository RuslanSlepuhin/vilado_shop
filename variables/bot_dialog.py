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

# Database
empty_base = "Ничего не нашлось по вашему запросу"
category_choose = "Выберите категорию:"

# CARDS
button_left = {'text': "<<", 'callback': 'left'}
button_number_empty = {'text': "Number*", 'callback': '*'}
button_right = {'text': ">>", 'callback': 'right'}
button_less = {'text': "-", 'callback': 'less'}
button_amount_empty = {'text': "Amount*", 'callback': '*'}
button_more = {'text': "+", 'callback': 'more'}
button_to_cart = {'text': "Добавить в корзину", 'callback': 'to cart'}
button_catalog = {'text': "Каталог", 'callback': 'main menu'}

text_empty_to_change_values, callback_empty_to_change_values = [button_number_empty['text'], button_amount_empty['text']], [button_number_empty['callback'], button_amount_empty['callback']]

card_buttons = {
    "1": {
        button_left['text']: button_left['callback'],
        button_number_empty['text']: button_number_empty['callback'],
        button_right['text']: button_right['callback'],
    },
    "2": {
        button_less['text']: button_less['callback'],
        button_amount_empty['text']: button_amount_empty['callback'],
        button_more['text']: button_more['callback'],
    },
    "3": {
        button_to_cart['text']: button_to_cart['callback'],
    },
    "4": {
        button_catalog['text']: button_catalog['callback'],
    }
}
