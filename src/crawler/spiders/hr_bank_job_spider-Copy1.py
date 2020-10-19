# -*- coding: utf-8 -*-
import scrapy
import re
import json
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, parse_qsl
from scrapy.http.request import Request
from scrapy.utils.project import get_project_settings
from copy import deepcopy
from datetime import datetime

from crawler.items import HrBankJobItem


MAX_TOTAL_PAGE = 150
DEFAULT_QUERY_PARAM = {
    # not recommended to change
    'page': 1,     # 頁數
    'mode': 's',   # s: 摘要顯示
    'order': 11,   # 11: 日期排序
    'ro': 0,       # 0: 全部職缺, 1: 全職職缺
    'asc': 0,      # 0: 降冪排序, 1: 升冪排序
}
SETTINGS = get_project_settings()
logging = SETTINGS['logging']

print('>>> Load Reference...')
def _get_json_file(path):
    with open(path, 'r') as f:
        return json.loads(f.read())

def _generate_child_node_dict(tree, d={}):
    ''' According to a tree, generate child nodes for each node.
    '''
    d = deepcopy(d)
    if 'n' in tree.keys():
        root = tree.get('no', 'root')
        nodes = []
        for node in tree['n']:
            nodes.append(node['no'])
            if 'no' in node.keys():
                d = _generate_child_node_dict(node, d)
        d[root] = nodes    
    return d

JSON_JOBCAT_ROOT = _get_json_file('crawler/reference/jsonJobCatRoot')
JSON_AREA_ROOT = _get_json_file('crawler/reference/jsonAreaRoot')
JSON_INDUST_ROOT = _get_json_file('crawler/reference/jsonIndustRoot')
CHILD_AREA_MAP_DICT = _generate_child_node_dict(JSON_AREA_ROOT)
CHILD_JOBCAT_MAP_DICT = _generate_child_node_dict(JSON_JOBCAT_ROOT)
CHILD_INDUST_MAP_DICT = _generate_child_node_dict(JSON_INDUST_ROOT)
print('>>> Load Reference... OK!')    


crawl_count = 0

class HrBankJobSpider(scrapy.Spider):
    name = 'hr_bank_job'
    allowed_domains = ['104.com.tw']
    denied_urls = [
        'http://www.104.com.tw/jobs/main/', 
        'http://www.104.com.tw/robots.txt',
        'http://www.tutor.104.com.tw/',
        'http://www.hunter.104.com.tw/',
    ]
#     start_urls = ['https://www.104.com.tw/jobs/search/?ro=0&keyword=%E7%88%AC%E8%9F%B2&jobcatExpansionType=0']
    start_urls = ['https://www.104.com.tw/jobs/search/?ro=1&jobcat=2007000000&jobcatExpansionType=0&area=6001001000&order=4&asc=1&page=1&mode=s']
    
    def __init__(self, **kwargs): 
        super(HrBankJobSpider, self).__init__(**kwargs)

        
    def start_requests(self):
        ''' Override default "start_requests" function in order to format "start_urls", and then start to crawl.
        '''
        if not self.start_urls and hasattr(self, 'start_url'):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found "
                "or empty (but found 'start_url' attribute instead, "
                "did you miss an 's'?)")
        else:
            for start_url in self.start_urls:
                urls = self.start_url_getter(start_url)
                print(f'\n>>> "start_urls":\n{len(urls)}\n')
                print('>>> Start To Crawl')
                for url in urls:
                    yield Request(url=url, callback=self.parse, dont_filter=True)

                    
    def start_url_getter(self, url):
        ''' According to url, format the url with query parameters, and subdivide url if it needs, 
        and then generate all pages of url.
        '''
        format_url = self._format_url_query_param(url)
        start_search_page_url = self._subdivide_url(format_url, sd_area=True)
        urls = start_search_page_url # to do: make the url from page 1 to the end
        return urls
    
    
    @classmethod
    def _format_url_query_param(cls, url, query_param=DEFAULT_QUERY_PARAM):
        ''' Transform url to json-response url, and set query parameters.
        '''
        url = cls._transform_url_to_json_response_url(url, endswith='list')
        url_param = cls._get_url_query_param_dict(url)
        new_url = cls._generate_url_with_new_query_params(url, query_param)
        return new_url
    
    
    @staticmethod
    def _transform_url_to_json_response_url(url, endswith):
        ''' Change url's path, and the website will return json-response instead of html.
        For example, "https://www.104.com.tw/jobs/search/?ro=0" to "https://www.104.com.tw/jobs/search/list?ro=0"
        '''
        url_parse = urlparse(url)
        if url_parse.path.endswith(endswith):
            return url
        new_path = url_parse.path + endswith
        url_parse = url_parse._replace(path=new_path)
        new_url = urlunparse(url_parse)
        return new_url

    
    @staticmethod
    def _get_url_query_param_dict(url):
        url_parse = urlparse(url)
        return dict(parse_qsl(url_parse.query))
    

    @staticmethod
    def _generate_url_with_new_query_params(url, new_query_params={}):
        url_parse = urlparse(url)
        url_query = dict(parse_qsl(url_parse.query))
        url_query.update(new_query_params)
        new_url_query = urlencode(url_query)
        url_parse = url_parse._replace(query=new_url_query)
        new_url = urlunparse(url_parse)
        return new_url
    
    
    def parse(self, response):
        global crawl_count
        j = json.loads(response.text)
        if j['status'] == 200:
            page_job_count = 0
            for job in j['data']['list']:
                page_job_count += 1
                print(f'>>> PAGE JOB COUNT: {page_job_count}')
                crawl_count += 1
                if crawl_count % 100 == 0:
                    print(f'>>> CRAWL COUNT: {crawl_count}')
                
                ##### temp for test
