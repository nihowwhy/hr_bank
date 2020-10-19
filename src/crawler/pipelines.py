# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_

from crawler.models import db_connect, create_table, TJobPrim, TJobDesc, TCompDesc



class JobCrawlerPipeline(object):
    
    def __init__(self):
        ''' Initialize database connection and sessionmaker
        Creates tables
        '''
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    
    def process_item(self, item, spider):
        session = self.Session()
        
        job_no = item['job_no']
        comp_no = item['comp_no']
        crawl_date = item['crawl_date']

        exist_job = session.query(TJobPrim).filter_by(job_no=job_no, crawl_date=crawl_date).first()     # if job exists
        exist_comp = session.query(TCompDesc).filter_by(comp_no=comp_no, crawl_date=crawl_date).first() # if company exists
        
        if exist_job is None:
            # JOB_PRIM table
            job_prim = TJobPrim()
            job_prim.job_no = item['job_no']
            job_prim.job_id = item['job_id']
            job_prim.job_name = item['job_name']
            job_prim.comp_no = item['comp_no']
            job_prim.comp_id = item['comp_id']
            job_prim.comp_name = item['comp_name']
            job_prim.indust_no = item['indust_no']
            job_prim.indust_desc = item['indust_desc']
            job_prim.appear_date = item['appear_date']
            job_prim.crawl_date = item['crawl_date']
            
            # JOB_DESC table
            job_desc = TJobDesc()
            job_desc.job_no = item['job_no']
            job_desc.search_job_json = item['search_job_json']
            job_desc.job_desc_json = item['job_desc_json']
            job_desc.job_analysis_json = item['job_analysis_json']
            job_desc.crawl_date = item['crawl_date']
        else:
            msg = f"Duplicate job found: [{item['job_id']}] {item['job_name']}"
#             print(msg)
            raise DropItem(msg)
            session.close()
            
        if exist_comp is None:
            # COMP_DESC table
            comp_desc = TCompDesc()
            comp_desc.comp_no = item['comp_no']
            comp_desc.comp_desc_json = item['comp_desc_json']
            comp_desc.crawl_date = item['crawl_date']
        else:
            pass

        try:
            if exist_comp is None:
                objs = [job_prim, job_desc, comp_desc]
            else:
                objs = [job_prim, job_desc]
            session.add_all(objs)
            session.commit()

        except:
            session.rollback()
            raise

        finally:
            session.close()

        return item
    
    
    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        stats = json.dumps(stats, indent=2)
        print('[Close Spider]')
        print(f'Stats:\n{stats}')
