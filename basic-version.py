#!/usr/bin/env python
# coding: utf-8

# In[2]:


get_ipython().system('jupyter nbconvert --to final_code.ipynb')


# In[3]:


from dateutil import rrule
import urllib.request
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import pandas as pd
import numpy as np
import json
import time
import ssl
import datetime
import matplotlib

a = int(input("股票代碼:"))
n = int(input("請輸入期限(天數):"))

today = datetime.datetime.now()
point = datetime.datetime.now().date() + datetime.timedelta(days=-n)

print("計算日期:", point.strftime("%Y-%m-%d"))

stock = str(a)
begin_date = point.strftime("%Y-%m-%d")

get_ipython().run_line_magic('matplotlib', 'inline')


# In[4]:


# 爬取每月股價的目標網站並包裝成函式
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


# In[5]:


def craw_stock(stock_number, start_month):
    b_month = datetime.date(*[int(x) for x in start_month.split('-')])
    now = datetime.datetime.now().strftime("%Y-%m-%d")         
    e_month = datetime.date(*[int(x) for x in now.split('-')])
    
    result = pd.DataFrame()
    for dt in rrule.rrule(rrule.MONTHLY, dtstart=b_month, until=e_month):
        result = pd.concat([result,craw_one_month(stock_number,dt)],ignore_index=True)
        time.sleep(2000.0/1000.0)
    
    return result

df = craw_stock(stock, begin_date)
df.set_index('日期',inplace=True)
df['日期'] = df.index
pd.set_option('display.max_columns',1000)
pd.set_option('display.width',1000)
pd.set_option('display.max_colwidth',1000)
pd.set_option('display.unicode.ambiguous_as_wide',True)
pd.set_option('display.unicode.east_asian_width',True)

df_without_date = df.drop(columns=['日期'])
if n <= 60: print(df_without_date)


# In[6]:


# alpha=0.3 透明度

df['收盤價']=df['收盤價'].astype(float)
df.loc[:]['收盤價'].plot(figsize=(14, 6))

df['開盤價']=df['開盤價'].astype(float)
df.loc[:]['開盤價'].plot(figsize=(14, 6))

df['最低價']=df['最低價'].astype(float)
df.loc[:]['最低價'].plot(figsize=(14, 6))

df['最高價']=df['最高價'].astype(float)
df.loc[:]['最高價'].plot(figsize=(14, 6))

plt.xlabel('date')
plt.ylabel('stock (basic factor)')
plt.legend(loc = 'lower left')
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.grid(True)
plt.show()


# In[7]:


# 创建蜡烛图
fig, ax = plt.subplots(figsize=(14, 6))
x_ticks = range(0, len(df), 5)  # 每隔5个数据点显示一个标签
plt.xticks(x_ticks, df['日期'][x_ticks], rotation=20)

ax.xaxis_date()  # 设置X轴为日期格式

# 绘制蜡烛图
for i, df_row in df.iterrows():
    date = df_row['日期']
    open_price = df_row['開盤價']
    high = df_row['最高價']
    low = df_row['最低價']
    close = df_row['收盤價']

    if close > open_price:
        color = 'g'  # 上涨日绿色
    else:
        color = 'r'  # 下跌日红色

    ax.plot([df_row['日期'], df_row['日期']], [df_row['最低價'], df_row['最高價']], color=color, linewidth=2)
    ax.plot([df_row['日期'], df_row['日期']], [df_row['開盤價'], df_row['收盤價']], color=color, linewidth=10)

# 设置标题和标签
ax.set_xlabel("Date")
ax.set_ylabel("Price")
plt.grid(True)
plt.show()


# In[8]:


#RSI

收盤價列 = df['收盤價']

平均收盤價 = 收盤價列.mean()
print("平均收盤價:", 平均收盤價)

最大收盤價 = 收盤價列.max()
最小收盤價 = 收盤價列.min()
收盤價標準差 = 收盤價列.std()

print("最大收盤價:", 最大收盤價)
print("最小收盤價:", 最小收盤價)
print("收盤價標準差:", 收盤價標準差)


