CONFIG_INI_DIR = '../../config.ini'

# config.ini
import configparser
config = configparser.ConfigParser()
config.read(CONFIG_INI_DIR)

# config.ini setting
log_folder = config['setting']['log_folder']
db_folder = config['setting']['db_folder']
db_name = config['setting']['hr_bank_db_name']

DB_CONNECTION_STRING = f'sqlite:///{db_folder}/{db_name}'


import re
import json
import unicodedata
import pandas as pd
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from urllib.parse import urljoin

from model.model import db_connect, create_table, TRawSearch, TRawJob, TRawJobAnalysis, TRawComp, TJob, TJobAnalysis, TComp


DOMAIN_URL = 'https://www.104.com.tw/'


# process =================================================================

class JobDataFormatter:
    
    def __init__(self):
        engine = db_connect(DB_CONNECTION_STRING)
        create_table(engine)
        self.Session = sessionmaker(bind=engine)


    def process(self):
        session = self.Session()
        records = []
        
        try:
            results = session.query(TRawSearch).all() # main table
        except Exception as e:
            print(e)
            logging.error('can not get data from "TRawSearch".')
            session.close()
            return records
        
        for i, r in enumerate(results):
            print(f'>>> processing {i} record...')
            job_no = r.job_no
            crawl_date = r.crawl_date
            logging.info(f'process record: JOB_NO={job_no}, CRAWL_DATE={crawl_date}')
            
            try:
                # job list content
                json_string = clean_json(r.json_string)
                search_json = json.loads(json_string)
                search_json = _parse_job_list_content(search_json)

                # job detail
                raw_job = session.query(TRawJob).filter(job_no==job_no, crawl_date==crawl_date).first()
                if raw_job:
                        json_string = clean_json(raw_job.json_string)
                        job_json = json.loads(json_string)
                        job_json = _parse_job_detail_content(job_json['data'])
                else:
                    job_json = {}

                # analysis
                raw_analysis = session.query(TRawJobAnalysis).filter(job_no==job_no, crawl_date==crawl_date).first()
                if raw_analysis:
                    json_string = clean_json(raw_analysis.json_string)
                    analysis_json = json.loads(json_string)
                    analysis_json = _parse_analysis_content(analysis_json)
                else:
                    analysis_json = {}
                
                # combine as one record
                record = {**analysis_json, **job_json, **search_json}
                records.append(record)
                print(f'>>> processing {i} record... Done!')
                
            except Exception as e:
                print(e)
                logging.error(f'No. {i} record:\nJOB_NO={job_no}\nCRAWL_DATE={crawl_date}\n{e}')
                
        session.close()
        return records
    
# process =================================================================


# search ==================================================================

def _parse_job_list_content(crawled_dict: dict) -> dict:
    parsed_job = {}
    
    # 職缺類型
    parsed_job['job_type'] = crawled_dict['jobType']
    
    # 職缺編號
    parsed_job['job_no'] = crawled_dict['jobNo']
    
    # 職缺名稱
    parsed_job['job_name'] = crawled_dict['jobName']
    
    # 工作性質：全職、兼職...
    parsed_job['job_role'] = crawled_dict['jobRole']
    
    # 工作地區：台北市信義區...
    parsed_job['job_addr_dist'] = crawled_dict['jobAddrNoDesc']
    
    # 職缺內容
    parsed_job['job_detail'] = crawled_dict['description']
    
    # 學歷要求
    parsed_job['edu'] = crawled_dict['optionEdu']
    
    # 工作經驗要求
    parsed_job['work_exp'] = int(crawled_dict['period'])
    
    # 應徵人數
    parsed_job['apply_count'] = int(crawled_dict['applyCnt'])
    
    # 公司編號
    parsed_job['comp_no'] = crawled_dict['custNo']
    
    # 公司名稱
    parsed_job['comp_name'] = crawled_dict['custName']
    
    # 產業編號
    parsed_job['indust_no'] = crawled_dict['coIndustry']
    
    # 產業描述
    parsed_job['indust_desc'] = crawled_dict['coIndustryDesc']
    
    # 最低薪資
    parsed_job['salary_min'] = int(crawled_dict['salaryLow'])
    
    # 最高薪資
    parsed_job['salary_max'] = int(crawled_dict['salaryHigh'])
    
    # 薪資描述
    parsed_job['salary_desc'] = crawled_dict['salaryDesc']
    
    # 薪資類型
    parsed_job['salary_type'] = crawled_dict['s10']
    
    # 開缺日期
    parsed_job['appear_date'] = int(crawled_dict['appearDate'])
    
    # 職缺標籤
    parsed_job['job_tag'] = join_element_in_list(crawled_dict['tags'])
    
    # 工作地點地標
    parsed_job['landmark_tag'] = crawled_dict['landmark']
    
    # 職缺連結
    try:
        parsed_job['job_url'] = urljoin(DOMAIN_URL, crawled_dict['link']['job'])
    except:
        parsed_job['job_url'] = ''
    
    # 應徵分析連結
    try:
        parsed_job['analysis_url'] = urljoin(DOMAIN_URL, crawled_dict['link']['applyAnalyze'])
    except:
        parsed_job['analysis_url'] = ''
    
    # 公司連結
    try:
        parsed_job['comp_url'] = urljoin(DOMAIN_URL, crawled_dict['link']['cust'])
    except:
        parsed_job['comp_url'] = ''
    
    # 工作地點經度
    parsed_job['lon'] = crawled_dict['lon']
    
    # 工作地點緯度
    parsed_job['lat'] = crawled_dict['lat']
    
    return parsed_job


