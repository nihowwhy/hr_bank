import os

CONFIG_INI_DIR = 'config/config.ini'


# config.ini
import configparser
config = configparser.ConfigParser()
config.read(CONFIG_INI_DIR)


# config.ini info
PROJECT_NAME = config['info']['project_name']
print(f'>>> PROJECT NAME: {PROJECT_NAME}')


# config.ini setting
LOG_FOLDER = config['setting']['log_folder']
DB_FOLDER = config['setting']['data_folder']
DB_NAME = config['setting']['db_name']
DATA_FOLDER = config['setting']['data_folder']


# directory init
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# output "raw_data, excel_data" directory
EXCEL_DATA_FOLDER = os.path.join(DATA_FOLDER, 'excel_data')
RAW_DATA_FOLDER = os.path.join(DATA_FOLDER, 'raw_data')
if not os.path.exists(EXCEL_DATA_FOLDER):
    os.makedirs(EXCEL_DATA_FOLDER)
if not os.path.exists(RAW_DATA_FOLDER):
    os.makedirs(RAW_DATA_FOLDER)



# database setting
DB_PATH = f'{DB_FOLDER}/{DB_NAME}'
DB_CONNECTION_STRING = f'sqlite:///{DB_FOLDER}/{DB_NAME}'
# DB_CONNECTION_STRING = '{drivername}://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8'.format(
#      drivername="sqlite",
#      user='',
#      passwd='',
#      host='',
#      port='',
#      db_name='hr_bank_db',
# )

