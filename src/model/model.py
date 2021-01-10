from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy import Integer, String, Date, DateTime, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


def db_connect(db_connection_string):
    ''' Returns sqlalchemy engine instance
    '''
    print(f'>>> DB_CONNECTION_STRING: {db_connection_string}')
    return create_engine(db_connection_string)


def create_table(engine):
    Base.metadata.create_all(engine)


class TRawSearch(Base):
    __tablename__ = 'T_RAW_SEARCH'
    
    crawl_date = Column('CRAWL_DATE', Integer, primary_key=True)
    job_no = Column('JOB_NO', String, primary_key=True)
    json_string = Column('JSON_STRING', String)


class TRawJob(Base):
    __tablename__ = 'T_RAW_JOB'
    
    crawl_date = Column('CRAWL_DATE', Integer, primary_key=True)
    job_no = Column('JOB_NO', String, primary_key=True)
    json_string = Column('JSON_STRING', String)
    

class TRawJobAnalysis(Base):
    __tablename__ = 'T_RAW_JOB_ANALYSIS'
    
    crawl_date = Column('CRAWL_DATE', Integer, primary_key=True)
    job_no = Column('JOB_NO', String, primary_key=True)
    json_string = Column('JSON_STRING', String)
    
    
class TRawComp(Base):
    __tablename__ = 'T_RAW_COMP'
    
    crawl_date = Column('CRAWL_DATE', Integer, primary_key=True)
    comp_no = Column('COMP_NO', String, primary_key=True)
    json_string = Column('JSON_STRING', String)
    
    
class TJob(Base):
    __tablename__ = 'T_JOB'

    job_no = Column('JOB_NO', String, primary_key=True)
    job_id = Column('JOB_ID', String)
    job_name = Column('JOB_NAME', String)
    job_link = Column('JOB_LINK', String)
    job_type = Column('JOB_TYPE', String)
    job_role = Column('JOB_ROLE', String)
    job_cat = Column('JOB_CAT', String)
    
    apply_count = Column('APPLY_COUNT', Integer)
    need_emp = Column('NEED_EMP', String)
    need_count_min = Column('NEED_COUNT_MIN', Integer)
    need_count_max = Column('NEED_COUNT_MAX', Integer)
    salary_desc = Column('SALARY_DESC', String)
    salary_min = Column('SALARY_MIN', Integer)
    salary_max = Column('SALARY_MAX', Integer)
    salary_type = Column('SALARY_TYPE', String)
    
    accept_role = Column('ACCEPT_ROLE', String)
    disaccept_role = Column('DISACCEPT_ROLE', String)
    edu = Column('EDU', String)
    work_exp = Column('WORK_EXP', Integer)
    major = Column('MAJOR', String)
    lang = Column('LANG', String)
    local_lang = Column('LOCAL_LANG', String)
    speciality = Column('SPECIALITY', String)
    skill = Column('SKILL', String)
    cert = Column('CERT', String)
    driver_license = Column('DRIVER_LICENSE', String)
    other = Column('OTHER', String)
    
    job_desc = Column('JOB_DESC', String)
    job_tag = Column('JOB_TAG', String)
    manage_resp = Column('MANAGE_RESP', String)
    business_trip = Column('BUSINESS_TRIP', String)
    work_period = Column('WORK_PERIOD', String)
    vacation_policy = Column('VACATION_POLICY', String)
    start_work_day = Column('START_WORK_DAY', String)
    hire_type = Column('HIRE_TYPE', String)
    delegate_recruit = Column('DELEGATE_RECRUIT', String)
    job_addr_dist = Column('JOB_ADDR_DIST', String)
    landmark_tag = Column('LANDMARK_TAG', String)
    lon = Column('LON', String)
    lat = Column('LAT', String)
    appear_date = Column('APPEAR_DATE', Integer)


class TJobAnalysis(Base):
    __tablename__ = 'T_JOB_ANALYSIS'
    
    update_date = Column('UPDATE_DATE', Integer, primary_key=True)
    job_no = Column('JOB_NO', String, primary_key=True)
    apply_count = Column('APPLY_COUNT', Integer)
    sex = Column('SEX', String)
    edu = Column('EDU', String)
    year_range = Column('YEAR_RANGE', String)
    work_exp = Column('WORK_EXP', String)
    lang = Column('LANG', String)
    major = Column('MAJOR', String)
    skill = Column('SKILL', String)
    cert = Column('CERT', String)
    crawl_date = Column('CRAWL_DATE', Integer)

    
class TComp(Base):
    __tablename__ = 'T_COMP'
    
    crawl_date = Column('CRAWL_DATE', Integer, primary_key=True)
    comp_no = Column('COMP_NO', String, primary_key=True)
    comp_name = Column('COMP_NAME', String)
#     indust_name = Column('INDUST_NAME', String)
    indust_no = Column('INDUST_NO', String)
    indust_desc = Column('INDUST_DESC', String)
    indust_cat = Column('INDUST_CAT', String)
    emp_count_desc = Column('EMP_COUNT_DESC', String)
    capital = Column('CAPITAL', String)
    comp_addr = Column('COMP_ADDR', String)
    comp_link = Column('COMP_LINK', String)
    profile = Column('PROFILE', String)
    product = Column('PRODUCT', String)
    welfare = Column('WELFARE', String)
    management = Column('MANAGEMENT', String)
    news = Column('NEWS', String)
    welfare_tag = Column('WELFARE_TAG', String)
    legal_tag = Column('LEGAL_TAG', String)
    comp_addr_dist = Column('COMP_ADDR_DIST', String) 
    

 
