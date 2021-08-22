# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import sys
sys.path.append('..')

# useful for handling different item types with a single interface
import re
import json
# from itemadapter import ItemAdapter
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from scrapy.utils.project import get_project_settings

from model.model import db_connect, create_table, TJob, TJobAnalysis, TCompany

SETTINGS = get_project_settings()
DB_CONNECTION_STRING = SETTINGS.get('DB_CONNECTION_STRING')
TODAY_DATE = int(datetime.now().strftime('%Y%m%d'))


# Database Pipeline
class HrBankCrawlerPipeline:

    def __init__(self):
        ''' Initialize database connection and sessionmaker
        Creates tables
        '''
        print('===============')
        print(f'>>> Create DB')
        print(f'>>> Connection String: {DB_CONNECTION_STRING}')
        print('===============')

        # config from scrapy settings
        engine = db_connect(DB_CONNECTION_STRING)
        create_table(engine)
        self.Session = sessionmaker(bind=engine)


    def process_item(self, item, spider):
        session = self.Session()

        # parse item
        crawl_date = TODAY_DATE
        parsed_item = self.parse_item(item)
        job_no = parsed_item['job_no']
        job_id = parsed_item['job_id']
        update_date = parsed_item.get('update_date', crawl_date) # job analysis table column
        company_no = parsed_item['company_no']
        company_id = parsed_item['company_id']

        # check if data crawled
        try:
            t_job = session.query(TJob).filter_by(job_no=job_no, job_id=job_id, crawl_date=crawl_date).first()
            is_already_crawl_job = bool(t_job)

            t_job_analysis = session.query(TJobAnalysis).filter_by(job_no=job_no, job_id=job_id, update_date=update_date).first()
            is_already_crawl_job_analysis = bool(t_job_analysis)

            t_company = session.query(TCompany).filter_by(company_no=company_no, company_id=company_id, crawl_date=crawl_date).first()
            is_already_crawl_company = bool(t_company)
        except Exception as e:
            print(e)
        finally:
            session.close()

        # If latest data not exist in database, then upsert data into database.
        if not is_already_crawl_job:
            self.upsert_data_to_t_job(parsed_item)

        if not is_already_crawl_job_analysis:
            self.upsert_data_to_t_job_analysis(parsed_item)

        if not is_already_crawl_company:
            self.upsert_data_to_t_company(parsed_item)

        return


    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        stats = json.dumps(stats, indent=2, default=str)
        print('[Close Spider]')
        # print(f'Stats:\n{stats}')


    def upsert_data_to_t_job(self, parsed_item):
        session = self.Session()

        crawl_date = TODAY_DATE
        job_no = parsed_item['job_no']
        job_id = parsed_item['job_id']

        # get table object
        t_job = session.query(TJob).filter_by(job_no=job_no, job_id=job_id).first()

        # set values to job table object
        try:
            is_job_exist = bool(t_job)
            if is_job_exist == False:
                t_job = TJob()
                t_job.job_id = job_id
                t_job.job_no = job_no
                t_job.first_crawl_date = crawl_date
            t_job.job_name = parsed_item['job_name']
            t_job.job_cat = parsed_item['job_cat']
            t_job.job_cat_desc = parsed_item['job_cat_desc']
            t_job.company_name = parsed_item['company_name']
            t_job.company_id = parsed_item['company_id']
            t_job.company_no = parsed_item['company_no']
            t_job.need_count_desc = parsed_item['need_count_desc']
            t_job.apply_count = parsed_item['apply_count']
            t_job.salary_min = parsed_item['salary_min']
            t_job.salary_max = parsed_item['salary_max']
            t_job.salary_desc = parsed_item['salary_desc']
            t_job.salary_type = parsed_item['salary_type']
            t_job.job_desc = parsed_item['job_desc']
            t_job.job_type = parsed_item['job_type']
            t_job.job_role = parsed_item['job_role']
            t_job.edu = parsed_item['edu']
            t_job.work_exp = parsed_item['work_exp']
            t_job.skill = parsed_item['skill']
            t_job.specialty = parsed_item['specialty']
            t_job.major = parsed_item['major']
            t_job.lang = parsed_item['lang']
            t_job.local_lang = parsed_item['local_lang']
            t_job.cert = parsed_item['cert']
            t_job.driver_license = parsed_item['driver_license']
            t_job.other = parsed_item['other']
            t_job.accept_role = parsed_item['accept_role']
            t_job.disaccept_role = parsed_item['disaccept_role']
            t_job.manage_resp = parsed_item['manage_resp']
            t_job.business_trip = parsed_item['business_trip']
            t_job.work_period = parsed_item['work_period']
            t_job.vacation_policy = parsed_item['vacation_policy']
            t_job.start_work_day = parsed_item['start_work_day']
            t_job.job_addr_dist = parsed_item['job_addr_dist']
            t_job.job_addr = parsed_item['job_addr']
            t_job.lon = parsed_item['lon']
            t_job.lat = parsed_item['lat']
            t_job.appear_date = parsed_item['appear_date']
            t_job.crawl_date = crawl_date

            if is_job_exist == False:
                session.add(t_job)
            session.commit()

        except Exception as e:
            print(e)
            session.rollback()

        finally:
            session.close()
            return


    def upsert_data_to_t_job_analysis(self, parsed_item):
        session = self.Session()

        crawl_date = TODAY_DATE
        job_no = parsed_item['job_no']
        job_id = parsed_item['job_id']

        # get table object
        t_job_analysis = session.query(TJobAnalysis).filter_by(job_no=job_no, job_id=job_id, crawl_date=crawl_date).first()

        # set values to job analysis table object
        try:
            is_job_analysis_exist = bool(t_job_analysis)
            if is_job_analysis_exist == False:
                t_job_analysis = TJobAnalysis()
                t_job_analysis.job_id = job_id
                t_job_analysis.job_no = job_no
                t_job_analysis.crawl_date = crawl_date
            t_job_analysis.update_date = parsed_item['update_date']
            t_job_analysis.job_name = parsed_item['job_name']
            t_job_analysis.apply_count = parsed_item['apply_count']
            t_job_analysis.sex_json = parsed_item['sex_json']
            t_job_analysis.edu_json = parsed_item['edu_json']
            t_job_analysis.age_json = parsed_item['age_json']
            t_job_analysis.work_exp_json = parsed_item['work_exp_json']
            t_job_analysis.lang_json = parsed_item['lang_json']
            t_job_analysis.major_json = parsed_item['major_json']
            t_job_analysis.skill_json = parsed_item['skill_json']
            t_job_analysis.cert_json = parsed_item['cert_json']

            if is_job_analysis_exist == False:
                session.add(t_job_analysis)
            session.commit()

        except Exception as e:
            print(e)
            session.rollback()

        finally:
            session.close()
            return


    def upsert_data_to_t_company(self, parsed_item):
        session = self.Session()

        crawl_date = TODAY_DATE
        company_no = parsed_item['company_no']
        company_id = parsed_item['company_id']

        # get table object
        t_company = session.query(TCompany).filter_by(company_no=company_no, company_id=company_id).first()

        # set values to company table object
        try:
            is_company_exist = bool(t_company)
            if is_company_exist == False:
                t_company = TCompany()
                t_company.company_id = company_id
                t_company.company_no = company_no

            t_company.company_name = parsed_item['company_name']
            t_company.industry_no = parsed_item['industry_no']
            t_company.industry_desc = parsed_item['industry_desc']
            t_company.industry_cat = parsed_item['industry_cat']
            t_company.emp_count_desc = parsed_item['emp_count_desc']
            t_company.capital = parsed_item['capital']
            t_company.profile = parsed_item['profile']
            t_company.product = parsed_item['product']
            t_company.management = parsed_item['management']
            t_company.welfare = parsed_item['welfare']
            t_company.welfare_tag = parsed_item['welfare_tag']
            t_company.legal_tag = parsed_item['legal_tag']
            t_company.company_addr = parsed_item['company_addr']
            t_company.crawl_date = crawl_date

            if is_company_exist == False:
                session.add(t_company)
            session.commit()

        except Exception as e:
            print(e)
            session.rollback()

        finally:
            session.close()
            return


    @staticmethod
    def parse_item(item):
        parsed_item = {}

        # Search Page
        try:
            # 職缺ID
            parsed_item['job_id'] = re.search('job\/(.*)\?', item['search_page']['link']['job']).group(1)

            # 職缺編號
            parsed_item['job_no'] = item['search_page']['jobNo']

            # 職缺名稱
            parsed_item['job_name'] = item['search_page']['jobName']

            # 公司ID
            parsed_item['company_id'] = re.search('company/(.*)\?', item['search_page']['link']['cust']).group(1)

            # 公司名稱
            parsed_item['company_name'] = item['search_page']['custName']

            # 公司編號
            parsed_item['company_no'] = item['search_page']['custNo']

            # 應徵人數
            parsed_item['apply_count'] = int(item['search_page']['applyCnt'])

            # 最低薪資
            parsed_item['salary_min'] = int(item['search_page']['salaryLow'])

            # 最高薪資
            parsed_item['salary_max'] = int(item['search_page']['salaryHigh'])

            # 薪資描述
            parsed_item['salary_desc'] = item['search_page']['salaryDesc']

            # 薪資類型code
            parsed_item['salary_type'] = item['search_page']['s10']

            # 職缺說明
            parsed_item['job_desc'] = item['search_page']['description']

            # 職缺類別
            parsed_item['job_type'] = item['search_page']['jobType']

            # 工作類型code
            parsed_item['job_role'] = item['search_page']['jobRole']

            # 學歷要求
            parsed_item['edu'] = item['search_page']['optionEdu']

            # 經驗要求
            parsed_item['work_exp'] = int(item['search_page']['period'])

            # 工作縣市
            parsed_item['job_addr_dist'] = item['search_page']['jobAddrNoDesc']

            # 工作地點
            parsed_item['job_addr'] = item['search_page']['jobAddrNoDesc'] + item['search_page']['jobAddress']

            # 經度
            parsed_item['lon'] = item['search_page']['lon']

            # 緯度
            parsed_item['lat'] = item['search_page']['lat']

            # 出現日期
            parsed_item['appear_date'] = int(item['search_page']['appearDate'])
        except Exception as e:
            print(e)

        # Job Page
        try:
            # 工作類型
            parsed_item['job_cat'] = join_list_of_dict_item(item['job_page']['data']['jobDetail']['jobCategory'], 'code')

            # 工作類型
            parsed_item['job_cat_desc'] = join_list_of_dict_item(item['job_page']['data']['jobDetail']['jobCategory'], 'description')

            # 需求人數描述 
            parsed_item['need_count_desc'] = item['job_page']['data']['jobDetail']['needEmp']

            # 技能要求
            parsed_item['skill'] = join_list_of_dict_item(item['job_page']['data']['condition']['skill'], 'description')

            # 專長要求
            parsed_item['specialty'] = join_list_of_dict_item(item['job_page']['data']['condition']['specialty'], 'description')

            # 科系要求
            parsed_item['major'] = join_list_of_element(item['job_page']['data']['condition']['major'])

            # 語言要求
            parsed_item['lang'] = get_language_requirement(item['job_page']['data']['condition']['language'])

            # 地方語言要求
            parsed_item['local_lang'] = get_language_requirement(item['job_page']['data']['condition']['localLanguage'])

            # 證照要求
            parsed_item['cert'] = join_list_of_element(item['job_page']['data']['condition']['certificate'])

            # 駕照要求
            parsed_item['driver_license'] = join_list_of_element(item['job_page']['data']['condition']['driverLicense'])

            # 其他要求
            parsed_item['other'] = item['job_page']['data']['condition']['other']

            # 接受身份
            parsed_item['accept_role'] = join_list_of_dict_item(item['job_page']['data']['condition']['acceptRole']['role'], 'description')

            # 婉拒身份
            parsed_item['disaccept_role'] = join_list_of_dict_item(item['job_page']['data']['condition']['acceptRole']['disRole']['disability'], 'type')

            # 管理責任
            parsed_item['manage_resp'] = item['job_page']['data']['jobDetail']['manageResp']

            # 出差外派
            parsed_item['business_trip'] = item['job_page']['data']['jobDetail']['businessTrip']

            # 上班時段
            parsed_item['work_period'] = item['job_page']['data']['jobDetail']['workPeriod']

            # 休假制度
            parsed_item['vacation_policy'] = item['job_page']['data']['jobDetail']['vacationPolicy']

            # 可上班日
            parsed_item['start_work_day'] = item['job_page']['data']['jobDetail']['startWorkingDay']

            # 產業編號
            parsed_item['industry_no'] = item['job_page']['data']['industryNo']
        except Exception as e:
            print(e)

        # Job Analysis Page
        try:
            # 更新日期
            parsed_item['update_date'] = get_update_date(item['analysis_page']['sex']['update_time'])

            # 性別json
            parsed_item['sex_json'] = json.dumps(format_basic_analysis_dict(item['analysis_page']['sex']), ensure_ascii=False)

            # 學歷json
            parsed_item['edu_json'] = json.dumps(format_basic_analysis_dict(item['analysis_page']['edu']), ensure_ascii=False)

            # 年齡json
            parsed_item['age_json'] = json.dumps(format_basic_analysis_dict(item['analysis_page']['yearRange']), ensure_ascii=False)

            # 工作經驗json
            parsed_item['work_exp_json'] = json.dumps(format_basic_analysis_dict(item['analysis_page']['exp']), ensure_ascii=False)

            # 語言json
            parsed_item['lang_json'] = json.dumps(format_language_analysis_dict(item['analysis_page']['language']), ensure_ascii=False)

            # 科系json
            parsed_item['major_json'] = json.dumps(format_option_analysis_dict(item['analysis_page']['major'], 'major'), ensure_ascii=False)

            # 技能json
            parsed_item['skill_json'] = json.dumps(format_option_analysis_dict(item['analysis_page']['skill'], 'skill'), ensure_ascii=False)

            # 證照json
            parsed_item['cert_json'] = json.dumps(format_option_analysis_dict(item['analysis_page']['cert'], 'cert'), ensure_ascii=False)
        except Exception as e:
            print(e)

        # Company Page
        # If skip crawling company page, then return "parsed_item".
        if 'company_page' not in item.keys():
            return parsed_item
        try:
            # 產業描述
            parsed_item['industry_desc'] = item['company_page']['data']['industryDesc']

            # 產業類別
            parsed_item['industry_cat'] = item['company_page']['data']['indcat']

            # 員工人數
            parsed_item['emp_count_desc'] = item['company_page']['data']['empNo']

            # 資本額
            parsed_item['capital'] = item['company_page']['data']['capital']

            # 公司介紹
            parsed_item['profile'] = item['company_page']['data']['profile']

            # 主要商品
            parsed_item['product'] = item['company_page']['data']['product']

            # 經營理念
            parsed_item['management'] = item['company_page']['data']['management']

            # 福利介紹
            parsed_item['welfare'] = item['company_page']['data']['welfare']

            # 福利標籤
            parsed_item['welfare_tag'] = join_list_of_element(item['company_page']['data']['tagNames'])

            # 法定標籤
            parsed_item['legal_tag'] = join_list_of_element(item['company_page']['data']['legalTagNames'])

            # 公司縣市
            parsed_item['company_addr_dist'] = item['company_page']['data']['addrNoDesc']

            # 公司地點
            parsed_item['company_addr'] = item['company_page']['data']['address']
        except Exception as e:
            print(e)

        return parsed_item


