def get_client_ip(request) -> str:
    """
    Получить IP адрес пользователя.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip  # noqa


def declenize(num: int, nouns: list) -> str:
    """
    Склонение слова, в зависимости от числа.
    """
    num = abs(num) % 100

    if num >= 5 and num <= 20:
        return nouns[2]

    num = num % 10

    if num == 1:
        return nouns[0]
    elif num >= 2 and num <= 4:
        return nouns[1]
    else:
        return nouns[2]
