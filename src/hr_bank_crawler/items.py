# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HrBankCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    schedule_filename = scrapy.Field()
    search_page = scrapy.Field()
    job_page = scrapy.Field()
    analysis_page = scrapy.Field()
    company_page = scrapy.Field()

    crawl_date = scrapy.Field()
    schedule_filename = scrapy.Field()

    job_ajax_link = scrapy.Field()
    analysis_ajax_link = scrapy.Field()
    company_ajax_link = scrapy.Field()
