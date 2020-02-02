# -*- coding: UTF-8 -*-
import logging
from flask import Flask

from app.controller import bp as controller_bp


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
logging.basicConfig(level=logging.INFO)


app.register_blueprint(controller_bp)


if __name__ == '__main__':
    print('>>> API Start Serving...')
    app.run(host='10.240.64.45', port=10400, debug=True)