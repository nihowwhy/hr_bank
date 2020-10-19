# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HrBankJobItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    search_job_json = scrapy.Field()
    job_desc_json = scrapy.Field()
    job_analysis_json = scrapy.Field()
    comp_desc_json = scrapy.Field()
    
    job_no = scrapy.Field()
    job_id = scrapy.Field()
    job_name = scrapy.Field()
    comp_no = scrapy.Field()
    comp_id = scrapy.Field()
    comp_name = scrapy.Field()
    indust_no = scrapy.Field()
    indust_desc = scrapy.Field()
    appear_date = scrapy.Field()
    crawl_date = scrapy.Field()
    
    meta = scrapy.Field()

    
#     #
#     job_link = scrapy.Field()
#     job_analysis_link = scrapy.Field()
#     #
    
#     job_type = scrapy.Field()
#     job_no = scrapy.Field()
#     job_name = scrapy.Field()
#     job_role = scrapy.Field() # 正職？
#     job_addr_dist = scrapy.Field()
#     job_addr = scrapy.Field()
#     job_desc = scrapy.Field()
#     education = scrapy.Field()
#     experience = scrapy.Field()
#     apply_count = scrapy.Field()
#     company_no = scrapy.Field()
#     company_name = scrapy.Field()
#     indust_no = scrapy.Field()
#     industry_name = scrapy.Field()
#     salary_low = scrapy.Field()
#     salary_high = scrapy.Field()
#     s10 = scrapy.Field() #?
#     update_date = scrapy.Field()
#     optionZone = scrapy.Field() #?
#     job_tag = scrapy.Field()

