from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.chrome_executable_path = "C:/Users/USER/Desktop/chromedriver-win64/chromedriver-win64/chromedriver.exe"

driver = webdriver.Chrome(options=options)

driver.get("https://www.cmoney.tw/identity/account/login")

#帳密登陸
usernameInput = driver.find_element(By.ID, "Account")
passwordInput = driver.find_element(By.ID, "Password")
usernameInput.send_keys("0908056599")
passwordInput.send_keys("Considermail2000123456789abcd1234")

signinButton = driver.find_element(By.ID, "Login")
signinButton.send_keys(Keys.ENTER)

time.sleep(2)

# 雙重認證不啟用
check_url = "https://www.cmoney.tw/identity/account/login/two-factor-options?"
try:
    #driver.current_url == check_url:
    skipClick = driver.find_element(By.CLASS_NAME, "formlabel")  # 找到 class 為 formlabel 的元素
    skipButton = driver.find_element(By.ID, "btn btn-pure")
    skipClick.click()
    skipButton.send_keys(Keys.ENTER)
    time.sleep(1)

except:
    pass
    print("nanaan")

driver.get("https://www.cmoney.tw/vt/main-page.aspx")

# 帳號選擇
choose_url = "https://www.cmoney.tw/identity/account/select?"

try:
    accountchoose = driver.find_element(By.XPATH, '//*[@id="DXrqIV6nPnuu0El0ioCxvzb20ZSAZ7imfbpN1So1Oag"]/div/div[1]/div/div[1]')
    accountchoose.click()

    driver.get("https://www.cmoney.tw/vt/main-page.aspx")

except:
    pass 
    print("mammmmmaaa")

#不閃退
options = webdriver.ChromeOptions()
options.add_argument('C:/Users/USER/Downloads/chromedriver-win64/chromedriver.exe')
options.add_argument('disable-infobars')
options.add_experimental_option('detach', True)

driver = webdriver.Chrome(options=options)

driver.get("https://www.cmoney.tw/identity/account/login") 


#輸入股票代碼
textBoxCommkeyInput = driver.find_element(By.ID, "textBoxCommkey")
textBoxCommkeyInput.send_keys("2330")
textBoxCommkeyInput.send_keys(Keys.ENTER)

#現股
cashClick = driver.find_element(By.XPATH, '//*[@id="AccountOrderSelect"]/ul/li[1]/a')
cashClick.click()

#選擇買或賣
Bs_BClick= driver.find_element(By.ID, "Bs_B")
Bs_BClick.click()

Bs_SClick= driver.find_element(By.ID, "Bs_S")
Bs_SClick.click()

#幾張
TextBoxQtyInput = driver.find_element(By.ID, "TextBoxQty")
TextBoxQtyInput.send_keys("3")

#買賣
OrderbtnClick = driver.find_element(By.ID, "Orderbtn")
OrderbtnClick.click()

#________________這是一個很長的分隔島________我來到一個島 他叫超級分隔島_________________________



