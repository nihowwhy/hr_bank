import sys
sys.path.append('..')

import re
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from datetime import datetime
import pandas as pd
from sqlalchemy.exc import IntegrityError

from model.model import db_connect, create_table, TJobPrim, TRawJobDesc, TRawCompDesc, TJobDesc, TJobAnalysis


from time import sleep


db_folder = 'db'
db_name = 'test_db.db'
DB_CONNECTION_STRING = f'sqlite:///{db_folder}/{db_name}'


ANALYSIS_TYPE_LIST = ['sex', 'edu', 'yearRange', 'exp', 'language', 'major', 'skill', 'cert']

class JobDataPreprocessor:
    
    def __init__(self):
        engine = db_connect(DB_CONNECTION_STRING)
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        
    
    def process(self):
        session = self.Session(expire_on_commit=False)
        
        raw_jobs = session.query(TRawJobDesc).all()
        
        for raw_job in raw_jobs:
            crawl_date = raw_job.crawl_date
            job_no = raw_job.job_no
            
            crawled_search_job_json = raw_job.search_job_json
            crawled_search_job_dict = SearchJobJsonProcessor(crawled_search_job_json).process()
            
            crawled_job_desc_json = raw_job.job_desc_json
            crawled_job_desc_dict = JobDescJsonProcessor(crawled_job_desc_json).process()
            
            crawled_job_analysis_json = raw_job.job_analysis_json
            crawled_job_analysis_dict = JobAnalysisJsonProcessor(crawled_job_analysis_json).process()
            
            job_desc_dict, job_analysis_dict = self._format_crawled_data_to_table_column(
                crawl_date, 
                job_no, 
                crawled_search_job_dict, 
                crawled_job_desc_dict, 
                crawled_job_analysis_dict
            )
            
            print(f'{crawl_date}  {job_no}')
            
            try:
                '''Upsert formatted data.'''
                job_desc = TJobDesc(**job_desc_dict)
                job_analysis = TJobAnalysis(**job_analysis_dict)
                continue
                session.add_all([job_desc, job_analysis])
                
#                 crawled_search_job_dict.clear()
#                 crawled_job_desc_dict.clear()
#                 crawled_job_analysis_dict.clear()
#                 job_desc_dict.clear()
#                 job_analysis_dict.clear()
#                 session.commit()
                
            except IntegrityError:
                print(f'>>> JOB_NO: "{job_no}" duplicated.')
                session.rollback()
                
            except Exception as e:
                print('wrong!!!')
                print(e)
                print()
                session.rollback()