# 計算每日漲跌幅度
df['漲跌'] = df['收盤價'].diff()

# 計算14天內的平均漲幅和跌幅
l = 14
df['平均UP'] = df['漲跌'].apply(lambda x: x if x > 0 else 0).rolling(l).mean()
df['平均DN'] = df['漲跌'].apply(lambda x: -x if x < 0 else 0).rolling(l).mean()

# 計算相對強弱（RS）
df['RS'] = df['平均UP'] / df['平均DN']
# 計算RSI
df['RSI'] = 100 - (100 / (1 + df['RS']))

# 列印包含RSI的DataFrame

if n<=60: print(df[['收盤價','漲跌','平均UP','平均DN','RS','RSI']])


# In[9]:


# 创建图表和子图
fig, ax1 = plt.subplots(figsize=(14, 6))
x_ticks = np.arange(0, len(df), 5)
plt.xticks(x_ticks, df.index[x_ticks], rotation=25)

# 绘制第一组数据在第一个Y轴
ax1.plot(df['日期'], df['收盤價'], 'g')
ax1.set_xlabel('date')
ax1.set_ylabel('stock(close)', color='g')
ax1.tick_params('y', colors='g')

# 创建第二个Y轴
ax2 = ax1.twinx()
ax2.plot(df['日期'], df['RSI'], 'b')
ax2.set_ylabel('RSI', color='b')
ax2.tick_params('y', colors='b')
plt.grid(True)
plt.show()


# In[10]:


#boll

# 計算布林通道的中軌（20日均線）
df['中軌'] = df['收盤價'].rolling(window=20).mean()

# 計算布林通道的標準差
std = df['收盤價'].rolling(window=20).std()

# 計算布林通道的上軌（20日均線 + 2倍標準差）
df['上軌'] = df['中軌'] + 2 * std

# 計算布林通道的下軌（20日均線 - 2倍標準差）
df['下軌'] = df['中軌'] - 2 * std

# 計算布林通道的帶寬（通道空間）
df['帶寬'] = (df['上軌'] - df['下軌']) / df['中軌']

# 打印包含布林通道數據的DataFrame
if n <= 60: print(df[['上軌','中軌','下軌','帶寬']])


# In[11]:


df['上軌']=df['上軌'].astype(float)
df.loc[:]['上軌'].plot(figsize=(14, 6))

df['中軌']=df['中軌'].astype(float)
df.loc[:]['中軌'].plot(figsize=(14, 6))

df['下軌']=df['下軌'].astype(float)
df.loc[:]['下軌'].plot(figsize=(14, 6))

df['收盤價']=df['收盤價'].astype(float)
df.loc[:]['收盤價'].plot(figsize=(14, 6))

plt.xlabel('date')
plt.ylabel('Boll')
plt.legend(loc = 'lower left')
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.grid(True)
plt.show()


# In[12]:


# 创建蜡烛图
fig, ax = plt.subplots(figsize=(14, 6))
x_ticks = range(0, len(df), 5)  # 每隔5个数据点显示一个标签
plt.xticks(x_ticks, df['日期'][x_ticks], rotation=20)

ax.xaxis_date()  # 设置X轴为日期格式

# 绘制蜡烛图
for i, df_row in df.iterrows():
    date = df_row['日期']
    open_price = df_row['開盤價']
    high = df_row['最高價']
    low = df_row['最低價']
    close = df_row['收盤價']

    if close > open_price:
        color = 'g'  # 上涨日绿色
    else:
        color = 'r'  # 下跌日红色

    ax.plot([df_row['日期'], df_row['日期']], [df_row['最低價'], df_row['最高價']], color=color, linewidth=2)
    ax.plot([df_row['日期'], df_row['日期']], [df_row['開盤價'], df_row['收盤價']], color=color, linewidth=10)

df['上軌']=df['上軌'].astype(float)
df.loc[:]['上軌'].plot(figsize=(14, 6), color='r')

df['中軌']=df['中軌'].astype(float)
df.loc[:]['中軌'].plot(figsize=(14, 6), color='y')

