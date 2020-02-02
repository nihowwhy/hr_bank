# -*- coding: UTF-8 -*-

import sys
sys.path.append('.')
sys.path.append('/ods/analysis/B0829/hr_bank/src/api/')
sys.path.append('/ods/analysis/B0829/hr_bank/src/api/app/controller/')
sys.path.append('../api/')
sys.path.append('../api/app/controller/')


from schedule import SCHEDULE
from controller_hr_bank_crawler import ControllerHrBankCrawler


print('>>> Batch Start')

for task in SCHEDULE:
    for prefix_filename, start_urls in task.items():
        ns_payload = {
            'prefix_filename': prefix_filename,
            'start_urls': start_urls,
        }
        try:
            controller = ControllerHrBankCrawler(ns_payload)
            controller.process()
        except:
            pass
            # todo
            # send email (open firewall)
        
print('>>> Batch End')

