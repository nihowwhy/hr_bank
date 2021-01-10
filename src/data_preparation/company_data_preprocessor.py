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
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from datetime import datetime
import pandas as pd
from sqlalchemy.exc import IntegrityError

from model.model import db_connect, create_table, TJobPrim, TRawCompDesc, TCompDesc


class CompanyDataPreprocessor:
    
    def __init__(self):
        engine = db_connect(DB_CONNECTION_STRING)
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        
    
    def process(self):
        session = self.Session()#(expire_on_commit=False)
        
        raw_companies = session.query(TRawCompDesc).all()    
        pk_crawl_date_list = []
        pk_comp_no_list = []
        for raw_comp in raw_companies:
            pk_crawl_date_list.append(raw_comp.crawl_date)
            pk_comp_no_list.append(raw_comp.comp_no)
        session.close()
        
        for crawl_date, comp_no in zip(pk_crawl_date_list, pk_comp_no_list):
            
            raw_comp = session.query(TRawCompDesc).filter_by(crawl_date=crawl_date, comp_no=comp_no).first()
            
            crawl_date = raw_comp.crawl_date
            comp_no = raw_comp.comp_no
            
            crawled_comp_desc_json = raw_comp.comp_desc_json
            crawled_comp_desc_dict = CompDescJsonProcessor(crawled_comp_desc_json).process()
            
            
            comp_desc_dict = self._format_crawled_data_to_table_column(
                crawl_date, 
                comp_no, 
                crawled_comp_desc_dict, 
            )
            
            print(f'{crawl_date}  {comp_no}')

            try:           
                comp_desc = TCompDesc(**comp_desc_dict)
                session.add(comp_desc)
                session.commit()
                
            except IntegrityError:
                session.rollback()
                print('does not insert data, but delete raw data')
                session.delete(raw_comp)
                session.commit()
                
            except Exception as e:
                print(f'>>> Error: {e}')
                session.rollback()
                raise
                
            else:
                '''Delete raw data.'''
                print('insert data and delete raw data')
                session.delete(raw_comp)
                session.commit()
                
            finally:
                session.close()
        
        print('done')
        
        
    @staticmethod
    def _format_crawled_data_to_table_column(
            crawl_date, 
            comp_no, 
            crawled_comp_desc_dict):
        comp_desc_dict = {}
        
        comp_desc_dict = crawled_comp_desc_dict
        comp_desc_dict['crawl_date'] = crawl_date
        comp_desc_dict['comp_no'] = comp_no
        
        return comp_desc_dict
    
    
class CompDescJsonProcessor:
    
    def __init__(self, comp_desc_json: str):
        self.d = json.loads(comp_desc_json)
        
        
    def process(self):        
        d = self.d
        comp_desc_dict = {}

        comp_desc_dict['comp_name'] = d['data']['custName']
        comp_desc_dict['indust_name'] = d['data']['industryDesc']
        comp_desc_dict['indust_cat'] = d['data']['indcat']
        comp_desc_dict['emp_count_desc'] = d['data']['empNo']
        comp_desc_dict['capital'] = d['data']['capital']
        comp_desc_dict['comp_addr'] = d['data']['address']
        comp_desc_dict['comp_link'] = d['data']['custLink']
        comp_desc_dict['profile'] = remove_unicode_blank(d['data']['profile'])
        comp_desc_dict['product'] = remove_unicode_blank(d['data']['product'])
        comp_desc_dict['welfare'] = remove_unicode_blank(d['data']['welfare'])
        comp_desc_dict['management'] = remove_unicode_blank(d['data']['management'])
        comp_desc_dict['news'] = remove_unicode_blank(d['data']['news'])
        comp_desc_dict['welfare_tag'] = join_list_element(d['data']['tagNames'])
        comp_desc_dict['legal_tag'] = join_list_element(d['data']['legalTagNames'])
        comp_desc_dict['comp_addr_dist'] = d['data']['addrNoDesc']
        
        return comp_desc_dict
    
    
# utils
def join_dict_item_in_list(l: list, key: str):
    dict_item_list = [d[key] for d in l]
    return '、'.join(dict_item_list)


def join_list_element(l: list):
    return '、'.join(l)


def remove_unicode_blank(text):
    text = text.replace('\xa0', '')
    text = text.replace('\u3000', '')
    text = text.replace('\r', '')
    return text


if __name__ == '__main__':
    filename = 'company_data_preprocessor'
    print(f'"{filename}" is ready.')