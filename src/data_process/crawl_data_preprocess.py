import sys
sys.path.append('.')
# sys.path.append('..')

import re
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, func
from datetime import datetime, timedelta

from model.model import db_connect, create_table, TJob, TJobAnalysis, TCompany, TDashboard
from config.config import DB_CONNECTION_STRING
from reference.hr_bank_code_mapping import MAPPING


TODAY_DATE = int(datetime.now().strftime('%Y%m%d'))


class CrawlDataProcessor:

    def __init__(self, **kwarg):

        # get the date which want to process data, if "process_date"=0, it means process all data.
        if 'process_all_date' in kwarg.keys():
            if kwarg['process_all_date'] == True:
                self.process_date = 0
        elif 'process_date' in kwarg.keys():
            self.process_date = int(kwarg['process_date'])
        else:
            self.process_date = TODAY_DATE

        # database connection
        self.db_connect()


    def db_connect(self):
        engine = db_connect(DB_CONNECTION_STRING)
        create_table(engine)
        self.Session = sessionmaker(bind=engine)


    def process(self):
        self.process_t_job()
        self.process_t_job_batch()
        self.process_t_company()
        self.process_t_dashboard()


    def process_t_job(self):
        # update job data according to "process_date"

        session = self.Session()

        # Filter process data by "process_date".
        if self.process_date:
            results = session.query(TJob).filter_by(crawl_date=self.process_date)
        else:
            results = session.query(TJob)

        # process job data
        for result in results:
            try:
                # 需求人數
                need_count_desc = result.need_count_desc
                need_count_max, need_count_min = get_need_count_max_and_min(need_count_desc)
                need_count = int((need_count_max + need_count_min) / 2)
                result.need_count_max = need_count_max
                result.need_count_min = need_count_min
                result.need_count = need_count

                # 薪資類型
                salary_type = result.salary_type
                result.salary_type_desc = convert_salary_type_code_to_desc(salary_type)

                # 估算薪水
                salary_max = result.salary_max
                salary_min = result.salary_min
                salary = convert_salary_to_estimated_monthly_salary(salary_min, salary_max, salary_type)
                result.salary = salary

                # 工作類型
                # todo
                job_role = result.job_role
                result.job_role_desc = convert_job_role_code_to_desc(job_role)

                # 工作地區
                job_addr_dist = result.job_addr_dist
                result.job_addr_area = convert_addr_to_area(job_addr_dist)

                # 開缺時間長度
                appear_date = result.appear_date
                first_crawl_date = result.first_crawl_date
                start_date_int = min(appear_date, first_crawl_date)
                end_date_int = result.crawl_date
                result.job_duration_day = calculate_duration_day(start_date_int, end_date_int)

                # 職缺分類
                # todo

            except Exception as e:
                print(e)

        session.commit()
        session.close()


    def process_t_job_batch(self):
        # update job exist information

        session = self.Session()

        max_crawl_date = session.query(func.max(TJob.crawl_date)).scalar()
        results = session.query(TJob)

        # process job data
        for result in results:
            try:
                # 結束時間、職缺存在
                crawl_date = result.crawl_date
                if crawl_date == max_crawl_date:
                    is_job_exist = 'Y'
                    close_date = None
                else:
                    is_job_exist = 'N'
                    close_date = crawl_date
                result.close_date = close_date
                result.is_job_exist = is_job_exist

            except Exception as e:
                print(e)

        session.commit()
        session.close()


    def process_t_company(self):
        session = self.Session()

        # Filter process data by "process_date".
        if self.process_date:
            results = session.query(TCompany).filter_by(crawl_date=self.process_date)
        else:
            results = session.query(TCompany)

        # process job data
        for result in results:
            try:
                # 公司地區
                company_addr = result.company_addr
                result.company_addr_area = convert_addr_to_area(company_addr)

                # 公司集團
                company_name = result.company_name
                result.company_group = convert_company_name_to_company_group(company_name)

            except Exception as e:
                print(e)

        session.commit()
        session.close()


    def process_t_dashboard(self):

        session = self.Session()

        # Filter process data by "process_date".
        if self.process_date:
            max_update_date = session.query(func.max(TJobAnalysis.update_date)).scalar()
            min_update_date = self.process_date
        else:
            max_update_date = session.query(func.max(TJobAnalysis.update_date)).scalar()
            min_update_date = session.query(func.min(TJobAnalysis.update_date)).scalar()
            print(f'Date Range: {min_update_date} ~ {max_update_date}')

        # get start window date
        start_window_date = get_last_monday_date(min_update_date)
        # start_window_date = timedelta_date_int(max_update_date, days=-30) # default: last 30 days

        # get end window date
        end_window_date = timedelta_date_int(start_window_date, days=6)

        # get weeks between start-window-date and max-update-date
        weeks = calculate_weeks_between_two_date(convert_int_to_date(start_window_date), convert_int_to_date(max_update_date))

        # query "job_id" in job analysis, which "update_date" is larger than "start_window_date".
        results = session.query(TJobAnalysis).filter(TJobAnalysis.update_date >= start_window_date).all()
        select_job_ids = [result.job_id for result in results]

        # loop every week within date range
        for _ in range(weeks + 1):

            print(f'Process Date: {start_window_date} ~ {end_window_date}')

            for select_job_id in select_job_ids:

                # query job analysis date between "start_window_date" and "end_window_date"
                result = session.query(
                            TJobAnalysis, TJob
                        ).filter(
                            (TJobAnalysis.job_id == select_job_id) & (TJob.job_id == select_job_id)
                        ).filter(
                            (TJobAnalysis.update_date >= start_window_date) & (TJobAnalysis.update_date <= end_window_date)
                        ).filter(
                            TJobAnalysis.job_id == TJob.job_id # resolve cartesian product problem
                        ).first()

                if result is None:
                    continue

                job_no = result.TJobAnalysis.job_no
                job_id = result.TJobAnalysis.job_id
                represent_date = start_window_date

                # get table object
                t_dashboard_session = self.Session()
                t_dashboard = t_dashboard_session.query(TDashboard).filter_by(job_no=job_no, job_id=job_id, represent_date=represent_date).first()

                # upsert data
                is_data_exist = bool(t_dashboard)
                try:
                    if is_data_exist == False:
                        t_dashboard = TDashboard()
                        t_dashboard.job_no = job_no
                        t_dashboard.job_id = job_id
                        t_dashboard.represent_date = represent_date

                    # represent date range
                    t_dashboard.represent_date_min = start_window_date
                    t_dashboard.represent_date_max = end_window_date

                    # job, company
                    t_dashboard.job_name = result.TJobAnalysis.job_name
                    t_dashboard.company_id = result.TJob.company_id
                    t_dashboard.company_no = result.TJob.company_no
                    t_dashboard.company_name = result.TJob.company_name

                    # salary, need_count, apply_count
                    t_dashboard.salary = result.TJob.salary
                    t_dashboard.need_count = result.TJob.need_count
                    t_dashboard.apply_count = result.TJob.apply_count

                    # sex
                    t_dashboard.sex_male = get_count_from_json('男', result.TJobAnalysis.sex_json)
                    t_dashboard.sex_female = get_count_from_json('女', result.TJobAnalysis.sex_json)

                    # education
                    t_dashboard.edu_junior = get_count_from_json('國中(含)以下', result.TJobAnalysis.edu_json)
                    t_dashboard.edu_senior = get_count_from_json('高中職', result.TJobAnalysis.edu_json) + get_count_from_json('專科', result.TJobAnalysis.edu_json)
                    t_dashboard.edu_undergrad = get_count_from_json('大學', result.TJobAnalysis.edu_json)
                    t_dashboard.edu_grad = get_count_from_json('博碩士', result.TJobAnalysis.edu_json)

                    # age
                    t_dashboard.age_00_20 = get_count_from_json('20歲以下', result.TJobAnalysis.age_json)
                    t_dashboard.age_21_25 = get_count_from_json('21~25歲', result.TJobAnalysis.age_json)
                    t_dashboard.age_26_30 = get_count_from_json('26~30歲', result.TJobAnalysis.age_json)
                    t_dashboard.age_31_35 = get_count_from_json('31~35歲', result.TJobAnalysis.age_json)
                    t_dashboard.age_36_40 = get_count_from_json('36~40歲', result.TJobAnalysis.age_json)
                    t_dashboard.age_41_45 = get_count_from_json('41~45歲', result.TJobAnalysis.age_json)
                    t_dashboard.age_46_50 = get_count_from_json('46~50歲', result.TJobAnalysis.age_json)
                    t_dashboard.age_51_55 = get_count_from_json('51~55歲', result.TJobAnalysis.age_json)
                    t_dashboard.age_56_60 = get_count_from_json('56~60歲', result.TJobAnalysis.age_json)
                    t_dashboard.age_60_99 = get_count_from_json('60歲以上', result.TJobAnalysis.age_json)

                    # work experience
                    t_dashboard.work_exp_0 = get_count_from_json('無工作經驗', result.TJobAnalysis.work_exp_json)
                    t_dashboard.work_exp_00_01 = get_count_from_json('1年以下', result.TJobAnalysis.work_exp_json)
                    t_dashboard.work_exp_01_03 = get_count_from_json('1~3年 ', result.TJobAnalysis.work_exp_json)
                    t_dashboard.work_exp_03_05 = get_count_from_json('3~5年', result.TJobAnalysis.work_exp_json)
                    t_dashboard.work_exp_05_10 = get_count_from_json('5~10年', result.TJobAnalysis.work_exp_json)
                    t_dashboard.work_exp_10_15 = get_count_from_json('10~15年', result.TJobAnalysis.work_exp_json)
                    t_dashboard.work_exp_15_20 = get_count_from_json('15~20年', result.TJobAnalysis.work_exp_json)
                    t_dashboard.work_exp_20_25 = get_count_from_json('20~25年', result.TJobAnalysis.work_exp_json)
                    t_dashboard.work_exp_25_99 = get_count_from_json('25年以上', result.TJobAnalysis.work_exp_json)

                    # major
                    t_dashboard.major_info_mgmt = get_count_from_json('資訊管理相關', result.TJobAnalysis.major_json)
                    t_dashboard.major_cs = get_count_from_json('資訊工程相關', result.TJobAnalysis.major_json)
                    t_dashboard.major_stat = get_count_from_json('統計學相關', result.TJobAnalysis.major_json)
                    t_dashboard.major_math_stat = get_count_from_json('數理統計相關', result.TJobAnalysis.major_json)

                    # skill
                    t_dashboard.skill_java = get_count_from_json('Java', result.TJobAnalysis.skill_json)
                    t_dashboard.skill_python = get_count_from_json('Python', result.TJobAnalysis.skill_json)

                    # language
                    t_dashboard.lang_eng = get_count_from_json('英文', result.TJobAnalysis.lang_json)
                    t_dashboard.lang_japan = get_count_from_json('日文', result.TJobAnalysis.lang_json)
                    t_dashboard.lang_korean = get_count_from_json('韓文', result.TJobAnalysis.lang_json)

                    # time info
                    t_dashboard.crawl_date = result.TJobAnalysis.crawl_date
                    t_dashboard.update_date = result.TJobAnalysis.update_date

                    if is_data_exist == False:
                        t_dashboard_session.add(t_dashboard)
                    t_dashboard_session.commit()

                except Exception as e:
                    print(e)

                finally:
                    t_dashboard_session.close()

            # moving window dates by 7 days
            start_window_date = timedelta_date_int(start_window_date, days=7)
            end_window_date = timedelta_date_int(end_window_date, days=7)

        session.close()


