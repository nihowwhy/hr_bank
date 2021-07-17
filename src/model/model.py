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


class TJob(Base):
    __tablename__ = 'T_JOB'

    job_id = Column('JOB_ID', String, primary_key=True)
    job_no = Column('JOB_NO', String, primary_key=True)

    job_name = Column('JOB_NAME', String)
    job_cat = Column('JOB_CAT', String)
    job_cat_desc = Column('JOB_CAT_DESC', String)
    company_name = Column('COMPANY_NAME', String)
    company_id = Column('COMPANY_ID', String)
    company_no = Column('COMPANY_NO', String)
    need_count_desc = Column('NEED_COUNT_DESC', String)
    need_count_min = Column('NEED_COUNT_MIN', Integer)
    need_count_max = Column('NEED_COUNT_MAX', Integer)
    need_count = Column('NEED_COUNT', Integer)
    apply_count = Column('APPLY_COUNT', Integer)
    salary = Column('SALARY', Integer)
    salary_desc = Column('SALARY_DESC', String)
    salary_min = Column('SALARY_MIN', Integer)
    salary_max = Column('SALARY_MAX', Integer)
    salary_type = Column('SALARY_TYPE', String)
    salary_type_desc = Column('SALARY_TYPE_DESC', String)
    job_desc = Column('JOB_DESC', String)
    job_type = Column('JOB_TYPE', String)
    job_role = Column('JOB_ROLE', String)
    job_role_desc = Column('JOB_ROLE_DESC', String)
    edu = Column('EDU', String)
    work_exp = Column('WORK_EXP', Integer)
    major = Column('MAJOR', String)
    lang = Column('LANG', String)
    local_lang = Column('LOCAL_LANG', String)
    specialty = Column('SPECIALTY', String)
    skill = Column('SKILL', String)
    cert = Column('CERT', String)
    driver_license = Column('DRIVER_LICENSE', String)
    other = Column('OTHER', String)
    accept_role = Column('ACCEPT_ROLE', String)
    disaccept_role = Column('DISACCEPT_ROLE', String)
    manage_resp = Column('MANAGE_RESP', String)
    business_trip = Column('BUSINESS_TRIP', String)
    work_period = Column('WORK_PERIOD', String)
    vacation_policy = Column('VACATION_POLICY', String)
    start_work_day = Column('START_WORK_DAY', String)
    job_addr_area = Column('JOB_ADDR_AREA', String)
    job_addr_dist = Column('JOB_ADDR_DIST', String)
    job_addr = Column('JOB_ADDR', String)
    lon = Column('LON', String)
    lat = Column('LAT', String)
    appear_date = Column('APPEAR_DATE', Integer)
    close_date = Column('CLOSE_DATE', Integer)
    job_duration_day = Column('JOB_DURATION_DAY', Integer)
    is_job_exist = Column('IS_JOB_EXIST', String)
    custom_job_cat = ('CUSTOM_JOB_CAT', String)
    custom_memo = ('CUSTOM_MEMO', String)
    first_crawl_date = Column('FIRST_CRAWL_DATE', Integer)
    crawl_date = Column('CRAWL_DATE', Integer)


class TJobAnalysis(Base):
    __tablename__ = 'T_JOB_ANALYSIS'

    job_id = Column('JOB_ID', String, primary_key=True)
    job_no = Column('JOB_NO', String, primary_key=True)
    crawl_date = Column('CRAWL_DATE', Integer, primary_key=True)

    update_date = Column('UPDATE_DATE', Integer)
    job_name = Column('JOB_NAME', String)
    apply_count = Column('APPLY_COUNT', Integer)
    sex_json = Column('SEX_JSON', String)
    edu_json = Column('EDU_JSON', String)
    age_json = Column('AGE_JSON', String)
    work_exp_json = Column('WORK_EXP_JSON', String)
    lang_json = Column('LANG_JSON', String)
    major_json = Column('MAJOR_JSON', String)
    skill_json = Column('SKILL_JSON', String)
    cert_json = Column('CERT_JSON', String)


