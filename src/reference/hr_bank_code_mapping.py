# MAPPING
MAPPING = {

    'salary_type_mapping': { # 薪資類型
        '10': '面議',
        '20': '論件計酬',
        '30': '時薪',
        '40': '日薪',
        '50': '月薪',
        '60': '年薪',
    },

    'job_type_mapping': { # 工作類型

    },

    'job_role_mapping': { # 工作形式
        '1': '全職(不接受身障)',
        '2': '兼職(不接受身障)',
        '3': '管理職',
        '4': '全職(接受身障)',
        '5': '兼職(接受身障)',
    },

    'addr_area_mapping': { # 工作地區
        '台北': '北區',
        '新北': '北區',
        '宜蘭': '北區',
        '基隆': '北區',
        '桃園': '北區',
        '新竹': '北區',
        '苗栗': '中區',
        '台中': '中區',
        '彰化': '中區',
        '雲林': '中區',
        '嘉義': '南區',
        '台南': '南區',
        '高雄': '南區',
        '屏東': '南區',
        '南投': '南區',
        '花蓮': '東區',
        '台東': '東區',
        '澎湖': '離島',
        '金門': '離島',
        '連江': '離島',
        '其他': '海外',
    },


    'company_group_mapping': { # 公司集團

        # 富邦
        '富邦金融控股股份有限公司': '富邦',
        '富邦人壽保險股份有限公司(總公司)': '富邦',
        '台北富邦商業銀行股份有限公司': '富邦',
        '富邦產物保險股份有限公司': '富邦',
        '富邦綜合證券股份有限公司': '富邦',

        # 國泰
        '國泰人壽保險股份有限公司_總公司_國泰金控': '國泰',
        '國泰世紀產物保險股份有限公司': '國泰',
        '國泰綜合證券股份有限公司': '國泰',
        '國泰金控_國泰金融控股股份有限公司': '國泰',
        '國泰世華商業銀行股份有限公司_人力資源部': '國泰',
    },


    'industry_no_mapping': { #
        '1003000000': '批發╱零售╱傳直銷業',
        '1003001000': '批發業',
        '1003001001': '農╱畜╱水產品批發業',
        '1003001002': '食品什貨批發業',
        '1003001003': '鞋類╱布類╱服飾品批發業',
        '1003001004': '家庭電器╱設備及用品批發業',
        '1003001005': '藥品╱化妝品及清潔用品批發業',
        '1003001006': '文教╱育樂用品批發業',
        '1003001007': '鐘錶╱眼鏡批發業',
        '1003001008': '首飾及貴金屬批發業',
        '1003001009': '建材╱傢俱批發業',
        '1003001010': '燃料批發業',
        '1003001011': '機械器具批發業',
        '1003001012': '汽機車及其零配件用品╱批發業',
        '1003001013': '化學原料及其製品批發業',
        '1003001014': '電子通訊╱電腦週邊批發業',
        '1003001015': '綜合商品批發代理業',
        '1003001016': '其他商品批發業',
        '1003002000': '零售業',
        '1003002001': '農╱畜╱水產品零售業',
        '1003002002': '食品什貨零售業',
        '1003002003': '鞋類╱布類╱服飾品零售業',
        '1003002004': '家庭電器╱設備及用品零售業',
        '1003002005': '藥品╱化妝品及清潔用品零售業',
        '1003002006': '文教╱育樂用品零售業',
        '1003002007': '鐘錶╱眼鏡零售業',
        '1003002008': '首飾及貴金屬零售業',
        '1003002009': '建材╱傢俱零售業',
        '1003002010': '燃料零售業',
        '1003002011': '機械器具零售業',
        '1003002012': '汽機車及其零配件╱用品零售業',
        '1003002013': '百貨相關業',
        '1003002014': '量販流通相關業',
        '1003002015': '電子通訊╱電腦週邊零售業',
        '1003002016': '其他零售業',
        '1003003000': '傳直銷相關業',
        '1003003001': '傳直銷相關業',
        '1005000000': '文教相關業',
        '1005001000': '教育服務業',
        '1005001001': '學前教育事業',
        '1005001002': '小學教育事業',
        '1005001003': '安親╱才藝班',
        '1005001004': '補習班',
        '1005001005': '中學教育事業',
        '1005001006': '職業學校教育事業',
        '1005001007': '大專校院教育事業',
        '1005001008': '特殊教育事業',
        '1005001009': '其他教育服務業',
        '1005002000': '出版業',
        '1005002001': '新聞出版業',
        '1005002002': '雜誌╱期刊出版業',
        '1005002003': '書籍出版業',
        '1005002004': '有聲出版業',
        '1005002005': '其他出版業',
        '1005003000': '藝文相關業',
        '1005003001': '技藝表演業',
        '1005003002': '藝文服務業',
        '1005003003': '圖書館╱博物館類似機構',
        '1006000000': '大眾傳播相關業',
        '1006001000': '電影業',
        '1006001001': '電影片製作業',
        '1006001002': '電影片發行業',
        '1006001003': '電影片映演業',
        '1006002000': '廣播電視業',
        '1006002001': '廣播業',
        '1006002002': '電視業',
        '1006002003': '廣播電視節目供應業',
        '1006003000': '廣告行銷╱傳播經紀業',
        '1006003001': '廣告行銷公關業',
        '1006003002': '藝人╱模特兒等經紀業',
        '1006003003': '會議展覽服務業',
        '1007000000': '旅遊╱休閒╱運動業',
        '1007001000': '運動及旅遊休閒服務業',
        '1007001001': '運動服務業',
        '1007001002': '休閒服務業',
        '1007001003': '旅遊服務業',
        '1009000000': '一般服務業',
        '1009001000': '人力仲介代徵╱派遣',
        '1009001001': '人力仲介代徵',
        '1009001002': '人力派遣服務',
        '1009002000': '租賃業',
        '1009002001': '機械設備租賃業',
        '1009002002': '運輸工具設備租賃業',
        '1009002003': '物品租賃業',
        '1009004000': '汽機車維修或服務相關業',
        '1009004001': '停車場業',
        '1009004002': '汽機車維修業',
        '1009004003': '汽車美容業',
        '1009004004': '其他汽機車相關業',
        '1009005000': '婚紗攝影及美髮美容業',
        '1009005001': '美髮業',
        '1009005002': '美容╱美體業',
        '1009005003': '婚紗服務業',
        '1009005004': '攝影沖印服務業',
        '1009006000': '徵信及保全樓管相關業',
        '1009006001': '保全樓管相關業',
        '1009006002': '徵信相關業',
        '1009007000': '其他服務相關業',
        '1009007001': '殯葬服務業',
        '1009007002': '寵物相關服務業',
        '1009007003': '洗衣服務業',
        '1009007004': '家事服務業',
        '1001000000': '電子資訊╱軟體╱半導體相關業',
        '1001001000': '軟體及網路相關業',
        '1001001001': '電腦系統整合服務業',
        '1001001002': '電腦軟體服務業',
        '1001001003': '網際網路相關業',
        '1001001004': '多媒體相關業',
        '1001001005': '數位內容產業',
        '1001001006': '其它軟體及網路相關業',
        '1001002000': '電信及通訊相關業',
        '1001002001': '電信相關業',
        '1001002003': '通訊機械器材相關業',
        '1001002004': '其他電信及通訊相關業',
        '1001003000': '電腦及消費性電子製造業',
        '1001003001': '電腦及其週邊設備製造業',
        '1001003002': '資料儲存媒體製造及複製業',
        '1001003003': '消費性電子產品製造業',
        '1001004000': '光電及光學相關業',
        '1001004001': '光電產業',
        '1001004002': '光學器材製造業',
        '1001005000': '電子零組件相關業',
        '1001005001': '印刷電路板製造業(PCB)',
        '1001005002': '被動電子元件製造業',
        '1001005003': '其他電子零組件相關業',
        '1001006000': '半導體業',
        '1001006001': 'IC設計相關業',
        '1001006002': '半導體製造業',
        '1001006003': '其他半導體相關業',
        '1002000000': '一般製造業',
        '1002001000': '食品菸草及飲料製造業',
        '1002001001': '菸草製造業',
        '1002001002': '屠宰業',
        '1002001003': '乳品製造業',
        '1002001004': '罐頭食品加工業',
        '1002001005': '糖果點心製造業',
        '1002001006': '食用油品及榖製品製造業',
        '1002001007': '製糖業',
        '1002001008': '調味用品製造業',
        '1002001009': '飲料製造業',
        '1002001010': '其他食品製造業',
        '1002002000': '紡織業',
        '1002002001': '紡紗業',
        '1002002002': '織布業',
        '1002002003': '不織布業',
        '1002002004': '繩╱纜╱網╱氈╱毯製造業',
        '1002002005': '印染整理業',
        '1002002006': '其他紡織業',
        '1002003000': '鞋類╱紡織製品製造業',
        '1002003001': '鞋類製造業',
        '1002003002': '紡織成衣業',
        '1002003003': '紡織帽製造業',
        '1002003004': '服飾品製造業',
        '1002003005': '其他紡織製品製造業',
        '1002004000': '家具及裝設品製造業',
        '1002004001': '木竹製品製造業',
        '1002004002': '傢俱及裝設品表面塗裝業',
        '1002004003': '金屬家具及裝設品製造業',
        '1002004004': '非金屬家具及裝設品製造業',
        '1002005000': '紙製品製造業',
        '1002005001': '紙相關製造業',
        '1002005002': '加工紙製造業',
        '1002005003': '紙容器製造業',
        '1002005004': '其他紙製品製造業',
        '1002006000': '印刷相關業',
        '1002006001': '製版業',
        '1002006002': '印刷業',
        '1002006003': '印刷品裝訂及加工業',
        '1002006004': '其他印刷輔助業',
        '1002007000': '化學相關製造業',
        '1002007001': '化學原料製造業',
        '1002007002': '人造纖維製造業',
        '1002007003': '合成樹脂╱塑膠及橡膠製造業',
        '1002007004': '塗料╱染料及顏料製造業',
        '1002007005': '藥品製造業',
        '1002007006': '清潔用品製造業',
        '1002007007': '化妝品製造業',
        '1002007008': '其他化學相關製造業',
        '1002008000': '石油及煤製品製造業',
        '1002008001': '石油煉製業',
        '1002008002': '其他石油及煤製品製造業',
        '1002009000': '橡膠及塑膠製品製造業',
        '1002009001': '橡膠製品製造業',
        '1002009002': '塑膠製品製造業',
        '1002010000': '非金屬礦物製品製造業',
        '1002010001': '陶瓷製品製造業',
        '1002010002': '玻璃及玻璃製品製造業',
        '1002010003': '水泥及水泥製品製造業',
        '1002010004': '耐火材料製造業',
        '1002010005': '石材製品製造業',
        '1002010006': '其他非金屬礦物製品製造業',
        '1002011000': '金屬相關製造業',
        '1002011001': '鋼鐵基本工業',
        '1002011002': '鋁基本工業',
        '1002011003': '銅基本工業',
        '1002011004': '鎂基本工業',
        '1002011005': '金屬鍛造及粉末冶金業',
        '1002011006': '金屬手工具製造業',
        '1002011007': '金屬結構及建築組件製造業',
        '1002011008': '金屬容器製造業',
        '1002011009': '金屬表面處理及熱處理業',
        '1002011010': '其他金屬相關製造業',
        '1002012000': '機械設備製造修配業',
        '1002012001': '自動控制相關業',
        '1002012002': '鍋爐及原動機製造修配業',
        '1002012003': '農業及園藝機械製造修配業',
        '1002012004': '金屬加工用機械製造修配業',
        '1002012005': '專用生產機械製造修配業',
        '1002012006': '建築及礦業機械設備製造修配業',
        '1002012007': '事務機器製造業',
        '1002012008': '污染防治設備製造修配業',
        '1002012009': '通用機械設備製造修配業',
        '1002012010': '其他機械製造修配業',
        '1002013000': '電力機械設備製造業',
        '1002013001': '電力機械器材製造修配業',
        '1002013002': '家用電器製造業',
        '1002013003': '照明設備製造業',
        '1002013004': '電池製造業',
        '1002013005': '其他電力器材製造業',
        '1002014000': '運輸工具製造業',
        '1002014001': '船舶及其零件製造修配業',
        '1002014002': '軌道車輛及其零件製造修配業',
        '1002014003': '汽車及其零件製造業',
        '1002014004': '機車及其零件製造業',
        '1002014005': '自行車及其零件製造業',
        '1002014006': '航空器及其零件製造修配業',
        '1002014007': '其他運輸工具及零件製造修配業',
        '1002015000': '精密儀器及醫療器材相關業',
        '1002015001': '精密儀器相關製造業',
        '1002015002': '醫療器材製造業',
        '1002015003': '鐘錶製造業',
        '1002016000': '育樂用品製造業',
        '1002016001': '文具禮品相關業',
        '1002016002': '玩具相關業',
        '1002016003': '育樂用品製造業',
        '1002017000': '其他相關製造業',
        '1002017001': '其他相關製造業',
        '1014000000': '農林漁牧水電資源業',
        '1014001000': '農產畜牧相關業',
        '1014001001': '農藝及園藝業',
        '1014001002': '畜牧業',
        '1014001003': '農事及畜牧服務業',
        '1014002000': '林場伐木相關業',
        '1014002001': '林場相關業',
        '1014002002': '伐木業',
        '1014003000': '漁撈水產養殖業',
        '1014003001': '漁獲打撈業',
        '1014003002': '水產養殖業',
        '1014004000': '水電能源供應業',
        '1014004001': '電力供應業',
        '1014004002': '氣體燃料供應業',
        '1014004003': '熱能供應業',
        '1014004004': '用水供應業',
        '1010000000': '運輸物流及倉儲',
        '1010001000': '運輸相關業',
        '1010001001': '海運',
        '1010001002': '鐵路運輸業',
        '1010001003': '大眾捷運系統',
        '1010001004': '汽車客運業',
        '1010001005': '汽車貨運業',
        '1010001006': '民航',
        '1010001007': '普通航空業',
        '1010001008': '其他陸上運輸業',
        '1010002000': '倉儲或運輸輔助業',
        '1010002001': '倉儲業',
        '1010002002': '儲配╱運輸物流業',
        '1010002003': '報關業',
        '1010002004': '船務代理業',
        '1010002005': '貨運承攬業',
        '1010002006': '陸上運輸輔助業',
        '1010002007': '水上運輸輔助業',
        '1010002008': '航空運輸輔助業',
        '1010002009': '其他運輸輔助業',
        '1010003000': '郵政及快遞業',
        '1010003001': '郵政業',
        '1010003002': '快遞服務業',
        '1013000000': '政治宗教及社福相關業',
        '1013001000': '政治機構相關業',
        '1013001001': '政府╱民意機關',
        '1013001002': '國防事業',
        '1013001003': '國際組織及外國機構',
        '1013002000': '宗教╱職業團體組織',
        '1013002001': '宗教組織',
        '1013002002': '職業團體',
        '1013002003': '其他組織',
        '1013003000': '社會福利服務業',
        '1013003001': '社會福利服務業',
        '1004000000': '金融投顧及保險業',
        '1004001000': '金融機構及其相關業',
        '1004001001': '銀行業',
        '1004001002': '信用合作社業',
        '1004001003': '農╱漁會信用部',
        '1004001004': '信託投資業',
        '1004001005': '郵政儲金匯兌業',
        '1004001006': '其他金融及輔助業',
        '1004001007': '金融控股業',
        '1004002000': '投資理財相關業',
        '1004002001': '創投業',
        '1004002002': '證券及期貨業',
        '1004002003': '其他投資理財相關業',
        '1004003000': '保險業',
        '1004003001': '人身保險業',
        '1004003002': '產物保險業',
        '1004003003': '社會保險業',
        '1004003004': '保險輔助業',
        '1004003005': '其他保險業',
        '1008000000': '法律╱會計╱顧問╱研發╱設計業',
        '1008001000': '法律服務業',
        '1008001001': '法律服務業',
        '1008002000': '會計服務業',
        '1008002001': '會計服務業',
        '1008003000': '顧問╱研發╱設計業',
        '1008003001': '工商顧問服務業',
        '1008003002': '檢測技術服務',
        '1008003003': '自然科學研發業',
        '1008003004': '生化科技研發業',
        '1008003005': '社會╱人文科學研發業',
        '1008003006': '其他專業╱科學及技術業',
        '1008003007': '專門設計相關業',
        '1011000000': '建築營造及不動產相關業',
        '1011001000': '建築或土木工程業',
        '1011001001': '土木工程業',
        '1011001002': '建築工程業',
        '1011001003': '其他營造業',
        '1011001004': '管線╱管道工程相關業',
        '1011002000': '建物裝修或空調工程業',
        '1011002001': '空調水機電工程業',
        '1011002002': '建物裝修及裝潢業',
        '1011003000': '建築規劃及設計業',
        '1011003001': '建築及工程技術服務業',
        '1011003002': '室內設計業',
        '1011003003': '建築設計業',
        '1011003004': '景觀設計業',
        '1011003005': '舞台架設及視聽工程業',
        '1011004000': '不動產業',
        '1011004001': '不動產經營業',
        '1011004002': '其他不動產業',
        '1012000000': '醫療保健及環境衛生業',
        '1012001000': '醫療服務業',
        '1012001001': '醫院',
        '1012001002': '診所',
        '1012001003': '動物醫院',
        '1012001004': '其他醫療保健服務業',
        '1012002000': '環境衛生相關業',
        '1012002001': '環境衛生及污染防治服務業',
        '1015000000': '礦業及土石採取業',
        '1015001000': '能源開採業',
        '1015001001': '石油╱天然氣及地熱礦業',
        '1015001002': '煤礦開採業',
        '1015002000': '其他礦業',
        '1015002001': '金屬礦業',
        '1015002002': '非金屬礦業',
        '1015003000': '土石採取業',
        '1015003001': '陸上土石採取業',
        '1015003002': '河海砂礫採取業',
        '1015003003': '其他土石採取業',
        '1016000000': '住宿╱餐飲服務業',
        '1016001000': '住宿服務業',
        '1016001001': '旅館業',
        '1016001002': '其他住宿服務業',
        '1016002000': '餐飲業',
        '1016002001': '餐館業',
        '1016002002': '飲料店業',
        '1016002003': '其他餐飲業'},

}