def _get_web_link(arg: str) -> str:
    try:
        return urljoin(DOMAIN_URL, crawled_dict['link'][arg])
    except:
        return ''
    
# search ==================================================================


# detail ==================================================================

def _parse_job_detail_content(crawled_dict: dict) -> dict:
    parsed_job = {}
    
    # 職缺名稱
    parsed_job['job_name'] = crawled_dict['header']['jobName']
    
    # 開缺日期
#     parsed_job['appear_date'] = int(re.sub('/', '', crawled_dict['header']['appearDate'])) # second choice

    # 公司名稱
    parsed_job['comp_name'] = crawled_dict['header']['custName']
    
    # 公司連結
    try:
        parsed_job['comp_url'] = urljoin(DOMAIN_URL, crawled_dict['header']['custUrl'])
    except:
        parsed_job['comp_url'] = ''
    
    # 分析類型
    parsed_job['analysis_type'] = crawled_dict['header']['analysisType']
    
    # 應徵分析連結
    try:
        parsed_job['analysis_url'] = urljoin(DOMAIN_URL, crawled_dict['header']['analysis_url'])
    except:
        parsed_job['analysis_url'] = ''
        
    # 接受身份
    parsed_job['accept_role'] = join_dict_item_in_list(
        crawled_dict['condition']['acceptRole']['role'], 'description') 
    
    # 婉拒身份
    parsed_job['accept_role'] = join_dict_item_in_list(
        crawled_dict['condition']['acceptRole']['disRole']['disability'], 'type') 
    
    # 工作經驗要求
#     parsed_job['work_exp'] = int(crawled_dict['condition']['workExp']) # second choice
    
    # 學歷要求
#     parsed_job['edu'] = crawled_dict['condition']['edu'] # second choice
    
    # 科系要求
    parsed_job['major'] = join_element_in_list(crawled_dict['condition']['major'])
    
    # 語言要求
    parsed_job['lang'] = join_dict_item_in_list(crawled_dict['condition']['language'], 'language')
    
    # 地方語言要求
    parsed_job['local_lang'] = join_dict_item_in_list(crawled_dict['condition']['localLanguage'], 'language')
    
    # 工具要求
    parsed_job['specialty'] = join_dict_item_in_list(crawled_dict['condition']['specialty'], 'description')
    
    # 技能要求
    parsed_job['skill'] = join_dict_item_in_list(crawled_dict['condition']['skill'], 'description')
    
    # 證照要求
    parsed_job['cert'] = join_element_in_list(crawled_dict['condition']['certificate'])
    
    # 駕照要求
