# coding: utf-8

"""
点评app“0元秒杀”活动秒杀脚本
"""

from appium import webdriver
import time

# 秒杀活动开始时间
ACTIVITY_START_TIME = "2019-05-13 10:00:00"
# 活动秒杀项，元素为xpath序号（xpath序号从1递增）
ACTIVITY_ITEMS = [2, 3, 4, 5, 6]
# 秒杀活动提前时间开始秒杀
ACTIVITY_AHEAD_SECONDS = 1
# app首页进入霸王餐页面按钮xpath
TO_OVERLOAD_MEAL_PAGE_XPATH = '//android.widget.ImageButton[@content-desc="霸王餐NEW"]'
# 霸王餐页面进入0元秒杀页面按钮xpath
TO_ZERO_PRICE_PAGE_XPATH = "/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.view.ViewGroup/android.webkit.WebView/android.webkit.WebView/android.view.View[1]/android.view.View[4]/android.view.View[2]/android.view.View[2]"
# 0元秒杀页面第一项活动的xpath，用于判断页面是否加载完成
ZERO_PRICE_PAGE_FIRST_ITEM_XPATH = "/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.view.ViewGroup/android.webkit.WebView/android.webkit.WebView/android.view.View[2]/android.view.View/android.view.View/android.view.View[1]/android.view.View[2]/android.view.View[2]/android.view.View[3]/android.view.View[2]"

def start_driver():
    """启动appium driver
    :return dirver
    """
    desired_caps={
        "platformName": "Android",
        "version": "8.0.0",
        "deviceName": "26d855ff", # adb devices查看 
        "appPackage": "com.dianping.v1",
        "appActivity": "com.dianping.main.guide.SplashScreenActivity",
        "noreset": True
    }
    driver=webdriver.Remote('http://127.0.0.1:4723/wd/hub', desired_caps)
    return driver

def app_login():
    """手动登录app
    """
    time_confirm_result = input("活动开始时间：{}，请确认：[y/n]".format(ACTIVITY_START_TIME))
    check_input(time_confirm_result, "y", "确认活动开始时间")
    login_result = input("请手动登录app。是否已完成登录：[y/n]")
    check_input(login_result, "y", "必须先完成登录才可继续操作")
    back_home_result = input("请手动返回app首页。是否已完成：[y/n]")
    check_input(back_home_result, "y", "请先返回app首页")

def open_target_page(driver):
    """打开0元秒杀页面
    """
    ele_overload = driver.find_element_by_xpath(TO_OVERLOAD_MEAL_PAGE_XPATH)
    ele_overload.click()
    wait_until(lambda :driver.find_element_by_xpath(TO_ZERO_PRICE_PAGE_XPATH), frequency=2, err_msg="进入霸王餐页面失败")
    print("进入霸王餐页面成功")
    # overload_result = input("进入霸王餐页面。是否页面已加载完成：[y/n]")
    # check_input(overload_result, "y", "需等待霸王餐页面加载完成才可进行后续操作")
    ele_zero_price = driver.find_element_by_xpath(TO_ZERO_PRICE_PAGE_XPATH)
    ele_zero_price.click()
    wait_until(lambda :driver.find_element_by_xpath(ZERO_PRICE_PAGE_FIRST_ITEM_XPATH), frequency=2, err_msg="进入0元秒杀页面失败")
    print("进入0元秒杀页面成功")
    # zero_price_result = input("进入0元秒杀页面。是否页面已加载完成：[y/n]")
    # check_input(zero_price_result, "y", "需等待0元秒杀页面加载完成才可进行后续操作")

