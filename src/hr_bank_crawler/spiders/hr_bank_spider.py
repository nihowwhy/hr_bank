import scrapy
import json
import re
import requests
import unicodedata
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from scrapy.http.request import Request
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from hr_bank_crawler.items import HrBankCrawlerItem

MAX_TOTAL_PAGE = 150
DEFAULT_QUERY_PARAM = {
    # not recommended to change
    'page': 1,     # 頁數
    'mode': 's',   # s: 摘要顯示
    'order': 11,   # 11: 日期排序
    'ro': 0,       # 0: 全部職缺, 1: 全職職缺
    'asc': 0,      # 0: 降冪排序, 1: 升冪排序
}

with open('reference/area_breakdown_json.txt', 'r') as f:
    AREA_BREAKDOWN_DICT = json.loads(f.read())

with open('reference/jobcat_breakdown_json.txt', 'r') as f:
    JOBCAT_BREAKDOWN_DICT = json.loads(f.read())

with open('reference/indust_breakdown_json.txt', 'r') as f:
    INDUST_BREAKDOWN_DICT = json.loads(f.read())

crawled_count = 0
crawled_company_urls = []

class HrBankSpider(scrapy.Spider):
    name = "104"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def start_requests(self):
        # urls = [
        #     'https://www.104.com.tw/jobs/search/?ro=0&keyword=python&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&area=6001004000&order=15&asc=0&page=1&mode=s'
        # ]
        urls = self.start_urls

        for url in urls:
            # format and subdivide url
            url_processor = StartUrlProcessor()
            all_search_page_urls = url_processor.process(url)
            print('==================')
            print(all_search_page_urls)
            print('==================')

            # send request to search page ajax link
            for search_page_url in all_search_page_urls:
                yield scrapy.Request(url=search_page_url, callback=self.parse_search_page_response)


    def parse(self, response):
        pass


    def parse_search_page_response(self, response):
        # print('>>> Parse search page')
        if response.status != 200:
            return None

        # get job list from search page
        search_page_json = json.loads(clean_text(response.text))
        job_list = search_page_json['data']['list']

        for job in job_list:
            # init item
            item = HrBankCrawlerItem() # scrapy item

            # set search page (one job) to item
            item['search_page'] = job

            # get job page ajax link
            job_id = self.get_job_id_from_link(job['link']['job'])
            job_ajax_link = self.get_job_ajax_link(job['link']['job'], job_id)

            # get analysis page ajax link
            job_no = job['jobNo']
            analysis_ajax_link = self.get_analysis_ajax_link(job['link']['applyAnalyze'], job_no)

            # get company page ajax link
            company_id = self.get_company_id_from_link(job['link']['cust'])
            company_ajax_link = self.get_company_ajax_link(job['link']['cust'], company_id)

            # set job, analysis, company links
            link = {}
            link['job_ajax_link'] = job_ajax_link
            link['analysis_ajax_link'] = analysis_ajax_link
            link['company_ajax_link'] = company_ajax_link

            # print crawled count and job name
            global crawled_count
            crawled_count = crawled_count + 1
            if crawled_count % 100 == 0:
                print(f'>>> Crawled Count: {crawled_count}')
                print(f">>> Job Name: {item['search_page']['jobName']}")

            # send request to job page ajax link
            yield Request(url=link['job_ajax_link'],
                            callback=self.parse_job_ajax_response,
                            meta={'item': item, 'link': link})


    def parse_job_ajax_response(self, response):
        # print('>>> Parse job page')
        if response.status != 200:
            return None

        try:
            # set job page to item
            job_page_json = json.loads(clean_text(response.text))
            item = response.meta['item']
            item['job_page'] = job_page_json
        except:
            print('>>> Failed to get Job Page Response.')
        finally:
            # send request to analysis page ajax link
            link = response.meta['link']
            yield Request(url=link['analysis_ajax_link'],
                            callback=self.parse_analysis_ajax_response,
                            meta={'item': item, 'link': link})


    def parse_analysis_ajax_response(self, response):
        # print('>>> Parse analysis page')
        if response.status != 200:
            return None

        try:
            # set analysis page to item
            analysis_page_json = json.loads(clean_text(response.text))
            item = response.meta['item']
            item['analysis_page'] = analysis_page_json
        except:
            print('>>> Failed to get Job Analysis Page Response.')
        finally:
            # send request to company page ajax link, if it has not been crawled.
            link = response.meta['link']
            if link['company_ajax_link'] in crawled_company_urls:
                yield item
            else:
                yield Request(url=link['company_ajax_link'],
                                callback=self.parse_company_ajax_response,
                                meta={'item': item, 'link': link},
                                dont_filter=True)


    def parse_company_ajax_response(self, response):
        # print('>>> Parse company page')
        if response.status != 200:
            return None

        try:
            # set company page to item
            company_page_json = json.loads(clean_text(response.text))
            item = response.meta['item']
            item['company_page'] = company_page_json
        except:
            print('>>> Failed to get Company Page Response.')
        finally:
            # add company url to crawled list
            global crawled_company_urls
            link = response.meta['link']
            crawled_company_urls.append(link['company_ajax_link'])

            # yield item to pipeline
            yield item


    @staticmethod
    def transform_search_link_to_ajax_link(link):
        ''' Change url's path, and the website will return json-response instead of html.
        For example, "https://www.104.com.tw/jobs/search/?ro=0" to "https://www.104.com.tw/jobs/search/list?ro=0"
        '''
        url_parse = urlparse(link)
        endswith_word = 'list'
        if url_parse.path.endswith(endswith_word):
            return link
        new_path = url_parse.path + endswith_word
        url_parse = url_parse._replace(path=new_path)
        ajax_link = urlunparse(url_parse)
        return ajax_link


    @staticmethod
    def get_job_id_from_link(link):
        try:
            return re.search('job\/(.*)\?', link).group(1)
        except:
            print(f'There is no JOB_ID. (link: {link})')
            return None


    @staticmethod
    def get_company_id_from_link(link):
        try:
            return re.search('company/(.*)\?', link).group(1)
        except:
            print(f'There is no COMPANY_ID. (link: {link})')
            return None


    @staticmethod
    def get_job_ajax_link(link, job_id):
        url_parse = urlparse(link)
        new_url_parse = url_parse._replace(scheme='https', path=f'/job/ajax/content/{job_id}', query='')
        job_ajax_link = urlunparse(new_url_parse)
        return job_ajax_link


    @staticmethod
    def get_analysis_ajax_link(link, job_no):
        url_parse = urlparse(link)
        new_url_parse = url_parse._replace(scheme='https', path='/jb/104i/applyAnalysisToJob/all', query=f'job_no={job_no}')
        job_analysis_ajax_link = urlunparse(new_url_parse)
        return job_analysis_ajax_link


    @staticmethod
    def get_company_ajax_link(link, company_id):
        url_parse = urlparse(link)
        new_url_parse = url_parse._replace(scheme='https', path=f'/company/ajax/content/{company_id}', query=f'')
        company_ajax_link = urlunparse(new_url_parse)
        return company_ajax_link