# T_JOB =========================================
# 需求人數
def get_need_count_max_and_min(need_count_desc):
    need_count_min = 0
    need_count_max = 0

    need_count_list = re.findall('\d+', need_count_desc)
    if len(need_count_list) == 2: # n~m人 -> min: n, max: m
        need_count_min = int(need_count_list[0])
        need_count_max = int(need_count_list[1])

    elif len(need_count_list) == 1: # n人以上 -> min: n, max: n
        need_count_min = int(need_count_list[0])
        need_count_max = int(need_count_list[0])

    elif len(need_count_list) == 0: # 不限 -> min: 1, max: 1
        need_count_min = 1
        need_count_max = 1

    return need_count_max, need_count_min


# 薪資類型
def convert_salary_type_code_to_desc(salary_type):
    salary_type_mapping = MAPPING['salary_type_mapping']
    return salary_type_mapping.get(salary_type, salary_type)


# 估算月薪
def convert_salary_to_estimated_monthly_salary(salary_min, salary_max, salary_type):
    # https://www.mol.gov.tw/media/5760435/no57-%E6%B4%BB%E7%94%A8%E6%B3%95%E8%A6%8F-%E9%9B%87%E4%B8%BB%E6%8B%9B%E5%8B%9F%E5%93%A1%E5%B7%A5%E7%B6%93%E5%B8%B8%E6%80%A7%E8%96%AA%E8%B3%874-%E8%90%AC%E5%85%83%E4%BB%A5%E4%B8%8B-%E6%87%89%E5%85%AC%E9%96%8B%E6%8E%B2%E7%A4%BA%E6%88%96%E5%91%8A%E7%9F%A5%E8%96%AA%E8%B3%87%E7%AF%84%E5%9C%8D.pdf
    # https://web.ntpu.edu.tw/~stou/class/ntpu/Group7-Fall-2011.pdf

    # convert 面議、時薪、日薪、月薪、年薪 to estimated monthly salary
    if salary_type not in ['10', '30', '40', '50', '60']: # 面議、時薪、日薪、月薪、年薪
        return None

    # 面議
    if salary_type == '10':
        return 45000 # minimum negociation salary

    # 9999999 means above
    if salary_max == 9999999:
        salary_max = salary_min

    # If salary_max is larger than salary_min by 25%, then set 125% of salary_min as salary_max.
    if salary_max / salary_min > 1.25:
        salary_max = salary_min * 1.25

    # 時薪
    if salary_type == '30':
        salary = int((salary_max + salary_min) / 2 * 72) # 1週18小時，共4週 = 72小時(1個月)

    # 日薪
    if salary_type == '40':
        salary = int((salary_max + salary_min) / 2 * 12) # 1週3天，共4週 = 12天(1個月)

    # 月薪
    if salary_type == '50':
        salary = int((salary_max + salary_min) / 2)

    # 年薪
    if salary_type == '60':
        salary = int((salary_max + salary_min) / 2 / 12) # 12 months

    return salary


