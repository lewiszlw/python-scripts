"""
保存公司wiki脚本

利用selenium来截图，然后使用PIL拼接截图，递归保存每一个wiki页面
"""
import math, os, time, requests, json
from selenium import webdriver
from PIL import Image

# 用户名和密码
USERNAME = "***"
PASSWORD = "***"
# 初始页面, 需要是具体页面，才能获取宽高等数据
START_URL = "***"
# browser.maximize_window()下的截图宽高
IMAGE_HEIGHT = 1332
IMAGE_WIDTH = 3292
# 空间id
SPACE_ID = 123
# 下载后保存文件夹路径
DOWNLOAD_DIR = "***"
# 获取空间下子节点的api formatter形式
SPACE_CHILD_API_FORMAT = "***"
# 获取页面下子节点的api formatter形式
PAGE_CHILD_API_FORMAT = "***"
# 页面访问url formatter形式
PAGE_URL_FORMAT = "***"

def main():
    browser = login()
    header_height = get_header_height(browser)
    body_height = get_body_height(browser)
    cookies = convert_to_requests_cookies(browser.get_cookies())
    # 获取所有content_id
    nodes = []
    query_all_nodes(nodes, cookies, None)
    # 遍历节点，截图保存
    for node in nodes:
        browser.get(PAGE_URL_FORMAT.format(node["content_id"]))
        time.sleep(3)
        # title中/分隔符要进行替换
        screenshot(browser, body_height-header_height/2, DOWNLOAD_DIR, "{}.png".format(node["title"].replace("/", "-")))
    browser.quit()

def query_all_nodes(nodes: list, cookies: dict, content_id: int):
    """递归保存所有节点的contentId和title
    Args:
        nodes: 保存的地方
        cookies: requests需要的cookies形式
        content_id: 父节点
    """
    # 获取子节点
    child_nodes = query_child_nodes(cookies, content_id)
    for child_node in child_nodes:
        nodes.append({"content_id": child_node["contentId"], "title": child_node["title"]})
        if child_node["childCount"] != 0:
            query_all_nodes(nodes, cookies, child_node["contentId"])

def query_child_nodes(cookies: dict, content_id: int = None) -> list:
    """查询当前节点的所有子节点
    """
    if content_id == None:
        response = requests.get(SPACE_CHILD_API_FORMAT.format(SPACE_ID), cookies=cookies)
    else:
        response = requests.get(PAGE_CHILD_API_FORMAT.format(SPACE_ID, content_id), cookies=cookies)
    if response.content != None:
        content = json.loads(response.content)
        return content["data"]["list"]
    else:
        return []

def convert_to_requests_cookies(cookies: list) -> dict:
    """将selenium获取的cookies转换为requests库需要的cookies形式
    """
    return {cookie["name"]: cookie["value"] for cookie in cookies}

def screenshot(browser, offset: int, path: str, filename: str):
    """当前页面截图
    Args:
        offset: 每次滚动长度
        max_top: 滚动最大长度
        path: 截图保存路径
    """
    # tmp文件夹临时保存此页面截图，拼接完成后删除
    tmp_dir = "tmp"
    max_top = get_max_top(browser)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    if max_top == 0:
        # 页面很短无需滚动，max_top值为0
        scroll_num = 1
    else:
        scroll_num = math.ceil(max_top/offset)
    for i in range(scroll_num):
        location = offset * i
        scroll_and_screenshot(browser, location, 1, tmp_dir, "tmp{}.png".format(i))
    # 截取最底部
    scroll_and_screenshot(browser, max_top, 1, tmp_dir, "tmp{}.png".format(i + 1))
    img_files = [Image.open(tmp_dir + "/" + filename) for filename in os.listdir(tmp_dir) if filename.endswith(".png")]
    img_paste(img_files, path, filename)
    # 拼接完成后删除tmp内截图
    files = [tmp_dir + "/" + filename for filename in os.listdir(tmp_dir) if filename.endswith(".png")]
    for file in files:
        os.remove(file)

def scroll_and_screenshot(browser, location: int, sleep: int, path: str, filename: str):
    browser.execute_script("return document.getElementById('viewPageScrollWrapper').scrollTo(0, {});".format(location))
    time.sleep(sleep)
    browser.find_element_by_id("viewPageScrollWrapper").screenshot("{}/{}".format(path, filename))

def get_body_height(browser):
    """获取body高度
    """
    return browser.execute_script("return document.body.scrollHeight;")

def get_header_height(browser):
    """获取页面header高度
    """
    return browser.execute_script("return document.getElementById('ct-header').scrollHeight;")

def get_max_top(browser):
    """获取滚动条滚动长度
    """
    # 确保滚动到最底部
    maxTop = 10000000
    browser.execute_script("return document.getElementById('viewPageScrollWrapper').scrollTo(0, {});".format(maxTop))
    return browser.execute_script("return document.getElementById('viewPageScrollWrapper').scrollTop;")

def login():
    """启动chrome, 登陆页面, 初始化窗口大小
    """
    browser = webdriver.Chrome()
    browser.get(START_URL)
    # 登录
    browser.find_element_by_id("login-username").send_keys(USERNAME)
    browser.find_element_by_id("login-password").send_keys(PASSWORD)
    browser.find_element_by_name("commit").click()
    # 短信验证
    time.sleep(2) #防止下一步出现找不到recheckPhone元素
    browser.find_element_by_id("recheckPhone").click()
    smsCode = input("请输入短信验证码: ")
    browser.find_element_by_name("smsCode").send_keys(smsCode)
    browser.find_element_by_name("commit").click()
    browser.maximize_window()
    return browser

def img_paste(img_files: list, path: str, filename: str, width: int = IMAGE_WIDTH, height: int = IMAGE_HEIGHT):
    """图片纵向拼接
    Args:
        img_files: Image对象列表
        path: 拼接图片保存路径
        filename: 图片名称
        width: 图片宽度
        height: 图片高度
    """
    if img_files == []:
        return
    target = Image.new("RGB", (width, height * len(img_files)))
    left = 0
    right = height
    for i, img in enumerate(img_files):
        target.paste(img, box=(0, i * height))
        left += height
        right += height
    # 创建目录和文件
    if not os.path.exists(path):
        os.makedirs(path)
    open(path + '/' + filename, 'w').close()
    target.save(path + '/' + filename, quality=100)

if __name__ == "__main__":
    main()
