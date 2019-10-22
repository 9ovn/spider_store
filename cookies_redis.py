from time import time
from redis import Redis
import base64
import rsa
import binascii
import requests
import re
from PIL import Image
import random
from urllib.parse import quote_plus
import http.cookiejar as cookielib


__slot__ = ['WeiboLogin', 'Redis_Insert', 'set', 'get']


AGENT = 'mozilla/5.0 (windowS NT 10.0; win64; x64) appLewEbkit/537.36 (KHTML, likE gecko) chrome/71.0.3578.98 safari/537.36'
HEADERS = {'User-Agent': AGENT}





class WeiboLogin:
    """
    通过登录 weibo.com 然后跳转到 m.weibo.cn
    """
    #初始化数据
    def __init__(self, user, password, cookie_path):
        super(WeiboLogin, self).__init__()
        self.user = user
        self.password = password
        self.session = requests.Session()
        self.cookie_path = cookie_path
        self.session.cookies = cookielib.LWPCookieJar(filename=self.cookie_path)
        # 网页版微博的首页
        self.index_url = "http://weibo.com/login.php"
        # 先保证session位于首页
        self.session.get(self.index_url, headers=HEADERS, timeout=2)
        # 创建空集
        self.postdata = dict()

    def get_su(self):
        """
        对 email 地址和手机号码 先 javascript 中 encodeURIComponent
        对应 Python 3 中的是 urllib.parse.quote_plus
        然后在 base64 加密后decode
        """
        username_quote = quote_plus(self.user)
        username_base64 = base64.b64encode(username_quote.encode("utf-8"))
        # 获得通过base64加密的username
        return username_base64.decode("utf-8")

    # 预登陆获得 servertime, nonce, pubkey, rsakv
    def get_server_data(self, su):
        """与原来的相比，微博的登录从 v1.4.18 升级到了 v1.4.19
        这里使用了 URL 拼接的方式，也可以用 Params 参数传递的方式
        """

        pre_url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="
        # pre_url = "http://login.sina.com.cn/sso/prelogin.php"
        pre_url = pre_url + su + "&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_="
        pre_url = pre_url + str(int(time() * 1000))
        pre_data_res = self.session.get(pre_url, headers=HEADERS)
        sever_data = eval(pre_data_res.content.decode("utf-8").replace("sinaSSOController.preloginCallBack", ''))
        
        return sever_data

    def get_password(self, servertime, nonce, pubkey):
        """对密码进行 RSA 的加密"""
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 65537)  # 创建公钥
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(self.password)  # 拼接明文js加密文件中得到
        message = message.encode("utf-8")
        passwd = rsa.encrypt(message, key)  # 加密
        passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制。
        return passwd

    def get_cha(self, pcid):
        # 只是用来获取验证码
        """获取验证码，并且用PIL打开，
        1. 如果本机安装了图片查看软件，也可以用 os.subprocess 的打开验证码
        2. 可以改写此函数接入打码平台。
        """
        cha_url = "https://login.sina.com.cn/cgi/pin.php?r="
        cha_url = cha_url + str(int(random.random() * 100000000)) + "&s=0&p="
        cha_url = cha_url + pcid
        cha_page = self.session.get(cha_url, headers=HEADERS)
        with open("cha.jpg", 'wb') as f:
            f.write(cha_page.content)
            f.close()
        try:
            im = Image.open("cha.jpg")
            im.show()
            im.close()
        except Exception as e:
            print(u"请到当前目录下，找到验证码后输入")

    def pre_login(self):
        # su 是加密后的用户名
        su = self.get_su()
        sever_data = self.get_server_data(su)
        #  获取su, servertime, nonce, pubkey, rsakv
        servertime = sever_data["servertime"]
        nonce = sever_data['nonce']
        rsakv = sever_data["rsakv"]
        pubkey = sever_data["pubkey"]
        showpin = sever_data["showpin"]  # 这个参数的意义待探索
        password_secret = self.get_password(servertime, nonce, pubkey)

        self.postdata = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'useticket': '1',
            'pagerefer': "https://passport.weibo.com",
            'vsnf': '1',
            'su': su,
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'rsakv': rsakv,
            'sp': password_secret,
            'sr': '1366*768',
            'encoding': 'UTF-8',
            'prelt': '115',
            "cdult": "38",
            # 'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'TEXT'  # 这里是 TEXT 和 META 选择，具体含义待探索
        }
        return sever_data

    def login(self):

        # 先不输入验证码登录测试
        # 代码150行开始一直到196 等价与Webweibo.py的88到122行
        # 这里主要是拼接url获取跳转url

        try:
            sever_data = self.pre_login()
            login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_'
            a = str(time() * 1000)
            login_url = login_url + a
            login_page = self.session.post(login_url, data=self.postdata, headers=HEADERS)
            ticket_js = login_page.json()
            # 得到ticket
            ticket = ticket_js["ticket"]
        except Exception as e:
            # 有验证码就要调用get_cha来获取验证码手动输入
            sever_data = self.pre_login()
            login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_'
            # 和我写的WebWeiBo的login_url一样都是导向干净额登录接口
            login_url = login_url + str(time() * 1000)
            pcid = sever_data["pcid"]
            self.get_cha(pcid)
            self.postdata['door'] = input(u"请输入验证码")
            login_page = self.session.post(login_url, data=self.postdata, headers=headers)
            ticket_js = login_page.json()
            ticket = ticket_js["ticket"]

        # 以下内容是 处理登录跳转链接
        save_pa = r'==-(\d+)-'
        # 后面添加的参数就是时间长度 这里我实验了 7小时  12小时 以及一年 均可以爬取。所以怀疑这个参数是指定cookies有效时长的。
        ssosavestate = int(re.findall(save_pa, ticket)[0]) + 31536000
        # header里面有一个ssosavestate 时间间隔为1年整 但是不知道为啥这里面是3600*7
        jump_ticket_params = {
            "callback": "sinaSSOController.callbackLoginStatus",
            "ticket": ticket,
            "ssosavestate": str(ssosavestate),
            "client": "ssologin.js(v1.4.19)",
            "_": str(time() * 1000),
        }
        # 横向对比WebWeiBO.py的跳转url
        jump_url = "https://passport.weibo.com/wbsso/login"
        jump_headers = {
            "Host": "passport.weibo.com",
            "Referer": "https://weibo.com/",
            "User-Agent": AGENT
        }
        jump_login = self.session.post(jump_url, params=jump_ticket_params, headers=jump_headers)
        uuid = jump_login.text
        uuid_pa = r'"uniqueid":"(.*?)"'
        uuid_res = re.findall(uuid_pa, uuid, re.S)[0]
        # profile页面 为了跳转profile验证是否登录成功
        # postman验证一下
        web_weibo_url = "http://weibo.com/%s/profile?topnav=1&wvr=6&is_all=1" % uuid_res
        
        self.session.get(web_weibo_url, headers=HEADERS)

        # 这里开始构建跳转m.weibo.com的url了
        Mheaders = {
            "Host": "login.sina.com.cn",
            "User-Agent": AGENT
        }

        # m.weibo.cn 登录的 url 拼接
        _rand = str(time())
        mParams = {
            "url": "https://m.weibo.cn/",
            "_rand": _rand,
            "gateway": "1",
            "service": "sinawap",
            "entry": "sinawap",
            "useticket": "1",
            "returntype": "META",
            "sudaref": "",
            "_client_version": "0.6.26",
        }
        murl = "https://login.sina.com.cn/sso/login.php"
        mhtml = self.session.get(murl, params=mParams, headers=Mheaders)
        mhtml.encoding = mhtml.apparent_encoding
        mpa = r'replace\((.*?)\);'
        # 得到 location.replace 函数内url 作用不明啊
        mres = re.findall(mpa, mhtml.text)

        # 关键的跳转步骤，这里不出问题，基本就成功了。
        # headers里将添加host属性 
        Mheaders["Host"] = "passport.weibo.cn"
        # self.session.get(eval(mres[0]), headers=Mheaders)
        mlogin = self.session.get(eval(mres[0]), headers=Mheaders)
        
        # 这里很神奇如果不调用一次这个LWP这个沙雕函数就登不上weibo.cn
        self.session.cookies.save()
        cookies = cookielib.LWPCookieJar("Cookie.txt")
        cookies.load(ignore_discard=True, ignore_expires=True)
        return requests.utils.dict_from_cookiejar(cookies)


class Redis_Insert:
    """
    调用set,存储用户名和cookie
    调用get，获得cookies
    """
    _instance_lock = None

    def __init__(self, ip='127.0.0.1', port=6379):
        self.ip = port
        self.ip = ip
        self.db = Redis(self.ip, self.port)

    def __new__(cls, *args, **kwargs):
        if not cls._instance_lock:
            cls._instance_lock = super().__new__(cls, *args, **kwargs)
        return cls._instance_lock


    def set(self, user_name: str, value: dict):
        """
        将cookies存到数据库
        :param user_name: dict
        :param value: str
        :return:
        """
        return self.db.set(user_name, value)

    def get(self, user_name):
        """
        得到指定user_name的cookies值
        :param user_name:
        :return:
        """
        return self.db.get(user_name)



if __name__ == "__main__":
    username = "a87762968@qq.com"  # 用户名
    password = "woninima111"  # 密码
    cookie_path = "Cookie2.txt"  # 保存cookie 的文件名称
    weibo = WeiboLogin(username, password, cookie_path)

    d = weibo.login()
    Redis_Insert().set(username, d)
