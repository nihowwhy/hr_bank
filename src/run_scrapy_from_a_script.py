import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from hr_bank_crawler.spiders.hr_bank_spider import HrBankSpider
from data_process.crawl_data_preprocess import CrawlDataProcessor
from config.config import LOG_FOLDER, DB_FOLDER


def init_check():
    # directory init
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)


def crawl_hr_bank_website():
    process = CrawlerProcess(get_project_settings())
    process.crawl('104') # "104" is the spider name
    process.start()      # the script will block here until the crawling is finished


def run():
    # initial check
    print(f'>>> Initial Check...')
    init_check()
    
    # crawl data
    print(f'>>> Start Crawling...')
    crawl_hr_bank_website()
    print('>>> Crawling Job Done!')
    
    # process crawl data
    print(f'>>> Start Process Data...')
    crawl_data_processor = CrawlDataProcessor()
    crawl_data_processor.process() # "process_date"(int)-> default: Today Date, 0 means process all data, or YYYYMMDD
    
    
if __name__ == '__main__':
    run()
    


