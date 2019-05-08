#coding: utf-8

"""
霸王餐自动报名脚本
"""

import requests, json, time, logging
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

ACTIVITY_LIST_URL = "http://m.dianping.com/activity/static/pc/ajaxList"

def query_all_activities():
    """查询所有活动
    :return: 活动列表
    """
    activities = []
    page = 1
    hasNext = True
    while hasNext:
        data = {"cityId": "2", "type": 1, "mode": "", "page": page}
        headers = {"Content-Type": "application/json"}
        response = requests.post(ACTIVITY_LIST_URL, data=json.dumps(data), headers=headers)
        content = json.loads(response.content)
        if content["code"] != 200:
            break;
        data = content["data"]
        logging.debug("\n================第{}请求活动数据===============".format(page))
        logging.debug(json.dumps(data, ensure_ascii=False))
        for activity in data["detail"]:
            activities.append(activity)
        hasNext = data["hasNext"]
        page += 1
    return activities

def main():
    # 获取的所有活动
    activities = query_all_activities()
    browser = webdriver.Chrome()
    first = True
    for activity in activities:
        browser.get(activity["detailUrl"])
        time.sleep(2)
        # 点击报名
        resp = browser.find_element_by_xpath("/html/body/div[3]/div[1]/div[2]/div[2]/span/a").click()
        time.sleep(2)
        # 第一次扫码登录
        if not scan_qr_code(first):
            break
        try:
            # TODO 选择分店
            # 点击确定
            browser.find_element_by_id("J_pop_ok").click()
            time.sleep(2)
        except NoSuchElementException:
            print("活动：{}，detailUrl：{} 已参与报名，重复报名异常"
                .format(activity["activityTitle"], activity["detailUrl"]))
        first = False
    browser.quit()

def scan_qr_code(first):
    """扫码登录二维码
    :return 是否已登录
    """
    if first:
        input_str = input("第一次请扫描登录，登录结果：[y/n]")
        return True if input_str == "y" else False
    else:
        return True

if __name__ == "__main__":
    main()
