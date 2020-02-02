# -*- coding: utf-8 -*-
import os
import configparser


PROJECT_NAME = 'hr_bank_test'


# =================================================
USE_PROXY = False                   # True or False
# =================================================


try:
    # Default config paths
    CURRENT_ENV_PATH = '/ods/analysis/CURRENT_ENV'
    CONFIG_INI_PATH = '/ods/analysis/config.ini'
    
    # Read current environment
    with open(CURRENT_ENV_PATH, 'r') as env:
        CURRENT_ENV = env.read().replace('\n', '')
    
    # Read config.ini
    config_parser = configparser.ConfigParser()
    config_parser.read(CONFIG_INI_PATH)
    env_config = config_parser[CURRENT_ENV]
    print(f'>>> using "{CURRENT_ENV}" config ...')
    
except:
    CURRENT_ENV = ''
    env_config = {}

    
# Directory
project_config_path = os.path.abspath(__file__)
project_config_dir = os.path.dirname(project_config_path)

PROJECT_DIR = os.path.abspath(os.path.join(project_config_dir, '../..'))
SAVE_FILE_DIR = os.path.join(PROJECT_DIR, 'data')
LOGS_DIR = os.path.join(env_config.get('logs_dir', os.path.join(PROJECT_DIR, 'logs')), PROJECT_NAME)


# Proxy
PROXY_IP = env_config.get('proxy_ip', '')
PROXY_PORT = env_config.get('proxy_port', '')
PROXIES = {
    'http': f'http://{PROXY_IP}:{PROXY_PORT}',
    'https': f'https://{PROXY_IP}:{PROXY_PORT}',
} if PROXY_IP and PROXY_PORT else {}


# Headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
    'Connection': 'keep-alive'
}


# Project config
config = {
    'project_name': PROJECT_NAME,
    'current_env': CURRENT_ENV,
    'headers': HEADERS,
    'use_proxy': USE_PROXY,
    'proxy_ip': PROXY_IP,
    'proxy_port': PROXY_PORT,
    'proxies': PROXIES,
    'project_dir': PROJECT_DIR,
    'save_file_dir': SAVE_FILE_DIR,
    'logs_dir': LOGS_DIR,
}
print(f'>>> Project Config= {config}')

