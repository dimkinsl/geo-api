from flask import Flask, abort, flash, jsonify, make_response
from geo.geo import geo

app = Flask(__name__)
app.config.from_object(__name__)

# Подключение файла настроек с API_KEY
app.config.from_pyfile('settings.py')

# Регистрация Bluprint 'geo'
app.register_blueprint(geo, url_prefix='/geo')

# app.secret_key = 'fdgfh78@#5?>gfhf89dx,v06k'


@app.route('/')
def index():
    return make_response(jsonify({'Content-Type': 'application/json;charset=utf-8',
                                  'Name': 'Bluprint geo-API',
                                  'Link': 'http://<you-domain:port>/geo/api/<address>'}))


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify({'error': 'Internal server error'}), 500)

if __name__ == '__main__':
    app.run(debug=True)
