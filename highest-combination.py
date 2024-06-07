import os
import openpyxl
import urllib.request
import pandas as pd
import json
import pandas as pd

os.chdir("C:/Users/BUBU/Downloads")  # Colab 換路徑使用
wb = openpyxl.load_workbook('專題.xlsx', data_only=True)  # 設定 data_only=True 只讀取計算後的數值
s1 = wb['以投報率排序']

a = 3661
rsiub = 80
rsidb = 20
ddub = 60
dddb = 40
jjub = 90
jjdb = 10
bollub = 0.2
bolldb = 0.2
kdub = 80
kddb = 20

za = -1
zb = -1
zc = -1
zd = -1
ze = -1
zf = -1
rate = 0

fields = None
data_record = []
open_day = []

for year in range(2023, 2024):  
    for month in range(10, 13):   
        date_str = f"{year}{month:02d}01"
        url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=" + date_str + "&stockNo=" + str(a)
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE"}
        
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        req_data = json.loads(response.read())
        
        # 檢查是否存在資料鍵
        if 'data' in req_data:
            # 將資料加入 data_record
            data_record.extend(req_data['data'])
            # 計算每個月的開盤天數
            open_day.append(len(req_data['data']))
        else:
            print(f"No data available for {date_str}", end='')
            
for year in range(2024, 2025):  
    for month in range(1, 5):   
        # 計算日期字串
        date_str = f"{year}{month:02d}01"
        url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=" + date_str + "&stockNo=" + str(a)
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE"}
        
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        req_data = json.loads(response.read())
        
        # 檢查是否存在資料鍵
        if 'data' in req_data:
            # 將資料加入 data_record
            data_record.extend(req_data['data'])
            # 計算每個月的開盤天數
            open_day.append(len(req_data['data']))
        else:
            print(f"\nNo data available for {date_str}")


df = pd.DataFrame(data_record,columns=fields) # 0日期 1成交股數 2成交金額 3開盤價 4最高價 5最低價 6收盤價 7漲跌價差 8成交筆數

df.set_index(0, inplace=True)
pd.set_option('display.max_columns',1000)
pd.set_option('display.width',1000)
pd.set_option('display.max_colwidth',1000)
pd.set_option('display.unicode.ambiguous_as_wide',True)
pd.set_option('display.unicode.east_asian_width',True)

def clean_value(value):
    if value == '--':  # 如果是"--"，直接返回 None
        return None
    return value

df = df.map(clean_value)

df = df.dropna()

df['開盤價']=df[3].str.replace(',', '').astype(float)
df['最低價']=df[5].str.replace(',', '').astype(float)
df['最高價']=df[4].str.replace(',', '').astype(float)
df['收盤價']=df[6].str.replace(',', '').astype(float)

analyze_df = pd.DataFrame()

#_______________________________________________________________________________________________________

# RSI
# 每日漲跌幅度
analyze_df['漲跌'] = df['收盤價'].diff()

# 14天內的平均漲幅和跌幅
l = 14
analyze_df['平均UP'] = analyze_df['漲跌'].apply(lambda x: x if x > 0 else 0).rolling(l).mean()
analyze_df['平均DN'] = analyze_df['漲跌'].apply(lambda x: -x if x < 0 else 0).rolling(l).mean()

# 相對強弱（RS）
analyze_df['RS'] = analyze_df['平均UP'] / analyze_df['平均DN']

# RSI
analyze_df['RSI'] = 100 - (100 / (1 + analyze_df['RS']))


#boll
# 中軌（20日均線）
analyze_df['中軌'] = df['收盤價'].rolling(window=20).mean()

# 標準差
std = df['收盤價'].rolling(window=20).std()

analyze_df['上軌'] = analyze_df['中軌'] + 2 * std
analyze_df['下軌'] = analyze_df['中軌'] - 2 * std
analyze_df['帶寬'] = (analyze_df['上軌'] - analyze_df['下軌']) / analyze_df['中軌']


# KDJ
analyze_df['RSV'] = (df['收盤價'] - df['最低價']) / (df['最高價'] - df['最低價']) * 100

k_values = [50]  # 初始K值 取50
d_values = [50]  # 初始D值

