import sys
sys.path.append('.')
# sys.path.append('..')

import re
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, func
from datetime import datetime

from model.model import db_connect, create_table, TJob, TJobAnalysis, TCompany
from config.config import DB_CONNECTION_STRING
from reference.hr_bank_code_mapping import MAPPING


TODAY_DATE = int(datetime.now().strftime('%Y%m%d'))


class CrawlDataProcessor:

    def __init__(self, **kwarg):

        # get the date which want to process data, if "process_date"=0, it means process all data.
        if 'process_all' in kwarg.keys():
            if kwarg['process_all'] == True:
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
        self.process_t_job_all()
        self.process_t_company()


    def process_t_job(self):
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
                result.need_count_max = need_count_max
                result.need_count_min = need_count_min

                # 薪資類型
                salary_type = result.salary_type
                result.salary_type_desc = convert_salary_type_code_to_desc(salary_type)

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


    def process_t_job_all(self):
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



# T_JOB =========================================
# 需求人數
def get_need_count_max_and_min(need_count_desc):
    need_count_min = 0
    need_count_max = 0

    need_count_list = re.findall('\d+', need_count_desc)
    if len(need_count_list) == 2: # n~m人 -> min: n, max: m
        need_count_min = need_count_list[0]
        need_count_max = need_count_list[1]

    elif len(need_count_list) == 1: # n人以上 -> min: n, max: n
        need_count_min = need_count_list[0]
        need_count_max = need_count_list[0]

    elif len(need_count_list) == 0: # 不限 -> min: 1, max: 1
        need_count_min = 1
        need_count_max = 1

    return need_count_max, need_count_min


# 薪資類型
def convert_salary_type_code_to_desc(salary_type):
    salary_type_mapping = MAPPING['salary_type_mapping']
    return salary_type_mapping.get(salary_type, salary_type)


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


if __name__ == '__main__':
    processor = CrawlDataProcessor()
    processor.process()