# 工作類型
def convert_job_role_code_to_desc(job_role):
    # todo
    job_role_mapping = MAPPING['job_role_mapping']
    return job_role_mapping.get(job_role, job_role)


# 工作地區
def convert_addr_to_area(addr):
    addr_area_mapping = MAPPING['addr_area_mapping']
    addr_mapping_text = addr[:2]
    if addr_mapping_text not in addr_area_mapping.keys():
        addr_mapping_text = '其他'
    return addr_area_mapping.get(addr_mapping_text, addr_mapping_text)


# 開缺時間長度
def calculate_duration_day(start_date_int: int, end_date_int: int) -> int:
    start_date = datetime.strptime(str(start_date_int), '%Y%m%d')
    end_date = datetime.strptime(str(end_date_int), '%Y%m%d')
    duration_day = (end_date - start_date).days + 1
    return duration_day
# ===============================================


# T_COMPANY =====================================
# 公司集團
def convert_company_name_to_company_group(company_name):
    company_group_mapping = MAPPING['company_group_mapping']
    return company_group_mapping.get(company_name, None)
# ===============================================


# T_DASHBOARD ===================================
def get_last_monday_date(date_int):
    date = convert_int_to_date(date_int)
    weekday = date.weekday()
    monday_date = date + timedelta(days=-weekday)
    monday_date_int = convert_date_to_int(monday_date)
    return monday_date_int