#                 if crawl_count >3:#
#                     break#
                ##### temp for test
                
        
                item = HrBankJobItem()
                
                # parse search page
#                 self._parse_search_job_json_response(item, job)
                
                # job description page
                job_link = self._get_job_ajax_link(job)
                yield Request(job_link, self._parse_job_json_response, meta={'item': item, 'job': job})
                
#                 # job analysis page
#                 job_analysis_link = self._get_job_analysis_ajax_link(job)
#                 yield Request(job_analysis_link, self._parse_job_analysis_json_response, meta={'item': item})
                
#                 # company description page
#                 company_link = self._get_company_ajax_link(job)
#                 yield Request(company_link, self._parse_company_json_response, meta={'item': item})
                
#                 if item['job_desc_json'] and item['comp_desc_json']:
#                     yield item

    
    def _parse_search_job_json_response(self, item, j):
        item['search_job_json'] = json.dumps(j, ensure_ascii=False)
        item['job_no'] = str(j['jobNo'])
        item['job_id'] = self._get_job_id(j)
        item['job_name'] = j['jobName']
        item['comp_no'] = str(j['custNo'])
        item['comp_id'] = self._get_company_id(j)
        item['comp_name'] = j['custName']
        item['indust_no'] = str(j['coIndustry'])
        item['indust_desc'] = j['coIndustryDesc']
        item['appear_date'] = int(j['appearDate'])
        item['crawl_date'] = int(datetime.now().strftime('%Y%m%d'))
        return item
    

    def _parse_job_json_response(self, response):
        item = response.meta['item']
        job = response.meta['job']
        j = json.loads(response.text)
        item['job_desc_json'] = 'test_job_desc'
        
        # job analysis page
        job_analysis_link = self._get_job_analysis_ajax_link(job)
        yield Request(job_analysis_link, self._parse_job_analysis_json_response, meta={'item': item, 'job': job})
        
#         item['job_desc_json'] = json.dumps(j, ensure_ascii=False)
#         return item
    
    
    def _parse_job_analysis_json_response(self, response):
        item = response.meta['item']
        job = response.meta['job']
        j = json.loads(response.text)
        item['job_analysis_json'] = 'test_analysis'
        
        # company description page
        company_link = self._get_company_ajax_link(job)
        yield Request(company_link, self._parse_company_json_response, meta={'item': item, 'job': job})
        
#         item['job_analysis_json'] = json.dumps(j, ensure_ascii=False)
#         return item
    
    
    def _parse_company_json_response(self, response):
        item = response.meta['item']
        j = json.loads(response.text)
        
        item['comp_desc_json'] = 'test_comp_desc'
        if item['job_desc_json'] and item['comp_desc_json']:
            yield item
        
