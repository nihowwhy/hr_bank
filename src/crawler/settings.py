# -*- coding: utf-8 -*-

# Scrapy settings for crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os

CONFIG_INI_DIR = '../config.ini'

BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawler (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Referer': 'https://www.104.com.tw/jobs/search/?jobsource=2018indexpoc&ro=0'
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'crawler.middlewares.CrawlerSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'crawler.middlewares.CrawlerDownloaderMiddleware': 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'crawler.pipelines.JobCrawlerPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# config.ini
import configparser
config = configparser.ConfigParser()
config.read(CONFIG_INI_DIR)

# config.ini info
print(f'>>> CONFIG: {config}')
project_name = config['info']['project_name']
print(f'>>> PROJECT NAME: {project_name}')

# config.ini setting
log_folder = config['setting']['log_folder']
db_folder = config['setting']['db_folder']
db_name = config['setting']['hr_bank_db_name']

# directory init
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

# logging
from logging.handlers import TimedRotatingFileHandler
from scrapy.utils.log import configure_logging
import logging
log_filepath = os.path.join(log_folder, 'hr_bank_crawler.log')
logHandler = TimedRotatingFileHandler(log_filepath, when='midnight', interval=10)
configure_logging(install_root_handler=False)
logging.basicConfig(handlers=[logHandler])
# LOG_LEVEL = 'ERROR'


# database setting
DB_CONNECTION_STRING = f'sqlite:///{db_folder}/{db_name}'
# DB_CONNECTION_STRING = '{drivername}://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8'.format(
#      drivername="sqlite",
#      user='',
#      passwd='',
#      host='',
#      port='',
#      db_name='hr_bank_db',
# )

