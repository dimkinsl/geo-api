from flask import Blueprint, make_response, jsonify
from geo.get_distance import get_yandex_coordinates

geo = Blueprint('geo', __name__, template_folder='templates', static_folder='static')


@geo.route('/')
def index():
    return make_response(jsonify({'Content-Type': 'application/json;charset=utf-8',
                                  'Name': 'Bluprint geo-API',
                                  'Link': 'http://<you-domain:port>/geo/api/<address>'}))


@geo.route('/api/<string>', methods=['GET'])
def get_address(string):
    try:
        # Вынужденное применение из-за обработки запроса через cURL.
        string = string.encode('iso8859-1').decode('utf-8')
        print('string через httpie', string)
    except UnicodeEncodeError:
        # Плохая практика использования pass, но из-за cURL - никак.
        # Браузеры и httpie обрабатывают строку в нормальной кодировке.
        pass
    result = get_yandex_coordinates(string)
    return jsonify(result)





