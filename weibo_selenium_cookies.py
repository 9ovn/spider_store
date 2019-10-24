import time
from selenium import webdriver
import redis


URL = 'https://passport.weibo.cn/signin/login'

class Weibo_selenium_login:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome()

    def cookie(self,cookie):
        cookies = {}
        for cook in cookie:
            cookies[cook['name']] = cook['value']
        return cookies


    def login(self):
        self.driver.implicitly_wait(3)
        self.driver.get(URL)
        username = self.driver.find_element_by_id('loginName')
        password = self.driver.find_element_by_id('loginPassword')
        button = self.driver.find_element_by_id('loginAction')
        username.send_keys(self.username)
        password.send_keys(self.password)
        button.click()
        time.sleep(2)
        if not self.driver.find_element_by_class_name('geetest_radar_tip_content'):
            raw_cookie = self.driver.get_cookies()
            cookies = self.cookie(raw_cookie)
            self.driver.close()
            return cookies
        else:
            button = self.driver.find_element_by_class_name('geetest_radar_tip_content')
            button.click()
            time.sleep(5)
            raw_cookie = self.driver.get_cookies()
            cookies = self.cookie(raw_cookie)
            self.driver.close()
            return cookies
        
def cookies_insert(cookies):
    Conn = redis.Redis('你的IP', '你的端口')
    conn.sadd('cookies', cookies)
        
if __name__ == '__main__':
    c = Weibo_selenium_login('16566743551', '5yiircm3')
    cookis = c.login()
    cookies_insert(cookies)
   
        












