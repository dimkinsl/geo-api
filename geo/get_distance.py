import requests
import os
import logging
from typing import Any
from bs4 import BeautifulSoup
from math import radians, cos, sin, sqrt, atan2
from geo.base_coordinates import MKAD

# В переменной data_polygon храним координаты полигона МКАД
data_polygon: list = MKAD

# Создаем обработчик событий для ошибок уровня WARNING
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
file_handler_error = logging.FileHandler('error.log')
file_format_error = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
file_handler_error.setFormatter(file_format_error)
logger.addHandler(file_handler_error)

# Создаем обработчик для логирования результатов расчитывания расстояния от точки до МКАД
logger_data = logging.getLogger('data')
logger_data.setLevel(logging.INFO)
file_handler_info = logging.FileHandler('distance.log')
file_format_info = logging.Formatter('%(asctime)s - %(message)s')
file_handler_info.setFormatter(file_format_info)
logger_data.addHandler(file_handler_info)


def get_yandex_coordinates(address: str) -> Any:
    """
    Главная функция принимает строку "address".
    Фунция принимает данные по HTTP и отправляет запрос
    к API-Геокоера Яндекс. Если ответ положительный ("200"),
    запрос обрабатывается вызовом ряда функций...
    Вызов функции "in_polygon_coordinates" проверяет,
    если координаты точки внутри МКАДа, то возвращает None.
    Если за МКАД, то подключаются на обработку данных
    функция "haversine" - вычисление расстояния от точки, до ближайшей точки МКАД.
    address - строка адреса для вычисления координат.
    API_KEY - "ключ разработчика", берется из переменной окружения.
    return - результат вычисления, None если в пределах МКАД,
    либо значение float (расстояние в км.)
    """
    API_KEY: str = os.environ.get('API_KEY')
    data: dict = {'apikey': API_KEY, 'geocode': address}

    # Проверка запроса, если удачно - обрабатываем результат запроса
    try:
        result = requests.get('https://geocode-maps.yandex.ru/1.x/', params=data)

    # Если нет, вызываем исключение
    except requests.exceptions.RequestException:
        logger.error('Bad request')
        return 'General error!'

    if result.status_code == 200:
        soup = BeautifulSoup(result.text, 'xml')

        # Проверка на наличие координат, 'found' == 0 означает ввод некорректных данных
        if int(soup.find('found').string):

            # x и y присваиваем значение координат первой из найденных точек
            y, x = soup.find('pos').string.split(' ')
            in_polygon: bool = in_polygon_coordinates(float(x), float(y), data_polygon)

            # Если точка внутри полигона, возвращаем None
            if in_polygon:
                return
            else:

                # Если снаружи, расчитываем и возвращаем расстояние до МКАД.
                # Результат записывается в файл distance.log
                distance: float = haversine(float(x), float(y), MKAD)
                logger_data.info(f'Расстояние от "{address}" до МКАД = {distance}')
                return distance
        else:

            # При некорректном адресе - возврат ответа и запись в лог.
            logger.error(f'Некорректный адрес запроса: {address}')
            return 'invalid address'
    else:

        # Если ответ сервера не равен '200'
        logger.error(f'Ошибка {result.status_code}')
        return 'Bad request'


def in_polygon_coordinates(x: float, y: float, data: list) -> bool:
    """
    Функция использует алгоритм трассировки лучей.
    Лучи попеременно проходят в цикле отрезки, проверяя пересечение.
    Результат выполнения функции: если 1, то точка внутри полигона,
    если 0, то снаружи полигона.
    x, y = долгота и широта искомой точки.
    data - зона поиска точки внутри полигона.
    return - bool (1, 0)
    """
    in_out_polygon: int = 0
    for i in range(len(data)):
        xp: float = data[i][0]
        yp: float = data[i][1]
        xp_prev: float = data[i - 1][0]
        yp_prev: float = data[i - 1][1]
        if (((yp <= y and y < yp_prev) or (yp_prev <= y and y < yp))
                and (x > (xp_prev - xp) * (y - yp) / (yp_prev - yp) + xp)):
            in_out_polygon = 1 - in_out_polygon
    return in_out_polygon


def haversine(lat1: float, lon1: float, data: list) -> float:
    """
    Функция haversine расчитывает расстояние от координат lat1 и lon1
    до всех координат списка data.
    Этот алгоритм вычисляет расстояние по прямой линии на поверхности земли.
    Все полученные значения расстояний заносятся в список. После прохождения
    цикла, список сортируется и возвращается первое, наименьшее значение.
    return - значение float.
    """

    # Приблизительный радиус земли в км
    R: float = 6373.0
    distance: list = []
    lat1: float = radians(lat1)
    lon1: float = radians(lon1)

    for i in range(len(data)):
        lat2: float = radians(data[i][0])
        lon2: float = radians(data[i][1])

        dlon: float = lon2 - lon1
        dlat: float = lat2 - lat1

        a: float = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c: float = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance.append(R * c)
        distance.sort()
    return round(distance[0], 2)
