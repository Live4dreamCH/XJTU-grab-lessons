from selenium import webdriver
from time import *

from selenium.webdriver.common.keys import Keys

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
# 构建一个chrome对象
driver = webdriver.Chrome(options=chrome_options)

# 打开百度
driver.get("http://www.baidu.com/")

# 定位输入框的位置
element = driver.find_element_by_id("kw")
# 清空原有的输入，输入python进行搜索
element.clear()
# 搜索栏输入"python"
element.send_keys("python")
# 模拟回车，执行搜索
element.send_keys(Keys.RETURN)

sleep(2)
# 浏览器截图
driver.get_screenshot_as_file("111.png")
sleep(2)
# 退出浏览
driver.quit()
