# hr_bank
爬取104人力銀行的職缺資料

# 操作說明
1.調整"hr_bank/src/schedule.py"的filename跟url
因"error.ReactorNotRestartable"，目前一次只能爬取單一網址

2.切換目錄到"hr_bank/src"

3.執行"python run_scrapy_from_a_script.py"

4.資料將產出在"hr_bank/data/excel_data"，欄位說明可參考"hr_bank/table_schema.xlsx"

