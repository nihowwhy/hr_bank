from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Date, DateTime, Float, Boolean, Text
from scrapy.utils.project import get_project_settings

SETTINGS = get_project_settings()
Base = declarative_base()


def db_connect():
    ''' Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    '''
    print(f'>>> DB_CONNECTION_STRING: {SETTINGS.get("DB_CONNECTION_STRING")}')
    return create_engine(SETTINGS.get('DB_CONNECTION_STRING'))


def create_table(engine):
    Base.metadata.create_all(engine)

    
# Association Table for Many-to-Many relationship between Quote and Tag

# quote_tag = Table('quote_tag', Base.metadata,
#     Column('quote_id', Integer, ForeignKey('quote.id')),
#     Column('tag_id', Integer, ForeignKey('tag.id'))
# )




class TJobPrim(Base):
    __tablename__ = 'JOB_PRIM'
    
    job_no = Column('JOB_NO', String, primary_key=True)
    job_id = Column('JOB_ID', String)
    job_name = Column('JOB_NAME', String)
    comp_no = Column('COMP_NO', String)
    comp_id = Column('COMP_ID', String)
    comp_name = Column('COMP_NAME', String)
    indust_no = Column('INDUST_NO', String)
    indust_desc = Column('INDUST_DESC', String)
    update_date = Column('UPDATE_DATE', Integer)
    first_crawl_date = Column('FIRST_CRAWL_DATE', Integer)
    last_crawl_date = Column('LAST_CRAWL_DATE', Integer)
    

class TJobDesc(Base):
    __tablename__ = 'JOB_DESC'
    
    job_no = Column('JOB_NO', String, primary_key=True)
    job_role = Column('JOB_ROLE', String)
    job_ro = Column('JOB_RO', String)
    job_addr_dist = Column('JOB_ADDR_DIST', String)
    job_addr = Column('JOB_ADDR', Integer)
    post_code = Column('POST_CODE', Integer)
    job_desc = Column('JOB_DESC', String)
    salary_type = Column('SALARY_TYPE', Integer)
    salary_min = Column('SALARY_MIN', Integer)
    salary_max = Column('SALARY_MAX', Integer)
    salary_desc = Column('SALARY_DESC', String)
    zone = Column('ZONE', String)
    tag = Column('TAG', String)
    job_source = Column('JOB_SOURCE', String)
    job_category = Column('JOB_CATEGORY', String)
    job_type = Column('JOB_TYPE', String)
    work_type = Column('WORK_TYPE', String)
    indust_area = Column('INDUST_AREA', String)
    longitude = Column('LONGITUDE', Float)
    latitude = Column('LATITUDE', Float)
    manage_resp = Column('MANAGE_RESP', String)
    business_trip = Column('BUSINESS_TRIP', String)
    work_period = Column('WORK_PERIOD', String)
    vacation_policy = Column('VACATION_POLICY', String)
    start_work_day = Column('START_WORK_DAY', String)
    hire_type = Column('HIRE_TYPE', String)
    delegate_recruit = Column('DELEGATE_RECRUIT', String)
    

    
class TJobQual(Base):
    __tablename__ = 'JOB_QUAL'
    
    job_no = Column('JOB_NO', String, primary_key=True)
    edu = Column('EDU', String)
    exp = Column('', String)
    exp_desc = Column('', String)
    major = Column('', String)
    lang = Column('', String)
    local_lang = Column('', String)
    specialty = Column('', String)
    skill = Column('', String)
    cert = Column('', String)
    driver_license = Column('', String)
    other = Column('', String)
    accept_role = Column('', String)
    disaccept_role = Column('', String)
    

class TJobWelfare(Base):
    __tablename__ = 'JOB_WELFARE'
    
    job_no = Column('JOB_NO', String, primary_key=True)
    welfare_tag = Column('', String)
    welfare_desc = Column('', String)
    legal_tag = Column('', String)
    

class TJobContact(Base):
    __tablename__ = 'JOB_CONTACT'
    
    job_no = Column('JOB_NO', String, primary_key=True)
    hr_name = Column('', String)
    email = Column('', String)
    visit = Column('', String)
    phone = Column('', String)
    other = Column('', String)
    reply = Column('', String)
    
    
class TJobStat(Base):
    __tablename__ = 'JOB_STAT'
    
    job_no = Column('JOB_NO', String, primary_key=True)
    crawl_date = Column('CRAWL_DATE', Integer)
    apply_num = Column('', Integer)
    apply_num_desc = Column('', String)
    need_num_min = Column('', Integer)
    need_num_max = Column('', Integer)
    need_num_desc = Column('', Integer)
    analysis_type = Column('', String)
    sex = Column('', String)
    edu = Column('', String)
    year_range = Column('', String)
    exp = Column('', String)
    lang = Column('', String)
    major = Column('', String)
    skill = Column('', String)
    cert = Column('', String)
    
    
class TCompDesc(Base):
    __tablename__ = 'COMP_DESC'
    
    comp_no = Column('COMP_NO', String, primary_key=True)
    comp_id = Column('', String)
    comp_name = Column('', String)
    indust_no = Column('', String)
    indust_desc = Column('', String)
    addr = Column('', String)
    profile = Column('', String)
    product = Column('', String)
    
    
class TCompStat(Base):
    __tablename__ = 'COMP_STAT'
    
    comp_no = Column('COMP_NO', String, primary_key=True)
    crawl_date = Column('CRAWL_DATE', Integer)
    emp_num = Column('', String)
    capital = Column('', String)


# class Author(Base):
#     __tablename__ = "author"

#     id = Column(Integer, primary_key=True)
#     name = Column('name', String(50), unique=True)
#     birthday = Column('birthday', DateTime)
#     bornlocation = Column('bornlocation', String(150))
#     bio = Column('bio', Text())
#     quotes = relationship('Quote', backref='author')  # One author to many Quotes


# class Tag(Base):
#     __tablename__ = "tag"

#     id = Column(Integer, primary_key=True)
#     name = Column('name', String(30), unique=True)
#     quotes = relationship('Quote', secondary='quote_tag',
#         lazy='dynamic', backref="tag")  # M-to-M for quote and tag