#     parsed_job['driver_license'] = join_element_in_list(crawled_dict['condition']['driverLicense'])
    
    # 其他要求
    parsed_job['other'] = crawled_dict['condition']['other']
    
    # 職缺內容
    parsed_job['job_detail'] = crawled_dict['jobDetail']['jobDescription']
    
    # 職缺分類
    parsed_job['job_cat'] = join_dict_item_in_list(crawled_dict['jobDetail']['jobCategory'], 'description')
    
    # 最低薪資
    parsed_job['salary_min'] = int(crawled_dict['jobDetail']['salaryMin'])
    
    # 最高薪資
    parsed_job['salary_max'] = int(crawled_dict['jobDetail']['salaryMax'])
    
    # 薪資描述
    parsed_job['salary_desc'] = crawled_dict['jobDetail']['salary']
    
    # 薪資類型
    parsed_job['salary_type'] = crawled_dict['jobDetail']['salaryType']
    
    # 職缺類型
    parsed_job['job_type'] = crawled_dict['jobDetail']['jobType']
    
    # 工作性質：全職、兼職...
    parsed_job['job_role'] = crawled_dict['jobDetail']['workType'] # or work_type?
    
    # 工作地區：台北市信義區...
    parsed_job['job_addr_dist'] = crawled_dict['jobDetail']['addressRegion']
    
    # 工作地點經度
    parsed_job['lon'] = crawled_dict['jobDetail']['longitude']
    
    # 工作地點緯度
    parsed_job['lat'] = crawled_dict['jobDetail']['latitude']
    
    # 管理責任
    parsed_job['manage_resp'] = crawled_dict['jobDetail']['manageResp']
    
    # 出差外派
    parsed_job['business_trip'] = crawled_dict['jobDetail']['businessTrip']
    
    # 上班時段
    parsed_job['work_period'] = crawled_dict['jobDetail']['workPeriod']
    
    # 休假制度
    parsed_job['vacation_policy'] = crawled_dict['jobDetail']['vacationPolicy']
    
    # 可上班日
    parsed_job['start_work_day'] = crawled_dict['jobDetail']['startWorkingDay']
    
    # 招募類型：0公司自聘、1代徵
    parsed_job['hire_type'] = crawled_dict['jobDetail']['hireType']
    
    # 委託招募單位
    parsed_job['delegate_recruit'] = crawled_dict['jobDetail']['delegatedRecruit']
    
    # 需求人數
    parsed_job['need_emp'] = crawled_dict['jobDetail']['needEmp']
    
    # 最少需求人數
    parsed_job['need_count_min'] = _get_need_emp_min(parsed_job['need_emp'])
    
    # 最少需求人數
    parsed_job['need_count_max'] = _get_need_emp_max(parsed_job['need_emp'])
    
    # 職缺狀況
#     parsed_job['switch'] = crawled_dict['switch']['needEmp']
    
    # 產業描述
    parsed_job['indust_desc'] = crawled_dict['industry']
    
    # 公司編號
    parsed_job['comp_no'] = crawled_dict['custNo']
    
    return parsed_job
   
    
def _get_need_emp_min(need_emp_string):
    result = re.findall('(\d+)', need_emp_string)
    if result:
        return result[0]
    else:
        return 1
    
    
def _get_need_emp_max(need_emp_string):
    result = re.findall('(\d+)', need_emp_string)
    if result:
        return result[-1]
    else:
        return 99
    
# detail ==================================================================


# analysis ================================================================

def _parse_analysis_content(crawled_dict: dict) -> dict:
    parsed_job = {}
    
    for type_, data in crawled_dict.items():
        
        # 資料更新時間
        if 'update_time' not in crawled_dict.keys():
            update_time = ''.join(re.findall('\d+', crawled_dict[type_]['update_time'][:10]))
            parsed_job['update_time'] = int(update_time)
        
        # 應徵人數
        if 'apply_count' not in crawled_dict.keys():
            parsed_job['apply_count'] = int(crawled_dict[type_]['total'])
    
    # 應徵人數資料整理
    apply_count_dict = _convert_analysis_json(crawled_dict)
    
    # 性別
    parsed_job['sex_m'] = apply_count_dict['sex']['男']
    parsed_job['sex_f'] = apply_count_dict['sex']['女']
    
    # 學歷
    parsed_job['edu_na'] = apply_count_dict['edu']['無法判斷']
    parsed_job['edu_no'] = apply_count_dict['edu']['不拘']
    parsed_job['edu_jr'] = apply_count_dict['edu']['國中(含)以下']
    parsed_job['edu_sr'] = apply_count_dict['edu']['高中職']
    parsed_job['edu_jr_coll'] = apply_count_dict['edu']['專科']
    parsed_job['edu_undergrad'] = apply_count_dict['edu']['大學']
    parsed_job['edu_grad'] = apply_count_dict['edu']['博碩士']

    # 年齡
    parsed_job['age_00_20'] = apply_count_dict['age']['20歲以下']
    parsed_job['age_21_25'] = apply_count_dict['age']['21~25歲']
    parsed_job['age_26_30'] = apply_count_dict['age']['26~30歲']
    parsed_job['age_31_35'] = apply_count_dict['age']['31~35歲']
    parsed_job['age_36_40'] = apply_count_dict['age']['36~40歲']
    parsed_job['age_41_45'] = apply_count_dict['age']['41~45歲']
    parsed_job['age_46_50'] = apply_count_dict['age']['46~50歲']
    parsed_job['age_51_55'] = apply_count_dict['age']['51~55歲']
    parsed_job['age_56_60'] = apply_count_dict['age']['56~60歲']
    parsed_job['age_60_99'] = apply_count_dict['age']['60歲以上']
    
    # 工作經驗
    parsed_job['work_exp_no'] = apply_count_dict['work_exp']['無工作經驗']
    parsed_job['work_exp_00_01'] = apply_count_dict['work_exp']['1年以下']
    parsed_job['work_exp_01_03'] = apply_count_dict['work_exp']['1~3年']
    parsed_job['work_exp_03_05'] = apply_count_dict['work_exp']['3~5年']
    parsed_job['work_exp_05_10'] = apply_count_dict['work_exp']['5~10年']
    parsed_job['work_exp_10_15'] = apply_count_dict['work_exp']['10~15年']
    parsed_job['work_exp_15_20'] = apply_count_dict['work_exp']['15~20年']
    parsed_job['work_exp_20_25'] = apply_count_dict['work_exp']['20~25年']
    parsed_job['work_exp_25_99'] = apply_count_dict['work_exp']['25年以上']

    # 語言
    filter_list = ['英文', '中文', '日文', '韓文']
    parsed_job['lang'] = apply_count_dict['lang'].get('英文', 0)
    parsed_job['lang'] = apply_count_dict['lang'].get('中文', 0)
    parsed_job['lang'] = apply_count_dict['lang'].get('日文', 0)
    parsed_job['lang'] = apply_count_dict['lang'].get('韓文', 0)
    parsed_job['lang'] = _get_other_apply_count(apply_count_dict['lang'], filter_list)
    
    # 科系
    filter_list = ['資訊管理相關', '資訊工程相關', '統計學相關', '數理統計相關']
    parsed_job['major_info_mgmt'] = apply_count_dict['major'].get('資訊管理相關', 0)
    parsed_job['major_cs'] = apply_count_dict['major'].get('資訊工程相關', 0)
    parsed_job['major_stat'] = apply_count_dict['major'].get('統計學相關', 0)
    parsed_job['major_math_stat'] = apply_count_dict['major'].get('數理統計相關', 0)
    parsed_job['major_other'] = _get_other_apply_count(apply_count_dict['major'], filter_list)

    # 技能
    filter_list = ['Java', 'Python']
    parsed_job['skill_java'] = apply_count_dict['skill'].get('Java', 0)
    parsed_job['skill_python'] = apply_count_dict['skill'].get('Python', 0)
    parsed_job['skill_other'] = _get_other_apply_count(apply_count_dict['skill'], filter_list)
    
    # 證照
    filter_list = ['國際專案管理師PMP']
    parsed_job['cert_pmp'] = apply_count_dict['cert'].get('國際專案管理師PMP', 0)
    parsed_job['cert_other'] = _get_other_apply_count(apply_count_dict['cert'], filter_list)

    return parsed_job
    

