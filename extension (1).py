from dateutil import rrule
import urllib.request
import datetime
import pandas as pd
import numpy as np
import json
import time
import ssl
import datetime
from collections import defaultdict

# 初始化一個字典來儲存每個組合的出現次數
combination_counts = defaultdict(int)


a = 2002 #股票代碼
n = 61 # 圖表觀察幾天 原設60
e = 214 # 從幾天前開始觀察
f = 1 # 實驗的第幾天
h = 0 # 現有股票
s = 2000000 # 初始資產

#count num
r0 = 0
m0 = 0
d0 = 0
j0 = 0
b0 = 0
x0 = 0

print("股票為:", a)
print("現有資產為", h, "張股票,", s, "元")
#print(n,e)
print('')

while f <= 360:

    today = datetime.datetime.now() + datetime.timedelta(days=-e)
    point = datetime.datetime.now().date() + datetime.timedelta(days=-e-n)
    
    stock = str(a)
    begin_date = point.strftime("%Y-%m-%d")
    strtoday = today.strftime("%Y-%m-%d")

    print("今天是:", strtoday, ",第", f,"天")

    e -= 1
    f += 1

    # 爬取每月股價的目標網站
    def craw_one_month(stock_number,date):
        url = (
            "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date="+
            date.strftime('%Y%m%d')+
            "&stockNo="+
            stock_number
        )
        headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE"}
        ssl._create_default_https_context = ssl._create_unverified_context
        req = urllib.request.Request(url, headers=headers)
        data = json.loads(urllib.request.urlopen(req).read())
        return pd.DataFrame(data['data'],columns=data['fields'])


    def craw_stock(stock_number, start_month):
        b_month = datetime.date(*[int(x) for x in start_month.split('-')])         
        e_month = datetime.date(*[int(x) for x in strtoday.split('-')])

        result = pd.DataFrame()
        for dt in rrule.rrule(rrule.MONTHLY, dtstart=b_month, until=e_month):
            result = pd.concat([result,craw_one_month(stock_number,dt)],ignore_index=True)
            time.sleep(2)
        
        return result


    df = craw_stock(stock, begin_date)
    df.set_index('日期',inplace=True)
    df['日期'] = df.index
    pd.set_option('display.max_columns',1000)
    pd.set_option('display.width',1000)
    pd.set_option('display.max_colwidth',1000)
    pd.set_option('display.unicode.ambiguous_as_wide',True)
    pd.set_option('display.unicode.east_asian_width',True)

    df['收盤價']=df['收盤價'].astype(float)
    df['開盤價']=df['開盤價'].astype(float)
    df['最低價']=df['最低價'].astype(float)
    df['最高價']=df['最高價'].astype(float)


    #RSI
    收盤價列 = df['收盤價']

    # 每日漲跌幅度
    df['漲跌'] = df['收盤價'].diff()

    # 14天內的平均漲幅和跌幅
    l = 14
    df['平均UP'] = df['漲跌'].apply(lambda x: x if x > 0 else 0).rolling(l).mean()
    df['平均DN'] = df['漲跌'].apply(lambda x: -x if x < 0 else 0).rolling(l).mean()

    # 相對強弱（RS）
    df['RS'] = df['平均UP'] / df['平均DN']
    # RSI
    df['RSI'] = 100 - (100 / (1 + df['RS']))


    #boll

    # 中軌（20日均線）
    df['中軌'] = df['收盤價'].rolling(window=20).mean()

    # 標準差
    std = df['收盤價'].rolling(window=20).std()

    df['上軌'] = df['中軌'] + 2 * std
    df['下軌'] = df['中軌'] - 2 * std
    df['帶寬'] = (df['上軌'] - df['下軌']) / df['中軌']


    for i, df_row in df.iterrows():
        date = df_row['日期']
        open_price = df_row['開盤價']
        high = df_row['最高價']
        low = df_row['最低價']
        close = df_row['收盤價']


    # KDJ

    df['最高價n'] = df['最高價'].rolling(window=n).max()
    df['最低價n'] = df['最低價'].rolling(window=n).min()
    df['RSV'] = (df['收盤價'] - df['最低價']) / (df['最高價'] - df['最低價']) * 100

    # 計算K值、D值和J值
    k_values = [50]  # 初始K值 取50
    d_values = [50]  # 初始D值

    for i in range(1, len(df)):
        k = (2 / 3) * k_values[-1] + (1 / 3) * df['RSV'].iloc[i]
        k_values.append(k)
        d = (2 / 3) * d_values[-1] + (1 / 3) * k
        d_values.append(d)

    df['K值'] = k_values
    df['D值'] = d_values
    df['J值'] = 3 * df['K值'] - 2 * df['D值']


    #MACD

    short_window = 12
    long_window = 26
    signal_window = 9

    df['ShortEMA'] = df['收盤價'].ewm(span=short_window, adjust=False).mean()
    df['LongEMA'] = df['收盤價'].ewm(span=long_window, adjust=False).mean()
    df['Fast'] = df['ShortEMA'] - df['LongEMA']
    df['Slow'] = df['Fast'].ewm(span=signal_window, adjust=False).mean()


    #爬資料

    min_year = today.year - 1911
    formatted_date = f"{min_year}/{today.strftime('%m/%d')}"

    matching_row = df.loc[df['日期'] == formatted_date]

    global c


     # 如果有匹配的行
    if not matching_row.empty:
        # 取得對應值的索引
        index_of_matching_row = matching_row.index[0]
        tf = df.loc[df['日期'] == formatted_date,'Fast'].values[0]
        ts = df.loc[df['日期'] == formatted_date,'Slow'].values[0]
        tk = df.loc[df['日期'] == formatted_date,'K值'].values[0]
        td = df.loc[df['日期'] == formatted_date,'D值'].values[0]
        j1 = df.loc[df['日期'] == formatted_date,'J值'].values[0]
        r = df.loc[df['日期'] == formatted_date,'RSI'].values[0]
        c = df.loc[df['日期'] == formatted_date,'收盤價'].values[0]
        u = df.loc[df['日期'] == formatted_date,'上軌'].values[0]
        m = df.loc[df['日期'] == formatted_date,'中軌'].values[0]
        d = df.loc[df['日期'] == formatted_date,'下軌'].values[0]
        en = df.loc[df['日期'] == formatted_date,'開盤價'].values[0]

        # 使用iloc方法取得上一行的值
        indices = np.where(df.values == tf)
        s_indices = np.where(df.values == ts)
        k_indices = np.where(df.values == tk)
        d_indices = np.where(df.values == td)
        j_indices = np.where(df.values == j1)

        if len(indices[0]) > 0:
            row_index= indices[0][0]
            col_f = indices[1][0]
            col_s = s_indices[1][0]
            col_k = k_indices[1][0]
            col_d = d_indices[1][0]
            col_j = j_indices[1][0]

            yf = df.iloc[row_index - 1, col_f]
            ys = df.iloc[row_index - 1, col_s]
            yd = df.iloc[row_index - 1, col_k]
            yk = df.iloc[row_index - 1, col_d]
            j2 = df.iloc[row_index - 1, col_j]
        
        tod = today.date()
        print("成交價：",en)

        arr = [0] * 7
        
        #RSI 
        if r >= 65 :
            arr[0] = 1
        elif r <= 35 :
            arr[0] = -1
            
        #boll-----------------------------------
        cu = u-c
        cd = c-d
        if c >= m :
            if cu <= -0.1 :
                arr[1] = 1

        elif c <= m :
            if cd <=0.2 :
                arr[1] = -1
                
        #MACD------------------------------------

        if yf < ys and tf >= ts:
            arr[2] = -1
        elif yf > ys and tf <= ts:
            arr[2] = 1
            
        #KDJ------------------------------------

        if td >= 65 :
            arr[3] = 1
        elif td <= 35 :
            arr[3] = -1

        if j1 >= 100 and j2 < j1:
            arr[4] = 1
        elif j1 <= 0 and j2 > j1:
            arr[4] = -1
            
        if td<=tk and tk<=20 and yd > yk : 
            arr[5] = -1
        elif td>=tk and td>=80 and yd < yk:
            arr[5] = 1


        # 整合判斷
        g = 0
        b = 0
        for i in range(0,6):
            if arr[i] == 1:
                g += 1
                
            elif arr[i] == -1:
                b += 1
        

        # 買賣紀錄
        if g >= 2 or b >= 2:
            print(tod,end = ' ')
            for i in range(0,6):
                if arr[i] == 1:
                    if i == 0: 
                        print("buy RSI",end = ' ')
                        r0 += 1
                    if i == 1: 
                        print("buy Boll",end = ' ')
                        b0 += 1
                    if i == 2: 
                        print("buy MACD",end = ' ')
                        m0 += 1
                    if i == 3: 
                        print("buy ddd",end = ' ')
                        d0 += 1
                    if i == 4: 
                        print("buy jjj",end = ' ')
                        j0 += 1
                    if i == 5: 
                        print("buy KD交叉",end = ' ')
                        x0 += 1
                
                elif arr[i] == -1:
                    if i == 0: 
                        print("sell RSI",end = ' ')
                        r0 += 1
                    if i == 1: 
                        print("sell Boll",end = ' ')
                        b0 += 1
                    if i == 2: 
                        print("sell MACD",end = ' ')
                        m0 += 1
                    if i == 3: 
                        print("sell ddd",end = ' ')
                        d0 += 1
                    if i == 4: 
                        print("sell jjj",end = ' ')
                        j0 += 1
                    if i == 5: 
                        print("sell KD交叉",end = ' ')
                        x0 += 1

            print("")

            if g >= 2:
                if g == 2:
                    if h >= 1:
                        print("sell 1")
                        h -= 1
                        s += 1000*en

                    else:
                        print("sorry you don't have enough stock to sell")

                elif g == 3:
                    if h >= 2:
                        print("sell 2")
                        h -= 2
                        s += 2000*en

                    else:
                        print("sorry you don't have enough stock to sell")

                elif g >= 4:
                    if h >= 3:
                        print("sell 3")
                        h -= 3
                        s += 3000*en

                    else:
                        print("sorry you don't have enough stock to sell")


            if b >= 2:
                if b == 2:
                    print("buy 1")
                    h += 1
                    s -= 1000*en

                elif b == 3:
                    print("buy 2")
                    h += 2
                    s -= 2000*en

                elif b >= 4:
                    print("buy 3")
                    h += 3
                    s -= 3000*en


        else:
            print("...")

        print("現有資產為", h, "張股票和", s, "元")

        current_combination = arr

        # 將組合轉為元組，以便作為字典的鍵
        current_combination_tuple = tuple(current_combination)

        # 將該組合的出現次數加一
        combination_counts[current_combination_tuple] += 1


    else:
        print("Today is weekend~")
        print("")
        pass


sum = 1000*h*c + s
rate = round(sum / 2000000.0,4)
print("賠率為",rate)
print("")
print("RSI:",r0," MACD:",m0," Boll:",b0," D value:",d0,"J value:",j0,"KDx:",x0)
print("")
# 輸出結果
for combination, count in combination_counts.items():
    print(f"{list(combination)} {count} times")

