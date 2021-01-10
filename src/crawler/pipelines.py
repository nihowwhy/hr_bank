# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from scrapy.utils.project import get_project_settings

from model.model import db_connect, create_table, TRawSearch, TRawJob, TRawJobAnalysis, TRawComp


SETTINGS = get_project_settings()
DB_CONNECTION_STRING = SETTINGS.get('DB_CONNECTION_STRING')


class JobCrawlerPipeline(object):
    
    def __init__(self):
        ''' Initialize database connection and sessionmaker
        Creates tables
        '''
        engine = db_connect(DB_CONNECTION_STRING)
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    
    def process_item(self, item, spider):
        session = self.Session()
        
        # keys
        job_no = item['job_no']
        comp_no = item['comp_no']
        crawl_date = item['crawl_date']
        
        # if data exists
        is_t_raw_search_exist = bool(session.query(TRawSearch).filter_by(job_no=job_no, crawl_date=crawl_date).first())
        is_t_raw_job_exist = bool(session.query(TRawJob).filter_by(job_no=job_no, crawl_date=crawl_date).first())
        is_t_raw_job_analysis_exist = bool(session.query(TRawJobAnalysis).filter_by(job_no=job_no, crawl_date=crawl_date).first())
        is_t_raw_comp_exist = bool(session.query(TRawComp).filter_by(comp_no=comp_no, crawl_date=crawl_date).first())
        
        # if data does not exist, then set data to table object and list.
        table_object_list = []
        
        if is_t_raw_search_exist == False:
            t_raw_search = TRawSearch()
            t_raw_search.job_no = job_no
            t_raw_search.crawl_date = crawl_date
            t_raw_search.json_string = item['search_job_json']
            table_object_list.append(t_raw_search)
            
        if is_t_raw_job_exist == False:
            t_raw_job = TRawJob()
            t_raw_job.job_no = job_no
            t_raw_job.crawl_date = crawl_date
            t_raw_job.json_string = item['job_desc_json']
            table_object_list.append(t_raw_job)
            
        if is_t_raw_job_analysis_exist == False:
            t_raw_job_analysis = TRawJobAnalysis()
            t_raw_job_analysis.job_no = job_no
            t_raw_job_analysis.crawl_date = crawl_date
            t_raw_job_analysis.json_string = item['job_analysis_json']
            table_object_list.append(t_raw_job_analysis)
        
        is_ignore_comp = item['meta']['is_ignore_comp']
        if (is_t_raw_comp_exist == False) and (is_ignore_comp == True):
            t_raw_comp = TRawComp()
            t_raw_comp.comp_no = comp_no
            t_raw_comp.crawl_date = crawl_date
            t_raw_comp.json_string = item['comp_desc_json']
            table_object_list.append(t_raw_comp)
        
        # if job exists in all job tables, then return. 
        if all([is_t_raw_search_exist, is_t_raw_job_exist, is_t_raw_job_analysis_exist]):
            msg = f"Duplicate job found: [{item['job_id']}] {item['job_name']}"
            session.close()
            raise DropItem(msg)
            return
        
        # save data
        try:
            if table_object_list:
                session.add_all(table_object_list)
                session.commit()

        except:
            session.rollback()
            raise

        finally:
#             self._vacuum_db()
            session.close()
            return 
    
    
    def _vacuum_db(self):
        session = self.Session() 
        session.execute('VACUUM')
    
    
    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        stats = json.dumps(stats, indent=2, default=str)
        print('[Close Spider]')
        print(f'Stats:\n{stats}')
       
    