class StartUrlProcessor:

    def process(self, url):
        # transform url to ajax url
        ajax_url = self.transform_search_url_to_ajax_url(url)
        print('ajax_url')
        print(ajax_url)

        # get query parameters
        url_param = self.get_url_query_param(ajax_url)
        print('url_param')
        print(url_param)

        # set query parameters to ajax url
        format_url_param = {**url_param, **DEFAULT_QUERY_PARAM}
        format_url = self.format_url_with_query_params(ajax_url, format_url_param)
        print('format_url')
        print(format_url)

        # subdivide query params if "total_page" >= MAX_TOTAL_PAGE
        all_page_urls = self.subdivide_url(format_url)
        print(all_page_urls)

        return all_page_urls


    @staticmethod
    def transform_search_url_to_ajax_url(url):
        ''' Change url's path, and the website will return json-response instead of html.
        For example, "https://www.104.com.tw/jobs/search/?ro=0" to "https://www.104.com.tw/jobs/search/list?ro=0"
        '''
        url_parse = urlparse(url)
        endswith = 'list'
        if url_parse.path.endswith(endswith):
            return url
        new_path = url_parse.path + endswith
        url_parse = url_parse._replace(path=new_path)
        new_url = urlunparse(url_parse)
        return new_url


    @staticmethod
    def get_url_query_param(url) -> dict:
        ''' Get query parameters in url. For example,
        input: "https://www.104.com.tw/jobs/search/list?ro=0&keyword=python",
        return: {'ro': '0', 'keyword': 'python'}
        '''
        url_parse = urlparse(url)
        return dict(parse_qsl(url_parse.query))


    @staticmethod
    def format_url_with_query_params(url, new_query_params={}):
        ''' Set formatted query parameters to url. Parameters are in "DEFAULT_QUERY_PARAM".
        '''
        url_parse = urlparse(url)
        url_query = dict(parse_qsl(url_parse.query))
        url_query.update(new_query_params)
        new_url_query = urlencode(url_query)
        url_parse = url_parse._replace(query=new_url_query)
        new_url = urlunparse(url_parse)
        return new_url


    @staticmethod
    def get_total_page_from_search_page(url):
        ''' temp: Get the total page number of result
        '''
