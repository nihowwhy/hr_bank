from sqlalchemy import create_engine
from scrapy.utils.project import get_project_settings

from model.hr_bank_raw_model import Base

SETTINGS = get_project_settings()
DB_CONNECTION_STRING = SETTINGS.get('DB_CONNECTION_STRING')


def db_connect():
    ''' Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    '''
    print(f'>>> DB_CONNECTION_STRING: {SETTINGS.get("DB_CONNECTION_STRING")}')
    return create_engine(DB_CONNECTION_STRING)


def create_table(engine):
    Base.metadata.create_all(engine)
    