df['下軌']=df['下軌'].astype(float)
df.loc[:]['下軌'].plot(figsize=(14, 6), color='b')

    
# 设置标题和标签
ax.set_xlabel("Date")
ax.set_ylabel("Price")
plt.grid(True)
plt.show()


# In[13]:


# KDJ

df['最高價n'] = df['最高價'].rolling(window=n).max()
df['最低價n'] = df['最低價'].rolling(window=n).min()
df['RSV'] = (df['收盤價'] - df['最低價']) / (df['最高價'] - df['最低價']) * 100

# 計算K值、D值和J值
k_values = [50]  # 初始K值，一般取50
d_values = [50]  # 初始D值

for i in range(1, len(df)):
    k = (2 / 3) * k_values[-1] + (1 / 3) * df['RSV'][i]
    k_values.append(k)
    d = (2 / 3) * d_values[-1] + (1 / 3) * k
    d_values.append(d)

df['K值'] = k_values
df['D值'] = d_values
df['J值'] = 3 * df['K值'] - 2 * df['D值']

# 打印包含KDJ指標的df
if n <= 60: print(df[['K值','D值','J值']])


# In[14]:


df['K值']=df['K值'].astype(float)
df.loc[:]['K值'].plot(figsize=(14, 6), color='b')

df['D值']=df['D值'].astype(float)
df.loc[:]['D值'].plot(figsize=(14, 6), color='g')

df['J值']=df['J值'].astype(float)
df.loc[:]['J值'].plot(figsize=(14, 6), color='purple')

plt.xlabel('date')
plt.ylabel('KDJ')
plt.legend(loc = 'lower left')
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.grid(True)
plt.show()


# In[15]:


#MACD

short_window = 12
long_window = 26
signal_window = 9

df['ShortEMA'] = df['收盤價'].ewm(span=short_window, adjust=False).mean()
df['LongEMA'] = df['收盤價'].ewm(span=long_window, adjust=False).mean()
df['Fast'] = df['ShortEMA'] - df['LongEMA']
df['Slow'] = df['Fast'].ewm(span=signal_window, adjust=False).mean()

if n <= 60: print(df[['ShortEMA','LongEMA','Fast','Slow']])


# In[16]:


df['Fast']=df['Fast'].astype(float)
df.loc[:]['Fast'].plot(figsize=(14, 6))

df['Slow']=df['Slow'].astype(float)
df.loc[:]['Slow'].plot(figsize=(14, 6))

plt.xlabel('date')
plt.ylabel('MACD')
plt.legend(loc = 'lower left')
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.grid(True)
plt.show()


# In[18]:


df_wt = df.drop(columns=['日期','成交股數','成交金額','開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數', '最高價n', '最低價n', '帶寬'])
print(df_wt.columns)

n1 = str(input("你想觀察的第一條線："))
n2 = str(input("你想觀察的第二條線："))

# 创建蜡烛图
fig, ax = plt.subplots(figsize=(14, 6))
x_ticks = range(0, len(df), 5)
plt.xticks(x_ticks, df['日期'][x_ticks], rotation=20)
ax.xaxis_date()

# 绘制蜡烛图
for i, df_row in df.iterrows():
    date = df_row['日期']
    open_price = df_row['開盤價']
    high = df_row['最高價']
    low = df_row['最低價']
    close = df_row['收盤價']

    if close > open_price:
        color = 'g'
    else:
        color = 'r'

    ax.plot([date, date], [low, high], color=color, linewidth=2)
    ax.plot([date, date], [open_price, close], color=color, linewidth=10)

plt.grid(True)
    
# 创建底部附图框，分别设置两个 Y 轴的颜色
bottom_ax = ax.inset_axes([0, -0.4, 1, 0.4])  # 调整底部副图的位置和大小
bottom_ax.yaxis.label.set_color('b')  # 第一个 Y 轴的颜色为蓝色
bottom_ax.tick_params(axis='y', colors='b')  # 设置第一个 Y 轴刻度线的颜色为蓝色

