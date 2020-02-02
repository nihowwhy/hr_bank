# -*- coding: UTF-8 -*-
import json
from flask import abort
from flask_restplus import Namespace, Resource, fields

from config import config
from app.utils.logger import get_logger
from app.service.service_hr_bank_crawler_split_url import ServiceHrBankCrawlerSplitUrl
from app.service.service_hr_bank_crawler_crawl import ServiceHrBankCrawlerCrawl


# logging
logger = get_logger()


ns = Namespace('hr_bank_crawler', description='Controller of Human Resource Bank Crawler.')


model = {
    'prefix_filename': fields.String(description='save file name'),
    'start_urls': fields.List(fields.Url(description='start urls')),
}
payload = ns.model('hr_bank_crawler_payload', model)


class ControllerHrBankCrawler:
    
    def __init__(self, ns_payload):
        self._config = config
        self._case = ns_payload
        self._composition = {}
        self._policies = [
            ServiceHrBankCrawlerSplitUrl(),
            ServiceHrBankCrawlerCrawl(),
        ]
    
    
    def process(self):
        for _policy in self._policies:
            _policy.process(self._config, self._case, self._composition)
            
            
    def __str__(self):
        string = ('CONFIG =================================================\n'
                  f'{self._config}\n\n'
                  'CASE ===================================================\n'
                  f'{self._case}\n\n'
                  'COMPOSITION ============================================\n'
                  f'{self._composition}')
        return string
    
    
    def todo(self):
        pass
        # split urls
        # call spider and crawl and save


@ns.route('/')
class HrBankCrawler(Resource):
    
    def get(self):
        return '======= HR Bank Crawler API ======='
    
    @ns.expect(fields=payload, validate=True)
    def post(self):
        print(f'>>> payload: {ns.payload}')
        logger.info(f'[POST] payload={ns.payload}')
        controller = ControllerHrBankCrawler(ns.payload)
        controller.process()
        return controller.__str__()
        