class TCompany(Base):
    __tablename__ = 'T_COMPANY'

    company_id = Column('COMPANY_ID', String, primary_key=True)
    company_no = Column('COMPANY_NO', String, primary_key=True)

    company_name = Column('COMPANY_NAME', String)
    industry_no = Column('INDUSTRY_NO', String)
    industry_desc = Column('INDUSTRY_DESC', String)
    industry_cat = Column('INDUSTRY_CAT', String)
    emp_count_desc = Column('EMP_COUNT_DESC', String)
    capital = Column('CAPITAL', String)
    profile = Column('PROFILE', String)
    product = Column('PRODUCT', String)
    management = Column('MANAGEMENT', String)
    welfare = Column('WELFARE', String)
    welfare_tag = Column('WELFARE_TAG', String)
    legal_tag = Column('LEGAL_TAG', String)
    company_addr_area = Column('COMPANY_ADDR_AREA', String)
    company_addr_dist = Column('COMPANY_ADDR_DIST', String)
    company_addr = Column('COMPANY_ADDR', String)
    company_group = Column('COMPANY_GROUP', String)
    crawl_date = Column('CRAWL_DATE', Integer)


class TDashboard(Base):
    __tablename__ = 'T_DASHBOARD'

    job_id = Column('JOB_ID', String, primary_key=True)
    job_no = Column('JOB_NO', String, primary_key=True)
    represent_date = Column('REPRESENT_DATE', Integer, primary_key=True)
    represent_date_min = Column('REPRESENT_DATE_MIN', Integer)
    represent_date_max = Column('REPRESENT_DATE_MAX', Integer)
    job_name = Column('JOB_NAME', String)
    company_id = Column('COMPANY_ID', String)
    company_no = Column('COMPANY_NO', String)
    company_name = Column('COMPANY_NAME', String)
    salary = Column('SALARY', Integer)
    need_count = Column('NEED_COUNT', Integer)
    need_count_min = Column('NEED_COUNT_MIN', Integer)
    need_count_max = Column('NEED_COUNT_MAX', Integer)
    apply_count = Column('APPLY_COUNT', Integer)
    sex_male = Column('SEX_MALE', Integer)
    sex_female = Column('SEX_FEMALE', Integer)
    edu_junior = Column('EDU_JUNIOR', Integer)
    edu_senior = Column('EDU_SENIOR', Integer)
    edu_undergrad = Column('EDU_UNDERGRAD', Integer)
    edu_grad = Column('EDU_GRAD', Integer)
    age_00_20 = Column('AGE_00_20', Integer)
    age_21_25 = Column('AGE_21_25', Integer)
    age_26_30 = Column('AGE_26_30', Integer)
    age_31_35 = Column('AGE_31_35', Integer)
    age_36_40 = Column('AGE_36_40', Integer)
    age_41_45 = Column('AGE_41_45', Integer)
    age_46_50 = Column('AGE_46_50', Integer)
    age_51_55 = Column('AGE_51_55', Integer)
    age_56_60 = Column('AGE_56_60', Integer)
    age_60_99 = Column('AGE_60_99', Integer)
    work_exp_0 = Column('WORK_EXP_0', Integer)
    work_exp_00_01 = Column('WORK_EXP_00_01', Integer)
    work_exp_01_03 = Column('WORK_EXP_01_03', Integer)
    work_exp_03_05 = Column('WORK_EXP_03_05', Integer)
    work_exp_05_10 = Column('WORK_EXP_05_10', Integer)
    work_exp_10_15 = Column('WORK_EXP_10_15', Integer)
    work_exp_15_20 = Column('WORK_EXP_15_20', Integer)
    work_exp_20_25 = Column('WORK_EXP_20_25', Integer)
    work_exp_25_99 = Column('WORK_EXP_25_99', Integer)
    major_info_mgmt = Column('MAJOR_INFO_MAGMT', Integer)
    major_cs = Column('MAJOR_CS', Integer)
    major_stat = Column('MAJOR_STAT', Integer)
    major_math_stat = Column('MAJOR_MATH_STAT', Integer)
    skill_java = Column('SKILL_JAVA', Integer)
    skill_python = Column('SKILL_PYTHON', Integer)
    lang_eng = Column('LANG_ENG', Integer)
    lang_japan = Column('LANG_JAPAN', Integer)
    lang_korean = Column('LANG_KOREAN', Integer)