def convert_date_to_int(date):
    ''' From datetime.datetime(2021, 7, 19, 0, 0) to 20210719
    '''
    return int(date.strftime('%Y%m%d'))


def convert_int_to_date(date_int):
    ''' From 20210719 to datetime.datetime(2021, 7, 19, 0, 0)
    '''
    year = int(date_int / 10000)
    month = int(date_int / 100) % 100
    day = int(date_int) % 100
    return datetime(year=year, month=month, day=day)


def timedelta_date_int(date_int, **kwarg):
    ''' Using function "datetime.timedelta" to calculate new date by "days, weeks"
    timedelta_date_int(20210719, days=7) -> 20210726
    '''
    date = convert_int_to_date(date_int)
    new_date = date + timedelta(**kwarg)
    return convert_date_to_int(new_date)


def calculate_weeks_between_two_date(date1, date2):
    ''' Return 0 if both dates fall within one week, 1 if two dates fall on two consecutive weeks, etc.
    '''
    monday1 = date1 - timedelta(days=date1.weekday())
    monday2 = date2 - timedelta(days=date2.weekday())
    return int((monday2 - monday1).days / 7)


def get_count_from_json(key, json_string):
    data_dict = json.loads(json_string)
    for _, value_dict in data_dict.items():
        if key in value_dict.keys():
            return int(value_dict[key])
    return 0
# ===============================================


# Json Processor
import os
import pandas as pd

from config.config import LOG_FOLDER, DB_CONNECTION_STRING, DATA_FOLDER


