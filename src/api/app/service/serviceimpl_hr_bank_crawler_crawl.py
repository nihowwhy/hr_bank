# -*- coding: UTF-8 -*-
import os
# from config import config


class ServiceImplHrBankCrawlerCrawl:
    

    @staticmethod
    def process(config, case, composition):
        print('>>> composition:::', composition)
        start_urls = case['start_urls']
        prefix_filename = case['prefix_filename']
        total_job_counts = composition['total_job_counts']
        
        start_urls_string = str(start_urls).replace(' ', '')
        
        project_dir = config['project_dir']
        scrapy_folder_dir = os.path.join(project_dir, 'src/api/app/hr_bank_crawler')
        
        cd_command = f'cd {scrapy_folder_dir}'
        scrapy_command = f'scrapy crawl hr_bank_104 -L WARNING -a start_urls_string={start_urls_string} -a prefix_filename={prefix_filename} -a total_job_counts={total_job_counts}'
        command = f'{cd_command} && {scrapy_command}'

        print(f'\n>>> start crawling task\n')
        os.system(command)
        print(f'\n>>> finish crawling task\n')
        

    