def _convert_analysis_json(analysis_dict: dict) -> dict:
    type_list = ['sex', 'edu', 'yearRange', 'exp', 'language', 'major', 'skill', 'cert']
    new_analysis_dict = {}

    for type_ in type_list:

        if type_ == 'sex':
            new_key = 'sex'

        elif type_ == 'edu':
            new_key = 'edu'

        elif type_ == 'yearRange':
            new_key = 'age'

        elif type_ == 'exp':
            new_key = 'work_exp'

        elif type_ == 'language':
            new_key = 'lang'

        elif type_ == 'major':
            new_key = 'major'

        elif type_ == 'skill':
            new_key = 'skill'

        elif type_ == 'cert':
            new_key = 'cert'
            
        else:
            new_key = type_

        new_analysis_dict[new_key] = {}
        for k1, v1 in analysis_dict[type_].items():
            if k1.isdigit():
                for k2, v2 in v1.items():
                    if 'Name' in k2:
                        new_analysis_dict[new_key][v2.strip()] = int(v1['count'])
                        break
                        
    return new_analysis_dict


def _get_other_apply_count(apply_count: dict, filter_list: list) -> int:
    other_count = 0
    for k, v in apply_count.items():
        if k in filter_list:
            continue
        other_count += v
    return other_count

# analysis ================================================================


# utils ===================================================================

def remove_unicode_blank(text):
    text = text.replace('\xa0', '')
    text = text.replace('\u3000', '')
    text = text.replace('\r', '')
    return text

    
def join_dict_item_in_list(l: list, key: str):
    ''' input:  [{"name": "Ian"}, {"name": "Wang"}]
        output: "Ian、Wang"
    '''
    dict_item_list = [d[key] for d in l]
    return '、'.join(dict_item_list)


def join_element_in_list(l: list) -> str:
    ''' input:  ["A", "B", "C"]
        output: "A、B、C"
    '''
    return '、'.join(l)


def clean_json(j: str) -> str:
    ''' convert full-width character to half-width one, such as "Ａ" to "A"
    '''
    j = unicodedata.normalize('NFKC', j)
    j = remove_unicode_blank(j)
    return j

# utils ===================================================================


if __name__ == '__main__':
    filename = 'job_data_fomatter'
    print(f'"{filename}" is ready.')
    
    job_data_formatter = JobDataFormatter()
    records = job_data_formatter.process()
    if records:
        print(records[0])
    
    