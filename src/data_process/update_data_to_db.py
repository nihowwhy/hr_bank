import sys
sys.path.append('.')

import os
# import pickle
import json
import pandas as pd
from sqlalchemy.orm import sessionmaker

from config.config import DASHBOARD_DATA_RECORD_PATH, DB_CONNECTION_STRING, EXCEL_DATA_FOLDER
from model.model import db_connect, create_table, TJob, TCompany, TDashboard


class DashDatabaseProcessor:

    def __init__(self):
        ''' Initialize database connection and sessionmaker
        Creates tables
        '''
        print('===============')
        print(f'>>> Create DB')
        print(f'>>> Connection String: {DB_CONNECTION_STRING}')
        print('===============')

        # create dashboard schema
        self.engine = db_connect(DB_CONNECTION_STRING)
        create_table(self.engine)
        self.Session = sessionmaker(bind=self.engine)


    def process(self):
        # get saved excel filenames in db
        saved_excel_files = self.get_saved_excel_filenames_in_db()
        saved_job_excel_filenames = saved_excel_files['saved_job_filenames']
        saved_company_excel_filenames = saved_excel_files['saved_company_filenames']

        # get excel filenames in folder
        excel_filenames_in_folder = self.get_excel_filenames_in_excel_data_folder()
        job_excel_filenames_in_folder = [filename for filename in excel_filenames_in_folder if 'job' in filename]
        company_excel_filenames_in_folder = [filename for filename in excel_filenames_in_folder if 'company' in filename]

        # get the excel filenames which don't exist in db
        job_excel_filenames_to_process = self.get_excel_filenames_to_save_into_db(job_excel_filenames_in_folder, saved_job_excel_filenames)
        company_excel_filenames_to_process = self.get_excel_filenames_to_save_into_db(company_excel_filenames_in_folder, saved_company_excel_filenames)

        # sort excel filenames order, from new to old
        # the filename format should be "XXXX_20210101.xlsx"
        job_excel_filenames_to_process.sort(key=lambda x: x.split('_')[-1], reverse=True)
        company_excel_filenames_to_process.sort(key=lambda x: x.split('_')[-1], reverse=True)

        # read excel data
        self.update_job_data_in_db(job_excel_filenames_to_process, 'T_JOB')

        # update data from new to old file (eliminate redundant update)

        # update records (add excel filenames to "dash_data_records")




    @staticmethod
    def get_saved_excel_filenames_in_db():
        ''' get records that saved excel filenames
        '''
        try:
            with open(DASHBOARD_DATA_RECORD_PATH, mode='r', encoding='utf-8') as f:
                # dash_data_records = pickle.load(f)
                dash_data_records = json.loads(f)
        except:
            dash_data_records = {'saved_job_filenames': [], 'saved_company_filenames': [],}
        finally:
            return dash_data_records


    @staticmethod
    def get_excel_filenames_in_excel_data_folder():
        ''' Read excel filenames in folder
        '''
        return [filename for filename in os.listdir(EXCEL_DATA_FOLDER) if filename.endswith('xlsx')]


    @staticmethod
    def get_excel_filenames_to_save_into_db(excel_filenames_in_folder, saved_excel_filenames):
        ''' Get the excel filenames that don't exist in db
        '''
        return list(set(excel_filenames_in_folder) - set(saved_excel_filenames))


    def update_job_data_in_db(self, excel_filenames, table_name):
        insert_df = pd.DataFrame()
        for excel_filename in excel_filenames:
            excel_path = os.path.join(EXCEL_DATA_FOLDER, excel_filename)
            excel_df = pd.read_excel(excel_path)
            excel_columns = [col.upper() for col in excel_df.columns]
            excel_df.columns = excel_columns

            if len(insert_df) == 0:
                insert_df = excel_df
            elif table_name == 'T_JOB':
                new_data_df = excel_df[~excel_df['JOB_ID'].isin(insert_df['JOB_ID'])]
                insert_df = pd.concat([insert_df, new_data_df], axis=0, ignore_index=True)
            elif table_name == 'T_COMPANY':
                new_data_df = excel_df[~excel_df['COMPANY_ID'].isin(insert_df['COMPANY_ID'])]
                insert_df = pd.concat([insert_df, new_data_df], axis=0, ignore_index=True)


            # session = self.Session()
            # session.close()
            table_columns = [col.key for col in TJob.__table__.columns]
            insert_table_columns = list(set.intersection(set(excel_columns), set(table_columns)))
            insert_db_df = insert_df[insert_table_columns]
            insert_db_df.to_sql(table_name, con=self.engine, if_exists='replace', index=False)




# add update filenames to "dash_data_records"
if False:
    input_excel_filenames.extend(excel_data_filenames)
    with open(DASHBOARD_DATA_RECORD_PATH, mode='w', encoding='utf-8') as f:
        pickle.dump(f)



if __name__ == '__main__':
    p = DashDatabaseProcessor()
    p.process()