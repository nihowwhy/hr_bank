# -*- coding: UTF-8 -*-

# Add crawler demand into "SCHEDULE" list

# Demand Format: {"prefix_of_filename": [start_url_1, start_url_2...]}.
# For example, if "prefix_of_filename" is "HR", then output filename will be "HR_RAW_2019-11-11.xlsx",
# and the file will be saved in "../../data" after finishing crawling.

SCHEDULE = [
    
    # 1
    {'LIANG_FIN_IT': [
        # 產業： 銀行業、金融控股業、人身保險業、產物保險業
        # 職類： 資訊軟體系統類
        # 地區： 全
        "https://www.104.com.tw/jobs/search/?ro=0&jobcat=2007000000&indcat=1004001001%2C1004001007%2C1004003001%2C1004003002&order=11&asc=0&page=1&mode=s&jobsource=2018indexpoc",
    ]},
    
    
    # # 2
    # {'LIANG_FIN': [
    #     # 產業： 銀行業、金融控股業、人身保險業、產物保險業
    #     # 職類： 行政/總務/法務類、資訊軟體系統類、財會/金融專業類
    #     # 地區： 全
    #     "https://www.104.com.tw/jobs/search/?ro=0&jobcat=2002000000%2C2007000000%2C2003000000&indcat=1004003001%2C1004003002%2C1004001001%2C1004001007&order=11&asc=0&page=1&mode=s&jobsource=2018indexpoc",
    # ]},
    
    
    # # 3
    # {'HR': [
    #     # 產業： 金融投顧及保險業
    #     # 職類： 資訊軟體系統類
    #     # 地區： 全
    #     "https://www.104.com.tw/jobs/search/?ro=0&jobcat=2007000000&indcat=1004000000&order=11&asc=0&page=1&mode=s&jobsource=2018indexpoc",
        
    #     # 產業： 一般製造業
    #     # 職類： 資訊軟體系統類
    #     # 地區： 全
    #     "https://www.104.com.tw/jobs/search/?ro=0&jobcat=2007000000&indcat=1002000000&order=11&asc=0&page=1&mode=s&jobsource=2018indexpoc",

    #     # 產業： 電子資訊_軟體_半導體相關業
    #     # 職類： 資訊軟體系統類
    #     # 地區： 全
    #     "https://www.104.com.tw/jobs/search/?ro=0&jobcat=2007000000&indcat=1001000000&order=11&asc=0&page=1&mode=s&jobsource=2018indexpoc",
    # ]},
    
    # TEST
#     {'TEST': [
#         "https://www.104.com.tw/jobs/search/?ro=0&jobcat=2007000000&indcat=1004001001%2C1004001007%2C1004003001%2C1004003002&order=11&asc=0&page=1&mode=s&jobsource=2018indexpoc",
#     ]},
    

]