import re
import requests
import redis


CONN = redis.Redis(host='127.0.0.1', port='6379')


class IpCathcer:
    __ip_list = []

    @classmethod
    def get_list(cls):
        return cls.__ip_list

    @staticmethod
    def ip_spider0(num):
        """
        66代理抓取
        :param num:
        :return:
        """
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
                   'Accept': '*/*',
                   'Connection': 'keep-alive',
                   'Accept-Language': 'zh-CN,zh;q=0.8'}
        url = 'http://www.66ip.cn/nmtq.php?getnum={}&isp=0&anonymoustype=0&s'
        try:
            html = requests.get(url.format(num), headers=headers).text
            ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html)
            IpCathcer.__ip_list.extend(ips)

            return IpCathcer

        except Exception as Err:
            print(Err)
            pass

    @staticmethod
    def ip_spider1():
        """
        xici代理
        :return:
        """
        url = 'https://www.xicidaili.com/nn/'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
                   'Accept': '*/*',
                   'Connection': 'keep-alive',
                   'Accept-Language': 'zh-CN,zh;q=0.8'}
        try:
            from lxml import etree
            html = requests.get(url, headers=headers)
            ips = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>', html.text)
            ports = re.findall(r'<td>(\d{1,5})</td>', html.text)

            if len(ips) == len(ports):
                for i in range(len(ips)):
                    ip = str(ips[i] + ':' + ports[i])
                    IpCathcer.__ip_list.append(ip)

            return IpCathcer.__ip_list

        except Exception as Err:
            print(Err)

    @staticmethod
    def ip_spider2():
        """
        目前就爬取这两个就可以其他的 后期继续写。
        :return:
        """
        pass


    @staticmethod
    def ip_checker(ips):
        """
        检查IP可用与否，可以写成装饰器的样式 但是感觉有点没啥用。
        高并发模式化将该函数改成装饰器，然后并发抓取IP。
        :param ip:
        :return:
        """
        ip_pool = []
        url = 'http://www.baidu.com'

        for ip in IpCathcer.__ip_list:

            proxy = {
                'http': ip,
                'https': ip
            }

            try:
                reponse = requests.get(url, proxies=proxy, timeout=4)

                if reponse.status_code == 200:
                    print('好玩意啊：' + ip)
                    ip_pool.append(ip)

                else:
                    print('什么几把玩意：' + ip)

            except Exception as Err:
                print('fuck')
        return ip_pool

def main():
    IpCathcer.ip_spider0(10)
    IpCathcer.ip_spider1()

    print(IpCathcer.get_list())

    ips = IpCathcer.ip_checker(IpCathcer.get_list())
    print(ips)

    while ips:
        ip = ips.pop()
        CONN.lpush('ip', ip)

    print(ips)


if __name__ == '__main__':
    main()
