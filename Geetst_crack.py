import requests, time
from PIL import Image
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from io import BytesIO
import numpy as np


URL = 'https://account.zbj.com/login'


class GeetstCrack:
    """
    注意以下几点：
        1.URL自定义
        2.极验3触发滑动的按钮位置在browsr中button内进行自定义
        3.get_pic中的canvas需要你自行的定义
        4.__main__语句下面有三个js语句分别对应着 ：没有阴影没有滑块的原图，有阴影有滑块的原图，没有滑块有引用的图
        根据情况不同，可以自行对改写调换三个语句
    """
    def __init__(self):
        self.driver = webdriver.Chrome()

    def browser(self):
        """
        创建浏览器，
        button处的css位置可以根据实际应用场景进行客制
        这个css选择器是极验3中的触发点击的按钮css位置。
        """
        self.driver.get(URL)
        wait = WebDriverWait(self.driver, 10)
        button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.geetest_radar_tip')))
        button.click()
        return self.driver

    def get_pic(self, browser,xpath='0', ):
        """
         将浏览器的内容截图下来，
        然后求得验证图片所在的位置，
        随后换算浏览器比例之后确定真实的图片位置所在随后将图片截图。
        :param browser:实例化的webdriver
        :param xpath: 为验证图片所在位置，根据情况自行选择
        :return: 存在内存中的图片
        """
        try:
            # 截屏
            screen = browser.get_screenshot_as_png()
            f = BytesIO()
            f.write(screen)
            picture = Image.open(f)

            # 获取验证图片的位置。
            canvas = browser.find_element_by_xpath(r'//div[@class="geetest_window"]')  # 这个地方可以自定义xpath
            if canvas:
                left = canvas.location['x']
                top = canvas.location['y']
                elementWidth = canvas.location['x'] + canvas.size['width']
                elementHeight = canvas.location['y'] + canvas.size['height']

                # 换算比例算出图片位置
                screen_height = browser.execute_script('return document.documentElement.clientHeight')
                screen_width = browser.execute_script('return document.documentElement.clientWidth')
                # 全局 x_scale 因为接下来会用到X_sale
                global x_scale
                x_scale = picture.size[0] / (screen_width + 10)  # 位置有便宜根据实际情况10这个位置可以没有也可以有。
                y_scale = picture.size[1] / (screen_height)
                postions = [left * x_scale, top * y_scale, elementWidth * x_scale, elementHeight * y_scale]
            else:
                print('未匹配到指定图片')
        except Exception as Err:
            raise Err
        return picture.crop(postions)

    def compare_pixel(self, img1, img2, x, y):
        """
        对图片之间的差值，确保图片有不同
        :param img1: 原图（没有阴影，没有滑块）
        :param img2: 有阴影的图
        :param x: 图片矩阵中的x
        :param y: 图片矩阵中的y
        :return: True/False 用作在compare函数中的判断
        """
        pixel1 = img1.load()[x, y]
        pixel2 = img2.load()[x, y]
        threshold = 50
        if abs(pixel1[0] - pixel2[0]) <= threshold:
            if abs(pixel1[1] - pixel2[1]) <= threshold:
                if abs(pixel1[2] - pixel2[2]) <= threshold:
                    return True
        return False

    def compare(self, full_img, slice_img):
        """
        找到像差异点
        :param full_img: 原图（没有阴影，没有滑块）
        :param slice_img: 有阴影的图
        :return: 像素差异点位置
        """
        left = 0
        for i in range(full_img.size[0]):
            for j in range(full_img.size[1]):
                if not self.compare_pixel(full_img, slice_img, i, j):
                    return i
        return left


    def get_tracks(self, distance, seconds=0.5):
        """
        根据轨迹离散分布生成的数学 生成
        成功率很高 90% 往上
        关于这个算法可以参考文档  https://www.jianshu.com/p/3f968958af5a
        :param distance: 缺口位置
        :param seconds:  时间
        :param ease_func: 生成函数
        :return: 轨迹数组
        """
        distance += 20
        tracks = [0]
        offsets = [0]
        for t in np.arange(0.0, seconds, 0.1):
            offset = round((1 - pow(1 - (t / seconds), 4)) * distance)
            print(offset)
            tracks.append(offset - offsets[-1])
            offsets.append(offset)
        tracks.extend([-3, -2, -3, -2, -2, -2, -2, -1, -0, -1, -1, -1])
        print(tracks)
        return tracks




if __name__ == '__main__':
    # 一个示例
    # 实例类
    cracker = GeetstCrack()
    # 生成浏览器
    browser = cracker.browser()
    time.sleep(3)
    # 取得没有阴影没有拼图的原图
    browser.execute_script(
        "document.getElementsByClassName('geetest_canvas_fullbg geetest_fade geetest_absolute')[0].style['display'] = 'block'")
    # 调用get_pic方法获得验证截图1
    pic1 = cracker.get_pic(browser, 1)
    # 将原图再变成有阴影有滑块
    browser.execute_script(
        "document.getElementsByClassName('geetest_canvas_fullbg geetest_fade geetest_absolute')[0].style['display'] = 'none'")
    time.sleep(2)
    # 去掉滑块 ，这里注意必须先取得干净的原图在取有阴影的图，不按此顺序那么图片不会有改变
    browser.execute_script(
        "document.getElementsByClassName('geetest_canvas_slice geetest_absolute')[0].style['display'] = 'none'")
    # 取得图片2
    pic2 = cracker.get_pic(browser, 2)
    # 对比两张图片的像素，必须大于50（可以自行定义，随后算出着点
    left = (cracker.compare(pic1, pic2)) / x_scale
    print(left)
    # 调用tracks方法得到运动轨迹
    tracks = cracker.get_tracks(left)
    print(tracks)
    # 这一步则将滑块恢复过来
    browser.execute_script(
        "document.getElementsByClassName('geetest_canvas_slice geetest_absolute')[0].style['display'] = 'block'")
    butoon = browser.find_element_by_xpath(r'/html/body/div[7]/div[2]/div[1]/div/div[1]/div[2]/div[2]')
    print('ok')
    # 选择滑块然后按照tracks内的像素数，调用actionchains来操作滑块
    ActionChains(browser).click_and_hold(butoon).perform()
    for x in tracks:
        ActionChains(browser).move_by_offset(xoffset=x, yoffset=0).perform()
    time.sleep(0.5)
    print('0k')
    ActionChains(browser).release().perform()
    print('done')

__author__ = "Govn"