import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from datetime import datetime

from hr_bank_crawler.spiders.hr_bank_spider import HrBankSpider
from data_process.crawl_data_preprocess import CrawlDataJsonProcessor
from config.config import LOG_FOLDER, DB_FOLDER
from schedule import schedules

TODAY_DATE = int(datetime.now().strftime('%Y%m%d'))

def init_check():
    # directory init
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)


def crawl_hr_bank_website(start_urls):
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl('104', start_urls=start_urls) # "104" is the spider name
    process.start()      # the script will block here until the crawling is finished


def run(**kwargs):
    # get parameters
    filename = kwargs['filename']
    start_urls = kwargs['start_urls']
    process_date = kwargs['process_date']
    print(f'>>> Schedule: {filename}')

    # initial check
    print(f'>>> Initial Check...')
    init_check()

    # crawl data
    print(f'>>> Start Crawling...')
    crawl_hr_bank_website(start_urls)
    print('>>> Crawling Job Done!')

    # process crawl data
    print(f'>>> Start Process Data...')
    crawl_data_processor = CrawlDataJsonProcessor(process_date=process_date, filename=filename)  # "process_date"(int)-> default: Today Date, 0 means process all data, or YYYYMMDD
    crawl_data_processor.process()


if __name__ == '__main__':
    # iterate schedule
    for s in schedules:
        [[filename, start_urls]] = s.items()
        run_settings = {
            'filename': filename,
            'start_urls': start_urls,
            'process_date': TODAY_DATE,
        }
        run(**run_settings)



