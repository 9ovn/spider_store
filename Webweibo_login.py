import requests
from lxml import etree
from urllib import parse
from time import time
import json
import re
import rsa
import binascii
import base64
import os


# mongodb的链接
# CONN = MongoClient(ip, ports)
# SESSION
SESSION = requests.session()
# 保存
COOKIES_FILE_PATH = 'Web_weibo_cookies.json'


class WeiBoLogin:
    """
    网页版cookies获取
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.pre_login_url = 'https://login.sina.com.cn/sso/prelogin.php'
        self.login_url = 'https://login.sina.com.cn/sso/login.php'
        self.profile_url = 'http://my.sina.com.cn/'

    def pre_login(self):
        # 首先对username进行url.quote并编译成utf-8格式的，之后用base64进行编译(同utf-8格式的)
        su = base64.b64encode(parse.quote(self.username).encode('utf-8')).decode('utf-8')
        pre_login = {
            'entry': 'sso',
            'callback': 'sinaSSOController.preloginCallBack',
            'su': su,
            'rsakt': 'mod',
            'client': 'ssologin.js(v1.4.15)',
            '_': int(time()*1000)
        }

        try:
            # 登录pre_login网址以便获得rsakv，pubkv，servertime， servertime
            reponse = SESSION.get(self.pre_login_url, params=pre_login)
            reponse.raise_for_status()
            reponse_json = re.findall(r'\((.*?)\)', reponse.text)[0]
            reponse_dict = json.loads(reponse_json)
            # 将获得json格式中的目标数据提取出来
            servertime = reponse_dict['servertime']
            nonce = reponse_dict['servertime']
            pubkey = reponse_dict['pubkey']
            rsakv = reponse_dict['rsakv']

            return su, servertime, nonce, pubkey, rsakv
        except Exception as ERR:
            raise ERR

    def encry_password(self, pubkey, nonce, servertime):
        """
        对password进行rsa加密。
        """
        public_key = int(pubkey, 16)
        key = rsa.PublicKey(public_key, int("10001", 16))
        message = str(servertime) + '\t' + str(nonce) + '\n' + self.password
        encrypt_message = rsa.encrypt(message.encode('utf-8'), key)
        sp = binascii.b2a_hex(encrypt_message).decode('utf-8')
        return sp

    def login(self):

        # if self.load_cookies():
        #     return t

        # 登录headers
        login_params = {
            'client': 'ssologin.js(v1.4.15)',
            '_': int(time()*1000)
        }

        # 给登录要用的form_data各个参数赋值，这里调用了pre_login()函数
        su, servertime, nonce, pubkey, rsakv = self.pre_login()
        # 给密码进行rsa加密，调用encry_password()
        sp = self.encry_password(pubkey, nonce, servertime)

        # 构造form_data
        login_data = {
            'entry': "account",
            'gateway': "1",
            'from': "null",
            'savestate': "30",
            'useticket': "0",
            'vsnf': "1",
            'su': su,
            'service': "account",
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': "rsa2",
            'rsakv': rsakv,
            'sp': sp,
            'sr': "1536*864",
            'encoding': "UTF-8",
            'cdult': "3",
            'domain': "sina.com.cn",
            'prelt': "170",
            'returntype': "TEXT"
        }
        try:
            # 进行登录
            response = SESSION.post(self.login_url, params=login_params, data=login_data)
        except Exception as ERR:
            print(ERR)
        
        # 将返回的dict格式的数据转化成json并去除crossDomainUrlList里的第一个链接，进行跳转补全cookies
        tar_json = json.loads(response.text)
        url = tar_json['crossDomainUrlList'][0]
        if url:
            SESSION.get(url)
            print('登录成功正在跳转')
        
        # 验证是否登录成功
        return self.check_status() 
        
    def check_status(self):
        headers = {
            'Referer': 'http://my.sina.com.cn/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36'
        }
        try:
            response = SESSION.get(url=self.profile_url, headers=headers)
            tree = etree.HTML(response.content.decode('utf-8'))
            user_name = tree.xpath(r'//p[@class="me_name"]/text()')[0]
            cookies_dict = requests.utils.dict_from_cookiejar(SESSION.cookies)

            # self.weibo_comment()
            
            if user_name:
                print(f'欢迎尊贵的用户：{user_name}')
                print(SESSION.cookies)
                return SESSION.cookies

            else:
                print(response.raise_for_status())
        except Exception as ERR:
            raise ERR

    def cookies_write(self, data):
        """
        不完善
        """
        cookies_dict = requests.utils.dict_from_cookiejar(SESSION.cookies)
        with open(COOKIES_FILE_PATH, 'w+', encoding='utf-8') as file:
            json.dump(cookies_dict, file)
            print('保存cookies文件成功！文件名: %s' % COOKIES_FILE_PATH)





if __name__ == "__main__":
    c = WeiBoLogin('a87762968@qq.com', 'woninima111')
    SESSION.cookies = c.login()
    # print(SESSION.cookies)