right_bottom_ax = bottom_ax.twinx()
right_bottom_ax.yaxis.label.set_color('orange')  # 第二个 Y 轴的颜色为红色
right_bottom_ax.tick_params(axis='y', colors='orange')  # 设置第二个 Y 轴刻度线的颜色为红色

# 绘制副图的线
x = df['日期']
y1 = df[n1]  # 第一个副图数据列
y2 = df[n2]  # 第二个副图数据列

bottom_ax.plot(x, y1, color='b', label='n1')
right_bottom_ax.plot(x, y2, color='orange', label='n2')

# 设置标题和标签
ax.set_xlabel("")  # 清除主图的 x 轴标签
ax.set_ylabel("Price")
bottom_ax.set_xlabel("Date")
bottom_ax.set_ylabel(n1)  # 第一个副图 Y 轴标签
right_bottom_ax.set_ylabel(n2)  # 第二个副图 Y 轴标签

# 控制底部附图的 x 轴坐标数量
x_ticks_bottom = range(0, len(df), 5)  # 例如，每隔10个数据点显示一个坐标
bottom_ax.set_xticks(x_ticks_bottom)

bottom_ax.set_xticklabels(df['日期'][x_ticks_bottom], rotation=20)

plt.show()
print("*n1(第一條線)為藍色 n2(第二條線)為綠色")


# In[19]:


rsi = pd.DataFrame(df['RSI'], index=df['日期'])

close = pd.DataFrame(df['收盤價'], index=df['日期'])
up = pd.DataFrame(df['上軌'], index=df['日期'])
md = pd.DataFrame(df['中軌'], index=df['日期'])
dn = pd.DataFrame(df['下軌'], index=df['日期'])

kk = pd.DataFrame(df['K值'], index=df['日期'])
dd = pd.DataFrame(df['D值'], index=df['日期'])
jj = pd.DataFrame(df['J值'], index=df['日期'])


c = close.loc[date, '收盤價']
r = rsi.loc[date, 'RSI']
u = up.loc[date, '上軌']
m = md.loc[date, '中軌']
d = dn.loc[date, '下軌']
kkk = kk.loc[date, 'K值']
ddd = dd.loc[date, 'D值']
jjj = jj.loc[date, 'J值']


# In[20]:


#RSI 
if r >= 65 :
    print("sell RSI")
elif r <= 35 :
    print("buy RSI")
else :
    print("na RSI")
    
#boll-----------------------------------
cu = u-c
cd = c-d
if c >= m :
    print("上半", end=' ')
    if cu <= -0.1 :
        print("sell Boll")
    else :
        print("na Boll")
elif c <= m :
    print("下半",end=' ')
    if cd <=0.2 :
        print("buy Boll")
    else :
        print("na Boll")
        
#MACD------------------------------------
tf = df['Fast'].iloc[-1]
yf = df['Fast'].iloc[-2]
ts = df['Slow'].iloc[-1]  
ys = df['Slow'].iloc[-2]

if tf==ts :
    if yf < ys:
        print("buy MACD")
    elif yf > ys:
        print("sell MACD")
else :
    print("na MACD")
    
#KDJ------------------------------------

td = df['D值'].iloc[-1]
yd = df['D值'].iloc[-2]
tk = df['K值'].iloc[-1]
yk = df['K值'].iloc[-2]
j1 = df['J值'].iloc[-1]
j2 = df['J值'].iloc[-2]
j3 = df['J值'].iloc[-3]
j4 = df['J值'].iloc[-4]


if td >= 65 :
    print("sell ddd")
elif td <= 35 :
    print("buy ddd")
else :
    print("na ddd")


if j1>=90 and j2>=90 and j3>=90 :
    print("sell jjj")
elif j1<=10 and j2<=10 and j3<=10 :
    print("buy jjj")
else :
    print("na jjj")
    

if td==tk and tk<=20:
    if yd > yk : 
        print("buy KD細交")
elif td==tk and td>=80:
    if yd < yk :
        print("sell KD細交")
else :
    print("na KD細交")

