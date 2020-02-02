# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

import re
import ast
import time
import scrapy
import requests
from bs4 import BeautifulSoup
from scrapy.utils.project import get_project_settings

from conf.conversion_table import AREA_DICT, INDUSTRY_DICT, JOBCAT_DICT
from utils.logger import get_logger 
from hr_bank_crawler.items import HrBankCrawlerItem


INDUSTRY_ID_DICT = {value: key for key, value in INDUSTRY_DICT.items()}
DENIED_URLS = ['https://www.104.com.tw/jobs/main/','https://www.104.com.tw/robots.txt',]

logger = get_logger()


class HrBank104Spider(scrapy.Spider):
    name = 'hr_bank_104'
    allowed_domains = ['104.com.tw']
    denied_urls = ['https://www.104.com.tw/jobs/main/','https://www.104.com.tw/robots.txt',]
    
    crawl_count = 0
    seen_job_id_list = []
    
    def __init__(self, **kwargs): 
        super(HrBank104Spider, self).__init__(**kwargs)
        self.settings = get_project_settings()
        self.config = self.settings.get('PROJECT_CONFIG')
        self.headers = self.config['headers']
        self.proxies = self.config['proxies']
        self.prefix_filename = kwargs.get('prefix_filename', 'DEFAULT')
        self.start_urls = kwargs.get('start_urls_string', '[]')[1:-1].split(',')
        self.accumulated_job_num = int(kwargs.get('total_job_counts', 0))
        print('=' * 30)
        print(f'>>> Start Urls:\n{self.start_urls}')
        print('=' * 30)

        
    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield Request(url, dont_filter=False)   

    
    def parse(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        total_job_num, total_page_num = self._get_total_job_and_page_num(soup)
        
        
        # Retry to send request
        retry_time = 0
        while total_job_num is None and total_page_num is None and retry_time < self.settings.get('RETRY_TIMES'):
            print(f'>>> Retry Main Page: {response.request.url}')
            time.sleep(2)
            response = requests.get(response.request.url,
                                    proxies=self.proxies,
                                    headers=self.headers,
                                    allow_redirects=False,
                                    verify=False,)
            soup = BeautifulSoup(response.text, 'lxml')
            total_job_num, total_page_num = self._get_total_job_and_page_num(soup)
            retry_time += 1
            # ===================================================
            # LOGGING retry
            logger.warning(f'[Retry] retry_times:{retry_time}, {response.request.url}')
            # ===================================================
        
        current_page_num = re.findall("&page=(\d+)", response.request.url)
        current_page_num = int(current_page_num[0])

        # accumulate total job number
        if current_page_num == 1:
            if total_job_num is not None and total_page_num is not None:
#                 self.accumulated_job_num += total_job_num
                print(f'>>> Accumulated Job Number: {self.accumulated_job_num}')
            else:
                print(f'>>> There is no total job num: {response.request.url}')
                raise ConnectionError(f'url: {response.request.url}')
        
        
            # yield different page urls
            if '&page=' in response.request.url:
                current_page_num = re.findall("&page=(\d+)", response.request.url)
                if current_page_num:
                    current_page_num = int(current_page_num[0])

                if current_page_num == 1:
                    print(f'>>> Yield Pages Urls: {response.request.url}')
                    while current_page_num < total_page_num:
                        current_page_num += 1
                        next_page_url = re.sub("(&page=)\d+", r"\g<1>{}".format(current_page_num), response.request.url)
                        yield scrapy.Request(next_page_url, self.parse)

            elif '&page=' not in response.request.url:
                if response.request.url not in DENIED_URLS:
                    url = response.request.url + '&page={}'.format(1)
                    yield scrapy.Request(url, self.parse)
                else:
                    print('>>> Deny URL + 1')
                    print(f'>>> Deny URL: {response.request.url}')
                    soup = None
        
        # If there is something wrong or being redirected to home page, it won't parse main page.
        if soup is not None:
            yield from self._parse_main_page(response, soup)

    
    def _parse_main_page(self, response, soup):
        
        # Get each job-urls, and parse main page to get some information
        if not soup.select('article div.b-block__left'):
            raise ValueError('could not find job blocks in main-page html.')
        
        
        for job_div in soup.select('article div.b-block__left'):
            job_link = job_div.select('a.js-job-link')
            if job_link:
                job_detail_url = 'https:' + job_link[0]["href"] # link for each detailed job page

                if not job_detail_url:
                    # ===================================================
                    # LOGGING when get blank url
                    logger.warning(f'[NoJobLink] {response.request.url}')
                    # ===================================================
                    continue

                # skip hunter 104 pages
                if 'hunter' in job_detail_url:
                    # ===================================================
                    # LOGGING skip hunter 104 pages
                    logger.info(f'[HunterUrl] {response.request.url}')
                    # ===================================================
                    print('>>> remove hunter 104...')
                    continue


                job_id = self._get_job_id(job_detail_url)
                if not job_id:
                    continue

                job_name = re.sub(' +', ' ', job_link[0].text).strip()
                

                # Get company url
                company_url = self._get_company_url(job_div)

                tag_default = job_div.select('span.b-tag--default')
                listed_company = ''
                foreign_company = ''
                staff_num = ''
                for tag in tag_default:
                    pattern = '.*?(上市|上櫃).*?'
                    result = re.search(pattern, tag.text)
                    if result:
                        listed_company = self._get_only_text(tag.text)

                    pattern = '.*?(外商).*?'
                    result = re.search(pattern, tag.text)
                    if result:
                        foreign_company = self._get_only_text(tag.text)

                    pattern = '員工(.*?)人'
                    result = re.search(pattern, tag.text)
                    if result:
                        staff_num = self._get_only_text(str(result.group(1)))


                item = HrBankCrawlerItem()
                item["msg"] = {}

                item["job_detail_url"] = job_detail_url
                item['company_url'] = company_url
                item["job_id"] = job_id
                item["job_name"] = job_name
                item["listed_company"] = listed_company
                item["foreign_company"] = foreign_company
                item["staff_num"] = staff_num
                item["company_industry"] = self._get_company_industry(response.request.url)


                if job_id in self.seen_job_id_list:
                    # ===================================================
                    # LOGGING duplicated job ID
                    logger.info(f'[Duplicated] JobId:{job_id}, {response.request.url}')
                    # ===================================================
                    continue
                else:
                    self.seen_job_id_list.append(job_id)
                    yield scrapy.Request(job_detail_url, self._parse_job_detail, meta={"item": item})
    
    
    def _parse_job_detail(self, response):
        self.crawl_count += 1
        item = response.meta['item']
        soup = BeautifulSoup(response.body, 'lxml')
        
        
        # parse from JSON-LD
        try:
            script = soup.find('script', type='application/ld+json').text.replace('\n','     ').replace('\/', '/').replace('\r','')
            detail = ast.literal_eval(script)[0]
            item = self._parse_jsonld(detail, item)

        except:
            # ===================================================
            # LOGGING when there is no "application/ld+json" in html, send request again.
            yield scrapy.Request(item["job_detail_url"], self._parse_job_detail, meta={"item": item}, dont_filter=True)
            logger.error(f'[NoJsonLd] {response.request.url}')
            return
            # ===================================================
        
        
        # parse from html
        try:
            if soup.select_one('.sub a'):
                item["applied_num"] = self._get_only_text(soup.select_one('.sub a').text)
        except Exception as e:
            # ===================================================
            # LOGGING if there is no applied counts
            logger.error(f'[ElementNotFound] {e}, No Applied Number Error, {response.request.url}')
            return
            # ===================================================
    
    
        detail_dict = {
            "職務類別": "",
            "工作待遇": "",
            "工作性質": "",
            "上班地點": "",
            "管理責任": "",
            "出差外派": "",
            "上班時段": "",
            "休假制度": "",
            "可上班日": "",
            "需求人數": "",
            "接受身份": "",
            "工作經歷": "",
            "學歷要求": "",
            "科系要求": "",
            "語文條件": "",
            "擅長工具": "",
            "工作技能": "",
            "具備證照": "",
            "其他條件": "",
            "雇用類型": "",
            "代徵企業": "",
        }

        content_keys = soup.select(".content dt")
        content_vals = soup.select('.content dd')
        index = -1
        for key in content_keys:
            index += 1
            title = self._clean_title(key.text)
            if title in detail_dict.keys():
                detail_dict[title] = self._get_only_text(content_vals[index].text).replace(
                    " 認識「」職務 詳細職類分析(工作內容、薪資分布..) 更多相關工作","").replace(
                    "地圖找工作","")#[:255]

        item["job_category"] = detail_dict["職務類別"]
        item["salary"] = detail_dict["工作待遇"]
        item["job_type"] = detail_dict["工作性質"]
        item["location"] = detail_dict["上班地點"]
        item["management"] = detail_dict["管理責任"]
        item["dispatch"] = detail_dict["出差外派"]
        item["working_hours"] = detail_dict["上班時段"]
        item["vacation"] = detail_dict["休假制度"]
        item["avalibale_work_date"] = detail_dict["可上班日"]
        item["required_num"] = detail_dict["需求人數"]
        item["identity"] = detail_dict["接受身份"]
        item["experience"] = detail_dict["工作經歷"]
        item["education"] = detail_dict["學歷要求"]
        item["department"] = detail_dict["科系要求"]
        item["language"] = detail_dict["語文條件"]
        item["tool"] = detail_dict["擅長工具"]
        item["skill"] = detail_dict["工作技能"]
        item["certification"] = detail_dict["具備證照"]
        item["other_requirement"] = detail_dict["其他條件"]
        item["employment_type"] = detail_dict["雇用類型"]
        item["agent_company"] = detail_dict["代徵企業"]

        if self.crawl_count % 100 == 0:
            print(f'[{self.crawl_count}] {item["company_industry"]} {item["job_id"]} {item["job_name"]} {item["job_detail_url"]}')
        yield item
    
    



    def _get_total_job_and_page_num(self, soup):
        total_job_num = re.findall('\"totalCount\":(\d+)', soup.text)
        total_page_num = re.findall('\"totalPage\":(\d+)', soup.text)
        if total_job_num and total_page_num:
            total_job_num = int(total_job_num[0])
            total_page_num = int(total_page_num[0])
            return total_job_num, total_page_num
        else:
            return None, None
        
        
    def _get_job_id(self, url):
        pattern = '\/job\/([0-9a-zA-Z]+)'
        result = re.search(pattern, url)
        if result:
            job_id = result.group(1)
            return job_id
        
    
    def _get_company_url(self, div):
        try:
            url = div.find('a', title=re.compile('^公司名.+'))['href']
            company_url = 'https:' + url
            return company_url
        except:
            return ''


    def _parse_jsonld(self, jsonld, item):
        item["company_name"] = self._get_only_text(jsonld["hiringOrganization"]["name"])
        item["update_date"] = jsonld["datePosted"]
        item["industry"] = jsonld["industry"]
        item["district"] = jsonld["jobLocation"]["address"]["addressLocality"]
        item["job_description"] = self._get_job_description(jsonld["description"])
        item["welfare"] = self._get_welfare_description(jsonld["description"])
        if item["company_industry"] is None:
            company_industry_id = INDUSTRY_DICT.get(item["industry"], None)
            company_industry_id = company_industry_id[:4] + '000000'
            if company_industry_id in INDUSTRY_ID_DICT.keys():
                item["company_industry"] = INDUSTRY_ID_DICT.get(company_industry_id, '其他')
        return item        

    
    def _get_only_text(self, text):
        # remove \n, \t, \r, \u3000 from text
        text = text.replace('\n',' ').replace('\t',' ').replace('\r',' ').replace('\u3000', ' ')
        text = re.sub(' +', ' ', text).strip()
        return text


    def _clean_title(self, text):
        text = text.replace('\n','').replace('\t','').replace('\r','').replace(' ','').replace('：','')
        return text
    
    
    def _get_job_description(self, text):
        text = text.replace('\n',' ').replace('\t','').replace('\r','')
        text = re.sub(' +', ' ', text)
        try:
            pattern = '【工作內容】(.*?)- 職務類別'
            if re.search(pattern, text):
                description = re.search(pattern, text).group(1).strip()
            else:
                pattern = '【工作內容】(.*?)【'
                description = re.search(pattern, text).group(1).strip()
            return description#[:255]
        except:
            return ''


    def _get_welfare_description(self, text):
        text = self._get_only_text(text)
        pattern = '【公司福利】(.*?)更多工作資訊請參考：'
        try:
            description = re.search(pattern, text).group(1).strip()
            return description
        except:
            return ''
    
    
    def _get_company_industry(self, url):
        pattern = '&indcat=(\d+)'
        result = re.findall(pattern, url)
        if result:
            industry_id = result[0]
            industry_id = industry_id[:4] + '000000'
            for indcat_name, indcat_id in INDUSTRY_DICT.items():
                if indcat_id == industry_id:
                    industry_category = indcat_name
                    return industry_category
        else:
            return None