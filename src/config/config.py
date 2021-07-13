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
DB_FOLDER = config['setting']['db_folder']
DB_NAME = config['setting']['db_name']


# directory init
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)


# database setting
DB_CONNECTION_STRING = f'sqlite:///{DB_FOLDER}/{DB_NAME}'
# DB_CONNECTION_STRING = '{drivername}://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8'.format(
#      drivername="sqlite",
#      user='',
#      passwd='',
#      host='',
#      port='',
#      db_name='hr_bank_db',
# )