#         return 1 # 150
        headers = {'Referer': url}
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            j = json.loads(response.text)
            total_page = j['data']['totalPage']
            return total_page
        print('Error happened, when get total page')
        return None


    @classmethod
    def subdivide_url(cls, url, urls=[]):
        ''' If the result of totlaPage is more than "MAX_TOTAL_PAGE", then subdivide url,
        based on area, job category, and industry category.
        '''
        # get the result of total page number
        total_page = cls.get_total_page_from_search_page(url)

        # if total page is 0, then drop the url
        if total_page == 0:
            return urls

        # if total page is less than MAX_TOTAL_PAGE, then return url
        if total_page < MAX_TOTAL_PAGE:
            print(f'>>> URL: {url}')
            print(f'    Total Pages: {total_page}')

            # generate urls with all pages
            page_urls = cls.generate_each_page_url_from_start_url(url, total_page)
            urls.extend(page_urls)
            return urls

        # subdivide area, jobcat, indust code
        area_urls = cls.subdivide_area(url)
        jobcat_urls = cls.subdivide_job_category(url)
        indust_urls = cls.subdivide_industry_category(url)

        if area_urls:
            for area_url in area_urls:
                urls = cls.subdivide_url(area_url, urls)

        elif jobcat_urls:
            for jobcat_url in jobcat_urls:
                urls = cls.subdivide_url(jobcat_url, urls)

        elif indust_urls:
            for indust_url in indust_urls:
                urls = cls.subdivide_url(indust_url, urls)

        else:
            # if total page is still more then MAX_TOTAL_PAGE, return url
            print(f'>>> URL: {url}')
            print(f'    It is still more than {MAX_TOTAL_PAGE} pages.')
            if url not in urls:
                # generate urls with all pages
                page_urls = cls.generate_each_page_url_from_start_url(url, total_page)
                urls.extend(page_urls)

        return urls


    @classmethod
    def subdivide_area(cls, url):
        # get query param
        url_param = cls.get_url_query_param(url)

        # get area code in url
        url_area_code = url_param.get('area', 'root')
        if url_area_code not in AREA_BREAKDOWN_DICT.keys():
            return None

        # subdivide area
        area_code_list = AREA_BREAKDOWN_DICT[url_area_code]
        urls = []
        for area_code in area_code_list:
            new_url = cls.format_url_with_query_params(url, {'area': area_code})
            urls.append(new_url)

        return urls


    @classmethod
    def subdivide_job_category(cls, url):
        # get query param
        url_param = cls.get_url_query_param(url)

        # get jobcat code in url
        url_jobcat_code = url_param.get('jobcat', 'root')
        if url_jobcat_code not in JOBCAT_BREAKDOWN_DICT.keys():
            return None

        # subdivide job category
        jobcat_code_list = JOBCAT_BREAKDOWN_DICT[url_jobcat_code]
        urls = []
        for jobcat_code in jobcat_code_list:
            new_url = cls.format_url_with_query_params(url, {'jobcat': jobcat_code})
            urls.append(new_url)

        return urls


    @classmethod
    def subdivide_industry_category(cls, url):
        # get query param
        url_param = cls.get_url_query_param(url)

        # get indust code in url
        url_indust_code = url_param.get('indust', 'root')
        if url_indust_code not in INDUST_BREAKDOWN_DICT.keys():
            return None

        # subdivide industry category
        indust_code_list = INDUST_BREAKDOWN_DICT[url_indust_code]
        urls = []
        for indust_code in indust_code_list:
            new_url = cls.format_url_with_query_params(url, {'indust': indust_code})
            urls.append(new_url)

        return urls


    @classmethod
    def generate_each_page_url_from_start_url(cls, url, pages):
        urls = []
        for p in range(pages):
            next_page_url = cls.format_url_with_query_params(url, {'page': p+1})
            urls.append(next_page_url)
        return urls


# utils ===========================================
def convert_full_width_to_half_width(text: str) -> str:
    ''' convert full-width character to half-width one, such as "Ａ" to "A"
    '''
    text = unicodedata.normalize('NFKC', text)
    return text


def remove_unicode_text(text: str) -> str:
    text = text.replace('\xa0', '')
    text = text.replace('\u3000', '')
    text = text.replace('\r', '')
    return text


def remove_extra_newline(text: str) -> str:
    text = re.sub('\n+', '\n', text)
    return text


def clean_text(text: str) -> str:
    text = convert_full_width_to_half_width(text)
    text = remove_unicode_text(text)
    text = remove_extra_newline(text)
    return text
# =================================================


def test():
    import pdb
    pdb.set_trace()

#js-job-content > article:nth-child(12) > div.b-block__left > ul:nth-child(2) > li:nth-child(2) > a
# response.css('a[href*=image] img::attr(src)').getall()