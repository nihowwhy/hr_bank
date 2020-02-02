# -*- coding: utf-8 -*-
import re
import time
import requests
from bs4 import BeautifulSoup
from itertools import product
from urllib.parse import urlparse, parse_qs, urlsplit, urlunsplit, urlencode

from config import config
from app.conf.conversion_table import AREA_DICT, INDUSTRY_DICT, JOBCAT_DICT


HEADERS = config['headers']
USE_PROXY = config['use_proxy']
PROXIES = config['proxies']


class ServiceImplHrBankCrawlerSplitUrl:
    

    @staticmethod
    def process(config, case, composition):
        return_url_list = []
        for url in case['start_urls']:
            split_url_list = []
            split_url_list = _split_url(url, split_url_list)
            if split_url_list:
                return_url_list.extend(split_url_list)
        return_url_list = list(set(return_url_list))
        case['start_urls'] = return_url_list
        composition['total_job_counts'] = total_counts
    
    

def _get_search_id(search_type: str, search_id: str=''):
    '''
    :param search_type: accept 'area', 'jobcat', 'indcat'
    '''
    if search_type == 'area':
        search_dict = AREA_DICT
    elif search_type == 'jobcat':
        search_dict = JOBCAT_DICT
    elif search_type == 'indcat':
        search_dict = INDUSTRY_DICT
    else:
        raise ValueError(f'Invalid search_type: {search_type}')

    next_search_id_list = []
    if search_id[-6:] == '000000':
        next_search_id_list = [ele_id for ele_id in search_dict.values() if ele_id[:4] == search_id[:4] and ele_id[-3:] == '000']
        next_search_id_list.remove(search_id)
    elif search_id[-3:] == '000':
        next_search_id_list = [ele_id for ele_id in search_dict.values() if ele_id[:7] == search_id[:7]]
        next_search_id_list.remove(search_id)
    elif search_id == '':
        next_search_id_list = [ele_id for ele_name, ele_id in search_dict.items() if ele_id[-6:] == '000000']
    return next_search_id_list

    

def _get_total_job_num(soup):
    total_job_num = re.findall('\"totalCount\":(\d+)', soup.text)
    if total_job_num:
        total_job_num = total_job_num[0]
        return total_job_num
    else:
        return None


def _send_request(url: str):
    if USE_PROXY:
        response = requests.get(url, headers=HEADERS, proxies=PROXIES, verify=False, allow_redirects=False)
    else:
        response = requests.get(url, headers=HEADERS, verify=False, allow_redirects=False)
    return response

    
total_counts = 0    
def _split_url(url: str, split_url_list: list):
    global total_counts
    
    # get total job num
    total_job_num = None
    while not total_job_num:
        response = _send_request(url)
        soup = BeautifulSoup(response.text, 'lxml')
        total_job_num = _get_total_job_num(soup)
        if not total_job_num:
            print('==============================')
            print('>>> ERROR:', url)
            print('==============================')
            time.sleep(2)
            

    print('counts:', total_job_num)
    print('url:', url)
    print()


    # if total job num is less than 3,000, then return
    if 0 < int(total_job_num) <= 3000:
        split_url_list.append(url)
        total_counts += int(total_job_num)
        print('==============================')
        print('>>> TOTAL COUNTS:', total_counts)
        print('==============================')
        return split_url_list

    elif int(total_job_num) == 0:
        return split_url_list


    # split urls
    is_modified = False
    

    # Page
    if 'page=' not in url and is_modified == False:
        is_modified = True
        next_url = url + f'&page=1'
        _split_url(next_url, split_url_list)

    
    # Area
    if 'area=' not in url and is_modified == False:
        print('>>> add area into url:', url)
        print()
        search_id_list = _get_search_id('area')
        for search_id in search_id_list:
            is_modified = True
            next_url = url + f'&area={search_id}'
            _split_url(next_url, split_url_list)

    elif 'area=' in url and is_modified == False:
        print('>>> split area url:', response.request.url)
        print()
        selected_search_id = re.search('area=(\d+)', response.request.url).group(1)
        if '%2C' not in selected_search_id:
            search_id_list = _get_search_id('area', selected_search_id)
            for search_id in search_id_list:
                is_modified = True
                next_url = re.sub('(area=)\d+', '\g<1>{}'.format(search_id), url)
                _split_url(next_url, split_url_list)
    
    
    # Industry category
    if 'indcat=' not in url and is_modified == False:
        print('>>> add indcat into url:', url)
        print()
        search_id_list = _get_search_id('indcat')
        for search_id in search_id_list:
            is_modified = True
            next_url = url + f'&indcat={search_id}'
            _split_url(next_url, split_url_list)

    elif 'indcat=' in url and is_modified == False:
        print('>>> split indcat url:', response.request.url)
        print()
        selected_search_id = re.search('indcat=(\d+)', response.request.url).group(1)
        if '%2C' not in selected_search_id:
            search_id_list = _get_search_id('indcat', selected_search_id)
            for search_id in search_id_list:
                is_modified = True
                next_url = re.sub('(indcat=)\d+', '\g<1>{}'.format(search_id), url)
                _split_url(next_url, split_url_list)
    
    
    # Multiple searching conditions
    if is_modified == False:
        scheme, netloc, path, query_string, fragment = urlsplit(url)
        
        query_dict = parse_qs(query_string)
        query_dict = {key: value[0].split(',') for key, value in query_dict.items()}
        query_value_combination_list = list(product(*(query_dict[query_key] for query_key in query_dict.keys())))
        
        for query_value_combination in query_value_combination_list:
            
            new_query_dict = {}
            for query_key, query_value in zip(query_dict.keys(), query_value_combination):
                new_query_dict[query_key] = [query_value]
            
            is_modified = True
            new_query_string = urlencode(new_query_dict, doseq=True)
            new_url = urlunsplit((scheme, netloc, path, new_query_string, fragment))
            _split_url(new_url, split_url_list)

            
    # Job category
    if 'jobcat=' not in url and is_modified == False:
        print('>>> add jobcat into url:', url)
        print()
        search_id_list = _get_search_id('jobcat')
        for search_id in search_id_list:
            is_modified = True
            next_url = url + f'&jobcat={search_id}'
            _split_url(next_url, split_url_list)

    elif 'jobcat=' in url and is_modified == False:
        print('>>> split jobcat url:', response.request.url)
        print()
        selected_search_id = re.search('jobcat=(\d+)', response.request.url).group(1)
        search_id_list = _get_search_id('jobcat', selected_search_id)
        for search_id in search_id_list:
            is_modified = True
            next_url = re.sub('(jobcat=)\d+', '\g<1>{}'.format(search_id), url)
            _split_url(next_url, split_url_list)
            
            
    return split_url_list