#                 raise
                
            else:
                '''Delete raw data.'''
                print('delete raw data')
                session.delete(raw_job)
                session.commit()
                
            finally:
                session.expunge_all()
        print('session close...done')
        session.close()
                
                
    
    @staticmethod
    def _format_crawled_data_to_table_column(
            crawl_date, 
            job_no, 
            crawled_search_job_dict, 
            crawled_job_desc_dict, 
            crawled_job_analysis_dict):
        job_desc_dict = {}
        job_analysis_dict = {}
        
        job_desc_dict['job_no'] = crawled_search_job_dict['job_no']
        job_desc_dict['job_id'] = crawled_search_job_dict['job_id']
        job_desc_dict['job_name'] = crawled_search_job_dict['job_name']
        job_desc_dict['job_link'] = crawled_search_job_dict['job_link']
        job_desc_dict['job_type'] = crawled_search_job_dict['job_type']
        job_desc_dict['job_role'] = crawled_search_job_dict['job_role']
        job_desc_dict['job_cat'] = crawled_job_desc_dict['job_cat']
        job_desc_dict['apply_count'] = crawled_search_job_dict['apply_count']
        job_desc_dict['need_count'] = crawled_job_desc_dict['need_count']
        job_desc_dict['salary_min'] = crawled_search_job_dict['salary_min']
        job_desc_dict['salary_max'] = crawled_search_job_dict['salary_max']
        job_desc_dict['salary_desc'] = crawled_search_job_dict['salary_desc']
        job_desc_dict['salary_type'] = crawled_search_job_dict['salary_type']
        job_desc_dict['accept_role'] = crawled_job_desc_dict['accept_role']
        job_desc_dict['disaccept_role'] = crawled_job_desc_dict['disaccept_role']
        job_desc_dict['edu'] = crawled_search_job_dict['edu']
        job_desc_dict['work_exp'] = crawled_search_job_dict['work_exp']
        job_desc_dict['major'] = crawled_job_desc_dict['major']
        job_desc_dict['lang'] = crawled_job_desc_dict['lang']
        job_desc_dict['local_lang'] = crawled_job_desc_dict['local_lang']
        job_desc_dict['speciality'] = crawled_job_desc_dict['speciality']
        job_desc_dict['skill'] = crawled_job_desc_dict['skill']
        job_desc_dict['cert'] = crawled_job_desc_dict['cert']
        job_desc_dict['driver_license'] = crawled_job_desc_dict['driver_license']
        job_desc_dict['other'] = crawled_job_desc_dict['other']
        job_desc_dict['job_desc'] = crawled_search_job_dict['job_desc']
        job_desc_dict['job_tag'] = crawled_search_job_dict['job_tag']
        job_desc_dict['manage_resp'] = crawled_job_desc_dict['manage_resp']
        job_desc_dict['business_trip'] = crawled_job_desc_dict['business_trip']
        job_desc_dict['work_period'] = crawled_job_desc_dict['work_period']
        job_desc_dict['vacation_policy'] = crawled_job_desc_dict['vacation_policy']
        job_desc_dict['start_work_day'] = crawled_job_desc_dict['start_work_day']
        job_desc_dict['hire_type'] = crawled_job_desc_dict['hire_type']
        job_desc_dict['delegate_recruit'] = crawled_job_desc_dict['delegate_recruit']
        job_desc_dict['job_addr_dist'] = crawled_search_job_dict['job_addr_dist']
        job_desc_dict['landmark_tag'] = crawled_search_job_dict['landmark_tag']
        job_desc_dict['lon'] = crawled_search_job_dict['lon']
        job_desc_dict['lat'] = crawled_search_job_dict['lat']
        job_desc_dict['appear_date'] = crawled_search_job_dict['appear_date']
        
        job_analysis_dict['crawl_date'] = crawl_date
        job_analysis_dict['job_no'] = job_no
        job_analysis_dict['total_count'] = crawled_job_analysis_dict['total_count']
        job_analysis_dict['sex'] = crawled_job_analysis_dict['sex']
        job_analysis_dict['edu'] = crawled_job_analysis_dict['edu']
        job_analysis_dict['year_range'] = crawled_job_analysis_dict['year_range']
        job_analysis_dict['work_exp'] = crawled_job_analysis_dict['work_exp']
        job_analysis_dict['lang'] = crawled_job_analysis_dict['lang']
        job_analysis_dict['major'] = crawled_job_analysis_dict['major']
        job_analysis_dict['skill'] = crawled_job_analysis_dict['skill']
        job_analysis_dict['cert'] = crawled_job_analysis_dict['cert']
        job_analysis_dict['update_date'] = crawled_job_analysis_dict['update_date']
        print('_format_crawled_data_to_table_column...done')
        return job_desc_dict, job_analysis_dict
    
    