def start_seckill_task(driver):
    """开启秒杀任务
    """
    print("开启秒杀，秒杀时间：{}, 秒杀活动: {}".format(ACTIVITY_START_TIME, ACTIVITY_ITEMS))
    activity_start_time = time.strptime(ACTIVITY_START_TIME, "%Y-%m-%d %H:%M:%S")
    time_point = time.time()
    round = 1
    while True:
        print("========第 {} 轮秒杀开始=======".format(round))
        current_time = time.time()
        print("当前时间：{}".format(current_time_str(current_time)))
        if time.mktime(activity_start_time) < time.time():
            print("结果：秒杀时间已过")
            break
        elif time.mktime(activity_start_time) >= time.time() and time.mktime(activity_start_time) - time.time() > ACTIVITY_AHEAD_SECONDS:
            print("结果：秒杀活动未开始")
            # 建议手机多长时间未操作则锁屏的时间长些
            if time.mktime(activity_start_time) - current_time > 15 and current_time - time_point > 10:
                print("刷新页面")
                # 距离活动开始大于15秒，每隔10秒刷新一次页面防止锁屏
                time_point = current_time
                refresh_page(driver, TO_ZERO_PRICE_PAGE_XPATH, sleep_secs_after_back=3)
        else:
            print("开始秒杀!!!")
            refresh_page(driver, TO_ZERO_PRICE_PAGE_XPATH, method=lambda:driver.find_element_by_xpath(ZERO_PRICE_PAGE_FIRST_ITEM_XPATH))
            seckill(driver)
            break
        round += 1
        time.sleep(1)

def seckill(driver, count=5):
    """秒杀
    :param count 重复秒杀次数
    """
    for i in range(count):
        print("***重复秒杀第 {} 次***".format(i + 1))
        print("当前时间：{}".format(current_time_str()))
        # 获取活动element
        eles = items_element(driver)
        # 点击“抢”
        for ele in eles:
            ele.click()
        # 刷新页面
        refresh_page(driver, TO_ZERO_PRICE_PAGE_XPATH, method=lambda:driver.find_element_by_xpath(ZERO_PRICE_PAGE_FIRST_ITEM_XPATH))

def items_element(driver):
    """获取0元秒杀页面每个活动的element
    :return element集合
    """
    eles = []
    for each in ACTIVITY_ITEMS:
        try:
            element = driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.view.ViewGroup/android.webkit.WebView/android.webkit.WebView/android.view.View[2]/android.view.View/android.view.View/android.view.View[1]/android.view.View[{}]/android.view.View[2]/android.view.View[3]/android.view.View[2]'.format(each))
            eles.append(element)
        except Exception:
            print("find_element_by_xpath exception item: {}".format(each))
    print("items_element actual size: {}, expected size: {}".format(len(eles), len(ACTIVITY_ITEMS)))
    return eles

def refresh_page(driver, xpath, sleep_secs_after_back=0.5, sleep_secs=2, method=None):
    """刷新页面，采用返回-重进来刷新
    """
    driver.back()
    time.sleep(sleep_secs_after_back)
    ele = driver.find_element_by_xpath(xpath)
    ele.click()
    if method == None:
        time.sleep(sleep_secs)
    else:
        wait_until(method)

def check_input(input, expected, err_msg):
    """检查输入结果
    :param input 输入值
    :param expected 期望的值
    :param err_msg 错误信息
    """
    if input != expected:
        raise Exception(err_msg)

def current_time_str(current_time=None):
    """获取当前时间字符串
    :param current_time 当前时间戳（秒）
    """
    if current_time == None:
        current_time = time.time()
    current_struct_time = time.localtime(current_time)
    return time.strftime("%Y-%m-%d %H:%M:%S", current_struct_time)

def wait_until(method, timeout=10, frequency=0.5, err_msg=""):
    """等待页面加载完毕
    :param method 判断加载完毕的方法
    :param timeout 超时时间（秒）
    :param frequency 判断频率（秒）
    """
    begin_time = time.time()
    expend_time = 0
    while expend_time < timeout:
        try:
            method()
            return
        except Exception as e:
            print("方法执行失败: {}".format(e))
        time.sleep(frequency)
        expend_time = time.time() - begin_time
    else:
        raise Exception("timeout, err_msg: {}".format(err_msg))

def main():
    driver = start_driver()
    app_login()
    open_target_page(driver)
    start_seckill_task(driver)

if __name__ == "__main__":
    main()
