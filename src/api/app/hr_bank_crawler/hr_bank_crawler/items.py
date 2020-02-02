# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HrBankCrawlerItem(scrapy.Item):
    msg = scrapy.Field() # pass message to pipline.py
    
    job_detail_url = scrapy.Field() #網址連結
    job_id = scrapy.Field() #工作編號
    job_name = scrapy.Field() #工作名稱
    listed_company = scrapy.Field() #上市上櫃
    foreign_company = scrapy.Field() #外商公司
    staff_num = scrapy.Field() #員工人數
    company_industry = scrapy.Field() #公司產業
    company_name = scrapy.Field() #公司名稱
    company_url = scrapy.Field() #公司網址
    update_date = scrapy.Field() #更新日期
    industry = scrapy.Field() #產業別
    district = scrapy.Field() #工作行政區
    job_description = scrapy.Field() #工作內容
    welfare = scrapy.Field() #公司福利
    applied_num = scrapy.Field() #應徵人數
    job_category = scrapy.Field() #職務類別
    salary = scrapy.Field() #工作待遇
    job_type = scrapy.Field() #工作性質
    location = scrapy.Field() #上班地點
    management = scrapy.Field() #管理責任
    dispatch = scrapy.Field() #出差外派
    working_hours = scrapy.Field() #上班時段
    vacation = scrapy.Field() #休假制度
    avalibale_work_date = scrapy.Field() #可上班日
    required_num = scrapy.Field() #需求人數
    identity = scrapy.Field() #接受身份
    experience = scrapy.Field() #工作經歷
    education = scrapy.Field() #學歷要求
    department = scrapy.Field() #科系要求
    language = scrapy.Field() #語文條件
    tool = scrapy.Field() #擅長工具
    skill = scrapy.Field() #工作技能
    certification = scrapy.Field() #具備證照
    other_requirement = scrapy.Field() #其他條件
    employment_type = scrapy.Field() #雇用類型
    agent_company = scrapy.Field() #代徵企業
    area = scrapy.Field() #工作區域