class SearchJobJsonProcessor:
    
    def __init__(self, search_job_json: str):
        self.d = json.loads(search_job_json)
        
        
    def process(self):        
        d = self.d
        search_job_dict = {}
        
        job_link = 'https:' + d['link']['job'] if 'job' in d['link'].keys() else ''
        search_job_dict['job_type'] = d['jobType'] # code
        search_job_dict['job_no'] = d['jobNo']
        search_job_dict['job_name'] = d['jobName']
        search_job_dict['job_role'] = d['jobRole'] # code
        search_job_dict['job_addr_dist'] = d['jobAddrNoDesc']
        search_job_dict['job_desc'] = d['description']
        search_job_dict['edu'] = d['optionEdu']
        search_job_dict['work_exp'] = d['period'] # int
        search_job_dict['salary_min'] = d['salaryLow'] # int
        search_job_dict['salary_max'] = d['salaryHigh'] # int
        search_job_dict['salary_desc'] = d['salaryDesc']
        search_job_dict['salary_type'] = d['s10'] # code 10:面議 20:論件計酬 30:時薪 50:月薪
        search_job_dict['appear_date'] = d['appearDate'] # int
        search_job_dict['job_tag'] = '、'.join(d['tags'])
        search_job_dict['landmark_tag'] = d['landmark']
        search_job_dict['job_link'] = job_link
        search_job_dict['job_id'] = _get_job_id_from_link(job_link)
        search_job_dict['lon'] = d['lon'][:11]
        search_job_dict['lat'] = d['lat'][:11]
        search_job_dict['apply_count'] = int(d['applyCnt'])
        
        return search_job_dict
    
    
class JobDescJsonProcessor:
    
    def __init__(self, job_desc_json: str):
        self.d = json.loads(job_desc_json)
        
        
    def process(self):
        d = self.d
        job_desc_dict = {}
        
        job_desc_dict['accept_role'] = _get_accept_role_string(d)
        job_desc_dict['disaccept_role'] = _get_disaccept_role_string(d)
        job_desc_dict['major'] = _get_major_string(d)
        job_desc_dict['lang'] = _get_language_string(d)
        job_desc_dict['local_lang'] = _get_local_language_string(d)
        job_desc_dict['speciality'] = _get_specialty_string(d)
        job_desc_dict['skill'] = _get_skill_string(d)
        job_desc_dict['cert'] = _get_certificate_string(d)
        job_desc_dict['driver_license'] = _get_driver_license_string(d)
        job_desc_dict['other'] = _get_other_string(d)
        job_desc_dict['job_cat'] = _get_job_category_string(d)
        job_desc_dict['manage_resp'] = _get_manage_resp_string(d)
        job_desc_dict['business_trip'] = _get_business_trip_string(d)
        job_desc_dict['work_period'] = _get_work_period_string(d)
        job_desc_dict['vacation_policy'] = _get_vacation_policy_string(d)
        job_desc_dict['start_work_day'] = _get_start_working_day_string(d)
        job_desc_dict['hire_type'] = _get_hire_type_string(d)
        job_desc_dict['delegate_recruit'] = _get_delegate_recruit_string(d)
        job_desc_dict['need_count'] = _get_need_emp_string(d)
        
        return job_desc_dict
        
        
class JobAnalysisJsonProcessor:
    def __init__(self, job_analysis_json: str):
        self.d = json.loads(job_analysis_json)
        
    
    def process(self):
        d = self.d
        job_analysis_dict = {}
        
        job_analysis_dict['total_count'] = _get_analysis_total(d)
        job_analysis_dict['update_date'] = _get_update_date(d)
        job_analysis_dict['sex'] = _get_analysis_json_by_type_name(d, 'sex')
        job_analysis_dict['edu'] = _get_analysis_json_by_type_name(d, 'edu')
        job_analysis_dict['year_range'] = _get_analysis_json_by_type_name(d, 'yearRange')
        job_analysis_dict['work_exp'] = _get_analysis_json_by_type_name(d, 'exp')
        job_analysis_dict['lang'] = _get_analysis_json_by_type_name(d, 'language')
        job_analysis_dict['major'] = _get_analysis_json_by_type_name(d, 'major')
        job_analysis_dict['skill'] = _get_analysis_json_by_type_name(d, 'skill')
        job_analysis_dict['cert'] = _get_analysis_json_by_type_name(d, 'cert')
        
        return job_analysis_dict
        
        
        
