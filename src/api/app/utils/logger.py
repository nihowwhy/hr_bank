import os
import logging
import logging.handlers

from config import config


LOGS_DIR= config['logs_dir']
PROJECT_NAME= config['project_name']


def get_logger():
    log_folder = LOGS_DIR
    if os.path.exists(log_folder) == False:
        os.makedirs(log_folder)


    logger = logging.getLogger(PROJECT_NAME)
    log_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    log_formatter = logging.Formatter(log_format)

    logger.handlers = []


    # streaming
#     stream_handler = logging.StreamHandler()
#     stream_handler.setFormatter(log_formatter)
#     stream_handler.setLevel(logging.INFO)
#     logger.addHandler(stream_handler)


    # info
    info_log_filename = 'info.log'
    info_log_filepath = os.path.join(log_folder, info_log_filename)
    file_handler_info = logging.handlers.TimedRotatingFileHandler(info_log_filepath, when='midnight', backupCount=7)
    file_handler_info.setFormatter(log_formatter)
    file_handler_info.setLevel(logging.INFO)
    logger.addHandler(file_handler_info)


    # error
    error_log_filename = 'error.log'
    error_log_filepath = os.path.join(log_folder, error_log_filename)
    file_handler_error = logging.handlers.TimedRotatingFileHandler(error_log_filepath, when='midnight', backupCount=7)
    file_handler_error.setFormatter(log_formatter)
    file_handler_error.setLevel(logging.ERROR)
    logger.addHandler(file_handler_error)

    return logger