class CrawlDataJsonProcessor:

    def __init__(self, **kwarg):

        # get the date which want to process data, if "process_date"=0, it means process all data.
        if 'process_all_date' in kwarg.keys():
            if kwarg['process_all_date'] == True:
                self.process_date = 0
        elif 'process_date' in kwarg.keys():
            self.process_date = int(kwarg['process_date'])
        else:
            self.process_date = TODAY_DATE

        # setting path
        self.data_folder = DATA_FOLDER
        self.raw_data_folder = os.path.join(DATA_FOLDER, 'raw_data')
        self.excel_data_folder = os.path.join(DATA_FOLDER, 'excel_data')


    def process(self):
        # filter json files
        self.raw_data_filepaths = self.get_raw_data_filepath_list()

        # convert json files to dataframe
        result_df = self.convert_json_data_to_dataframe()

        # save dataframe to excel
        output_filename = f'{self.process_date}_output.xlsx'
        output_path = os.path.join(self.excel_data_folder, output_filename)
        self.save_dataframe_to_excel(result_df, output_path)


    def get_raw_data_filepath_list(self):
        filenames = os.listdir(self.raw_data_folder)
        filepaths = []
        if self.process_date:
            for filename in filenames:
                if filename.split('_')[0] == str(self.process_date):
                    filepaths.append(os.path.join(self.raw_data_folder, filename))
        else:
            for filename in filenames:
                filepaths.append(os.path.join(self.raw_data_folder, filename))
        return filepaths


    def convert_json_data_to_dataframe(self):
        result_df = pd.DataFrame()

        for filepath in self.raw_data_filepaths:
            # read data
            with open(filepath, 'r') as f:
                j = f.read()
                item = json.loads(j)

            # parse json data
            parsed_item = self.parse_item(item)
            parsed_item = self.filter_result_dataframe_columns(parsed_item)
            item_df = pd.DataFrame([parsed_item], columns=parsed_item.keys())

            # add parsed data to dataframe
            if len(result_df) == 0:
                result_df = item_df
            result_df = result_df.append(item_df, ignore_index=True)

        print(f'>>> Total Jobs: {len(result_df)}')
        return result_df


    def filter_result_dataframe_columns(self, item):
        # remove analysis raw json
        item.pop('sex_json', None)
        item.pop('edu_json', None)
        item.pop('age_json', None)
        item.pop('work_exp_json', None)
        item.pop('lang_json', None)
        item.pop('major_json', None)
        item.pop('skill_json', None)
        item.pop('cert_json', None)

        return item


    @staticmethod
    def save_dataframe_to_excel(output_df, output_path):
        with pd.ExcelWriter(output_path, options={'strings_to_urls': False}) as writer:
            output_df.to_excel(writer, index=False, encoding='utf8')


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

            # 薪資類型desc (derived)
            salary_type = parsed_item['salary_type']
            parsed_item['salary_type_desc'] = convert_salary_type_code_to_desc(salary_type)

            # 估算薪水 (derived)
            salary_max = parsed_item['salary_max']
            salary_min = parsed_item['salary_min']
            salary = convert_salary_to_estimated_monthly_salary(salary_min, salary_max, salary_type)
            parsed_item['salary'] = salary

            # 職缺說明
            parsed_item['job_desc'] = item['search_page']['description']

            # 職缺類別
            parsed_item['job_type'] = item['search_page']['jobType']

            # 工作類型code
            parsed_item['job_role'] = item['search_page']['jobRole']

            # 工作類型 (derived)
            # todo
            job_role = parsed_item['job_role']
            parsed_item['job_role_desc'] = convert_job_role_code_to_desc(job_role)

            # 學歷要求
            parsed_item['edu'] = item['search_page']['optionEdu']

            # 經驗要求
            parsed_item['work_exp'] = int(item['search_page']['period'])

            # 工作縣市
            parsed_item['job_addr_dist'] = item['search_page']['jobAddrNoDesc']

            # 工作地點
            parsed_item['job_addr'] = item['search_page']['jobAddrNoDesc'] + item['search_page']['jobAddress']

            # 工作地區 (derived)
            job_addr_dist = parsed_item['job_addr_dist']
            parsed_item['job_addr_area'] = convert_addr_to_area(job_addr_dist)

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

            # 需求人數max, min, count (derived)
            need_count_desc = parsed_item['need_count_desc']
            need_count_max, need_count_min = get_need_count_max_and_min(need_count_desc)
            need_count = int((need_count_max + need_count_min) / 2)
            parsed_item['need_count_max'] = need_count_max
            parsed_item['need_count_min'] = need_count_min
            parsed_item['need_count'] = need_count

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

            # 職缺分類 (derived)
            # todo

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

            # sex
            parsed_item['sex_male'] = get_count_from_json('男', parsed_item['sex_json'])
            parsed_item['sex_female'] = get_count_from_json('女', parsed_item['sex_json'])

            # education
            parsed_item['edu_junior'] = get_count_from_json('國中(含)以下', parsed_item['edu_json'])
            parsed_item['edu_senior'] = get_count_from_json('高中職', parsed_item['edu_json']) + get_count_from_json('專科', parsed_item['edu_json'])
            parsed_item['edu_undergrad'] = get_count_from_json('大學', parsed_item['edu_json'])
            parsed_item['edu_grad'] = get_count_from_json('博碩士', parsed_item['edu_json'])

            # age
            parsed_item['age_00_20'] = get_count_from_json('20歲以下', parsed_item['age_json'])
            parsed_item['age_21_25'] = get_count_from_json('21~25歲', parsed_item['age_json'])
            parsed_item['age_26_30'] = get_count_from_json('26~30歲', parsed_item['age_json'])
            parsed_item['age_31_35'] = get_count_from_json('31~35歲', parsed_item['age_json'])
            parsed_item['age_36_40'] = get_count_from_json('36~40歲', parsed_item['age_json'])
            parsed_item['age_41_45'] = get_count_from_json('41~45歲', parsed_item['age_json'])
            parsed_item['age_46_50'] = get_count_from_json('46~50歲', parsed_item['age_json'])
            parsed_item['age_51_55'] = get_count_from_json('51~55歲', parsed_item['age_json'])
            parsed_item['age_56_60'] = get_count_from_json('56~60歲', parsed_item['age_json'])
            parsed_item['age_60_99'] = get_count_from_json('60歲以上', parsed_item['age_json'])

            # work experience
            parsed_item['work_exp_0'] = get_count_from_json('無工作經驗', parsed_item['work_exp_json'])
            parsed_item['work_exp_00_01'] = get_count_from_json('1年以下', parsed_item['work_exp_json'])
            parsed_item['work_exp_01_03'] = get_count_from_json('1~3年 ', parsed_item['work_exp_json'])
            parsed_item['work_exp_03_05'] = get_count_from_json('3~5年', parsed_item['work_exp_json'])
            parsed_item['work_exp_05_10'] = get_count_from_json('5~10年', parsed_item['work_exp_json'])
            parsed_item['work_exp_10_15'] = get_count_from_json('10~15年', parsed_item['work_exp_json'])
            parsed_item['work_exp_15_20'] = get_count_from_json('15~20年', parsed_item['work_exp_json'])
            parsed_item['work_exp_20_25'] = get_count_from_json('20~25年', parsed_item['work_exp_json'])
            parsed_item['work_exp_25_99'] = get_count_from_json('25年以上', parsed_item['work_exp_json'])

            # major
            parsed_item['major_info_mgmt'] = get_count_from_json('資訊管理相關', parsed_item['major_json'])
            parsed_item['major_cs'] = get_count_from_json('資訊工程相關', parsed_item['major_json'])
            parsed_item['major_stat'] = get_count_from_json('統計學相關', parsed_item['major_json'])
            parsed_item['major_math_stat'] = get_count_from_json('數理統計相關', parsed_item['major_json'])

            # skill
            parsed_item['skill_java'] = get_count_from_json('Java', parsed_item['skill_json'])
            parsed_item['skill_python'] = get_count_from_json('Python', parsed_item['skill_json'])

            # language
            parsed_item['lang_eng'] = get_count_from_json('英文', parsed_item['lang_json'])
            parsed_item['lang_japan'] = get_count_from_json('日文', parsed_item['lang_json'])
            parsed_item['lang_korean'] = get_count_from_json('韓文', parsed_item['lang_json'])

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

            # 公司地區 (derived)
            company_addr = parsed_item['company_addr']
            parsed_item['company_addr_area'] = convert_addr_to_area(company_addr)

            # 公司集團 (derived)
            company_name = parsed_item['company_name']
            parsed_item['company_group'] = convert_company_name_to_company_group(company_name)

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


if __name__ == '__main__':
    # processor = CrawlDataProcessor()
    processor = CrawlDataJsonProcessor()
    processor.process()