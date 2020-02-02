# -*- coding: UTF-8 -*-
from flask import Blueprint
from flask_restplus import Api

from app.controller.controller_hr_bank_crawler import ns as controller_hr_bank_crawler_ns


bp = Blueprint('controller', __name__, url_prefix='/controller')


api = Api(bp, title='人力銀行爬蟲 控制器', version='1.0', description='', doc='/')


api.add_namespace(controller_hr_bank_crawler_ns)