#         item['comp_desc_json'] = json.dumps(j, ensure_ascii=False)
#         return item

    
    @staticmethod
    def _get_job_id(j):
        try:
            link = j['link']['job']
            return re.search('job\/(.*)\?', link).group(1)
        except:
            print('There is no JOB_ID.', link)
            
    @staticmethod
    def _get_company_id(j):
        try:
            link = j['link']['cust']
            return re.search('company/(.*)\?', link).group(1)
        except:
            print(j)
            print('There is no COMP_ID.', link)
        
    
    @staticmethod
    def _get_job_ajax_link(j):
        link = j['link']['job']
        url_parse = urlparse(link)
        job_id = re.search('job\/(.*)', url_parse.path).group(1)
        new_url_parse = url_parse._replace(scheme='http', path=f'/job/ajax/content/{job_id}', query='')
        job_link = urlunparse(new_url_parse)
        return job_link
    
    
    @staticmethod
    def _get_job_analysis_ajax_link(j):
        link = j['link']['applyAnalyze']
        url_parse = urlparse(link)
        job_no = j['jobNo']
        new_url_parse = url_parse._replace(scheme='http', path='/jb/104i/applyAnalysisToJob/all', query=f'job_no={job_no}')
        job_analysis_link = urlunparse(new_url_parse)
        return job_analysis_link
    
    
    @staticmethod
    def _get_company_ajax_link(j):
        link = j['link']['cust']
        url_parse = urlparse(link)
        company_id = re.search('company/(.*)\?', link).group(1)
        new_url_parse = url_parse._replace(scheme='http', path=f'/company/ajax/content/{company_id}', query=f'jobsource=n104bank2')
        company_link = urlunparse(new_url_parse)
        return company_link


    def _subdivide_url(self, url, urls=[], sd_area=False, sd_jobcat=False, sd_indust=False):
        ''' If the result of totlaPage is more than "MAX_TOTAL_PAGE", then subdivide url, 
        based on area, job category, and company industry.
        '''
        total_page = self._get_total_page(url)
        if total_page >= MAX_TOTAL_PAGE:
            url_param = self._get_url_query_param_dict(url)
            if sd_area:
                area = url_param.get('area', 'root')
                child_node = CHILD_AREA_MAP_DICT.get(area, [])
                if child_node:
                    for value in child_node:
                        new_url = self._generate_url_with_new_query_params(url, {'area': value})
                        urls = self._subdivide_url(new_url, urls, sd_area=True)
                else:
                    sd_jobcat = True
            
            if sd_jobcat:
                jobcat = url_param.get('jobcat', 'root')
                child_node = CHILD_JOBCAT_MAP_DICT.get(jobcat, [])
                if child_node:
                    for value in child_node:
                        new_url = self._generate_url_with_new_query_params(url, {'jobcat': value})
                        urls = self._subdivide_url(new_url, urls, sd_jobcat=True)
                else:
                    sd_indust = True
                    
            if sd_indust:
                indust = url_param.get('indust', 'root')
                child_node = CHILD_INDUST_MAP_DICT.get(indust, [])
                if child_node:
                    for value in child_node:
                        new_url = self._generate_url_with_new_query_params(url, {'indust': value})
                        urls = self._subdivide_url(new_url, urls, sd_indust=True)
                else:
                    print('>>> Can not subdivide url.')
                    logging.warning(f'>>> Can not subdivide url. {url}')
        else:
            for p in range(1, total_page+1):
                next_page_url = self._generate_url_with_new_query_params(url, {'page': p})
                urls.append(next_page_url)
        return urls
    
    
    @staticmethod
    def _get_total_page(url):
        ''' temp: Get the total page number of result
        '''
#         headers = {'Referer': url}
        headers = SETTINGS['DEFAULT_REQUEST_HEADERS']
        r = requests.get(url, headers=headers)
        j = json.loads(r.text)
        print(f'>>> URL: {url}')
        print(f'    Total Page: {j["data"]["totalPage"]}')
        return j['data']['totalPage']
        

        
    