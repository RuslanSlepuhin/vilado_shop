
def text_from_error_response(response) -> str:
    error_text = "ОШИБКА\n"
    response = response.json()
    for i in range(len(response)):
        for key, value in response.items():
            error_text += f"{key}: {', '.join(value)}\n"
    return error_text

def text_from_dict(d:dict) -> str:
    text = ""
    for key, value in d.items():
        text += f"{key}: {value}\n"
    return text


