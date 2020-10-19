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
    appear_date = Column('APPEAR_DATE', Integer)
    crawl_date = Column('CRAWL_DATE', Integer, primary_key=True)
    

class TJobDesc(Base):
    __tablename__ = 'JOB_DESC'
    
    job_no = Column('JOB_NO', String, primary_key=True)
    search_job_json = Column('SEARCH_JOB_JSON', String)
    job_desc_json = Column('JOB_DESC_JSON', String)
    job_analysis_json = Column('JOB_ANALYSIS_JSON', String)
    crawl_date = Column('CRAWL_DATE', Integer, primary_key=True)
    
    
class TCompDesc(Base):
    __tablename__ = 'COMP_DESC'
    
    comp_no = Column('COMP_NO', String, primary_key=True)
    comp_desc_json = Column('COMP_DESC_JSON', String)
    crawl_date = Column('CRAWL_DATE', Integer, primary_key=True)