# search job
def _get_job_id_from_link(link):
    try:
        return re.search('job\/(.*)\?', link).group(1)
    except:
        print(f'There is no JOB_ID. (link: {link})')
        return None
    
    
# utils
def join_dict_item_in_list(l: list, key: str):
    dict_item_list = [d[key] for d in l]
    return '、'.join(dict_item_list)


def join_list_element(l: list):
    return '、'.join(l)


# job desc
def _get_accept_role_string(d):
    l = d['data']['condition']['acceptRole']['role']
    return join_dict_item_in_list(l, 'description')


def _get_disaccept_role_string(d):
    l = d['data']['condition']['acceptRole']['disRole']['disability']
    return join_dict_item_in_list(l, 'type')


def _get_major_string(d):
    l = d['data']['condition']['major']
    return join_list_element(l)


def _get_language_string(d):
    l = d['data']['condition']['language']
    return join_dict_item_in_list(l, 'language')


def _get_local_language_string(d):
    l = d['data']['condition']['localLanguage']
    return join_dict_item_in_list(l, 'language')


def _get_specialty_string(d):
    l = d['data']['condition']['specialty']
    return join_dict_item_in_list(l, 'description')


def _get_skill_string(d):
    l = d['data']['condition']['skill']
    return join_dict_item_in_list(l, 'description')


def _get_certificate_string(d):
    l = d['data']['condition']['certificate']
    return join_list_element(l)


def _get_driver_license_string(d):
    l = d['data']['condition']['driverLicense']
    return join_list_element(l)


def _get_other_string(d):
    return d['data']['condition']['other']


def _get_job_category_string(d):
    l = d['data']['jobDetail']['jobCategory']
    return join_dict_item_in_list(l, 'description')


def _get_manage_resp_string(d):
    return d['data']['jobDetail']['manageResp']


def _get_business_trip_string(d):
    return d['data']['jobDetail']['businessTrip']


def _get_work_period_string(d):
    return d['data']['jobDetail']['workPeriod']


def _get_vacation_policy_string(d):
    return d['data']['jobDetail']['vacationPolicy']


def _get_start_working_day_string(d):
    return d['data']['jobDetail']['startWorkingDay']


def _get_hire_type_string(d):
    ''' code
    0: 公司自聘
    1: 代徵
    '''
    return str(d['data']['jobDetail']['hireType'])


def _get_delegate_recruit_string(d):
    return d['data']['jobDetail']['delegatedRecruit']


def _get_need_emp_string(d):
    return d['data']['jobDetail']['needEmp']


# job analysis
def _convert_analysis_dict_to_format_json(raw_analysis_dict):
    stat_dict = {key: raw_analysis_dict[key] for key in raw_analysis_dict.keys() if key.isdigit()}
    stat_json = json.dumps(stat_dict, ensure_ascii=False)
    stat_df = pd.read_json(stat_json).T
    format_json = stat_df.to_json(force_ascii=False)
    return format_json


def _get_analysis_json_by_type_name(raw_dict, key):
    raw_analysis_dict = raw_dict[key]
    analysis_json = _convert_analysis_dict_to_format_json(raw_analysis_dict)
    return analysis_json


def _get_analysis_total(raw_dict):
    ''' TODO: use DFS to find first 'total' value. Same thing for "_get_update_date"
    '''
    for type_name in ANALYSIS_TYPE_LIST:
        if 'total' in raw_dict[type_name].keys():
            total = raw_dict[type_name]['total']
            return int(total)
    return -1
    

def _get_update_date(raw_dict):
    for type_name in ANALYSIS_TYPE_LIST:
        if 'update_time' in raw_dict[type_name].keys():
            update_time_string = raw_dict[type_name]['update_time']
            update_date = datetime.strptime(update_time_string, '%Y-%m-%d %H:%M:%S')
            update_date = int(update_date.strftime('%Y%m%d'))
            return update_date
    return -1


if __name__ == '__main__':
    print('start')
    JobDataPreprocessor().process()
    print('end')