def get_language_requirement(language_list):
    ''' If a language requirement is "精通", then add the language to the list.
    '''
    if len(language_list) == 0:
        return ''

    required_lang_list = []
    for lang in language_list:
        if '精通' in lang['ability']:
            required_lang_list.append(lang['language'])
    return join_list_of_element(required_lang_list)


def get_update_date(update_time_string):
    ''' From "2021-07-04 02:00:27" to 20210704
    '''
    update_date = ''.join(re.findall('\d+', update_time_string[:10]))
    return int(update_date)


def format_basic_analysis_dict(analysis_dict):
    ''' format sample: {0: {'男': 3}, 1: {'女': 4}}
    '''
    sequence_num = 0
    formatted_analysis_dict = {}
    for serial, record in analysis_dict.items():
        if not serial.isdigit():
            continue

        has_record_value = False
        for record_name, record_value in record.items():
            if 'Name' in record_name:
                record_name_desc = record_value
            elif 'count' in record_name:
                record_count = int(record_value)
                has_record_value = True
                formatted_analysis_dict[sequence_num] = {}

        if has_record_value:
            formatted_analysis_dict[sequence_num][record_name_desc] = record_count
            sequence_num += 1

    return formatted_analysis_dict


def format_language_analysis_dict(analysis_dict):
    ''' format sample: {0: {'中文': 2}}
    Only if level is up to "精通", then add the language to the dictionary.
    '''
    sequence_num = 0
    formatted_analysis_dict = {}
    for serial, record in analysis_dict.items():
        if not serial.isdigit():
            continue

        has_record_value = False
        for record_name, record_value in record.items():
            if 'Name' in record_name:
                record_name_desc = record_value
            elif 'count' in record_name:
                record_count = int(record_value)
            elif 'level' in record_name:
                if '精通' in str(record_value):
                    has_record_value = True
                    formatted_analysis_dict[sequence_num] = {}

        if has_record_value:
            formatted_analysis_dict[sequence_num][record_name_desc] = record_count
            sequence_num += 1

    return formatted_analysis_dict