for i in range(1, len(df)):
    k = (2 / 3) * k_values[-1] + (1 / 3) * analyze_df['RSV'].iloc[i]
    k_values.append(k)
    d = (2 / 3) * d_values[-1] + (1 / 3) * k
    d_values.append(d)

analyze_df['K值'] = k_values
analyze_df['D值'] = d_values
analyze_df['J值'] = 3 * analyze_df['K值'] - 2 * analyze_df['D值']


#MACD
short_window = 12
long_window = 26
signal_window = 9

analyze_df['ShortEMA'] = df['收盤價'].ewm(span=short_window, adjust=False).mean()
analyze_df['LongEMA'] = df['收盤價'].ewm(span=long_window, adjust=False).mean()
analyze_df['Fast'] = analyze_df['ShortEMA'] - analyze_df['LongEMA']
analyze_df['Slow'] = analyze_df['Fast'].ewm(span=signal_window, adjust=False).mean()

for a in range(0,2): #RSI有無
    
    for b in range(0,2): #D值

        for c in range(0,2): #J

            for d in range(0,2): #Boll

                for e in range(0,2): #MACD

                    for f in range(0,2): #KD
                        
                        own_stock = 0
                        own_money = 100000
                        
                        for i in range(22,140):
                            
                            rsi = analyze_df.iloc[i]["RSI"]
                            tj = analyze_df.iloc[i]["J值"]
                            yj = analyze_df.iloc[i-1]["J值"]
                            td = analyze_df.iloc[i]["D值"]
                            yd = analyze_df.iloc[i-1]["D值"]
                            tk = analyze_df.iloc[i]["K值"]
                            yk = analyze_df.iloc[i-1]["K值"]
                            tf = analyze_df.iloc[i]["Fast"]
                            yf = analyze_df.iloc[i-1]["Fast"]
                            ts = analyze_df.iloc[i]["Slow"]
                            ys = analyze_df.iloc[i-1]["Slow"]
                            cu = analyze_df.iloc[i]["上軌"] - df.iloc[i]["收盤價"] #u-c
                            cd = df.iloc[i]["收盤價"] - analyze_df.iloc[i]["下軌"] #c-d
                            price = df.iloc[i]['開盤價']
                            
                            if a == 0:
                                if rsi >= rsiub:
                                    own_stock -= 1
                                    own_money += price
                                elif rsi <= rsidb:
                                    own_stock += 1
                                    own_money -= price
                                else:
                                    pass
                            else:
                                pass

                            if b == 0:
                                if td >= ddub:
                                    own_stock -= 1
                                    own_money += price
                                elif td <= dddb:
                                    own_stock += 1
                                    own_money -= price
                                else:
                                    pass
                            else:
                                pass

                            if c == 0:
                                if yj >= jjub and tj < yj:
                                    own_stock -= 1
                                    own_money += price
                                elif yj <= jjdb and tj > yj:
                                    own_stock += 1
                                    own_money -= price
                                else:
                                    pass
                            else:
                                pass

                            if d == 0:
                                if cu >= bollub:
                                    own_stock -= 1
                                    own_money += price
                                elif cd <= bolldb:
                                    own_stock += 1
                                    own_money -= price
                                else:
                                    pass
                            else:
                                pass

                            if e == 0:
                                if tf > ts and yf <= ys:
                                    own_stock -= 1
                                    own_money += price
                                elif tf < ts and yf >= ys:
                                    own_stock += 1
                                    own_money -= price
                                else:
                                    pass
                            else:
                                pass

                            if f == 0:
                                if td > tk and td >= kdub:
                                    own_stock -= 1
                                    own_money += price
                                elif td < tk and tk <= kddb:
                                    own_stock += 1
                                    own_money -= price
                                else:
                                    pass
                            else:
                                pass

                        new_rate = ((own_stock * price) + own_money)/2000000
                        #print(a,b,c,d,e,f,":",new_rate)
                        
                        if new_rate > rate:
                            rate = new_rate
                            za = a
                            zb = b
                            zc = c
                            zd = d
                            ze = e
                            zf = f

print(za,zb,zc,zd,ze,zf,rate)