def format_option_analysis_dict(analysis_dict, analysis_type):
    ''' format sample: {0: {'3018001000': 2, '普通科': 2}, 1: {'3006001000': 1, '一般商業學類': 1}}
    '''
    sequence_num = 0
    formatted_analysis_dict = {}
    for serial, record in analysis_dict.items():
        if not serial.isdigit():
            continue

        has_record_value = False
        for record_name, record_value in record.items():
            if analysis_type == record_name:
                record_name_no = record_value
            elif 'Name' in record_name:
                record_name_desc = record_value
            elif 'count' in record_name:
                record_count = int(record_value)
                has_record_value = True
                formatted_analysis_dict[sequence_num] = {}

        if has_record_value:
            formatted_analysis_dict[sequence_num][record_name_no] = record_count
            formatted_analysis_dict[sequence_num][record_name_desc] = record_count
            sequence_num += 1

    return formatted_analysis_dict


# utils ===========================================
def join_list_of_dict_item(l: list, key: str):
    ''' input:  l = [{"name": "Ian"}, {"name": "Wang"}]
                key = 'name'
        output: "Ian、Wang"
    '''
    dict_item_list = [d[key] for d in l]
    return '、'.join(dict_item_list)


def join_list_of_element(l: list) -> str:
    ''' input:  ["A", "B", "C"]
        output: "A、B、C"
    '''
    return '、'.join(l)
# =================================================


# Json File Pipeline
import os

DATA_FOLDER = SETTINGS.get('DATA_FOLDER')

class HrBankCrawlerJsonPipeline:

    def __init__(self):
        self.save_folder = DATA_FOLDER
        self.raw_data_folder = os.path.join(self.save_folder, 'raw_data')


    def process_item(self, item, spider):

        try:
            # key value
            job_id = re.search('job\/(.*)\?', item['search_page']['link']['job']).group(1)
            crawl_date = TODAY_DATE

            # filename
            filename = f'{crawl_date}_{job_id}.json'
            filepath = os.path.join(self.raw_data_folder, filename)
            is_file_exist = os.path.exists(filepath)

            # save json
            if not is_file_exist:
                with open(filepath, mode='w', encoding='utf-8') as f:
                    j = json.dumps(dict(item))
                    f.write(j)

        except Exception as e:
            print(e)

        finally:
            return