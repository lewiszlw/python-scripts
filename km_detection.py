#coding: utf-8

"""
检测更新或新建的wiki
"""

import requests, json, os

# 获取空间下子节点的api formatter形式
SPACE_CHILD_API_FORMAT = "https://***/api/spaces/child/{}"
# 获取页面下子节点的api formatter形式
PAGE_CHILD_API_FORMAT = "https://***/api/pages/child/{}/{}"
# URL formatter形式
URL_FORMAT = "https://***/page/{}"
# 空间id
SPACE_ID = 1 
# wiki本地存放地址
DIC = "/Users/***/Documents/***/"

def get_cookies():
    """获取cookies字典
    """
    cookies_str = input("输入cookies:\n")
    return extract_cookies(cookies_str)

def extract_cookies(cookies: str) -> dict:
    """转换cookies为dict
    """
    return {l.split("=")[0]:l.split("=")[1] for l in cookies.split("; ")}

def query_all_nodes(nodes: list, cookies: dict, content_id: int, depth = 0):
    """递归保存所有节点的contentId和title
    Args:
        nodes: 保存的地方
        cookies: requests需要的cookies形式
        content_id: 父节点
    """
    depth += 2
    # 获取子节点
    child_nodes = query_child_nodes(cookies, content_id)
    for child_node in child_nodes:
        print("-" * depth, child_node["title"])
        nodes.append({"content_id": child_node["contentId"], "title": child_node["title"], "modify_time": child_node["modifyTime"]})
        if child_node["childCount"] != 0:
            query_all_nodes(nodes, cookies, child_node["contentId"], depth)

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

def all_files(directory: str):
    """获取目录下所有文件及文件修改时间
    """
    filenames = os.listdir(directory)
    files: list = []
    for filename in filenames:
        files.append({"filename": filename, "modify_time": os.path.getmtime(os.path.join(directory, filename)) * 1000})
    print("==============================")
    print("本地文件数量：", len(files))
    return files

def detection(nodes: list, files: list):
    """检测哪些文件需下载或更新
    """
    need_download_nodes = []
    print("============检测结果============")
    for node in nodes:
        if need_download(files, node):
            need_download_nodes.append(node)
            print("title: ", node["title"], "(url: " + URL_FORMAT.format(node["content_id"]) + " )")
    print("\n需下载或更新wiki数量: ", len(need_download_nodes))
    

def need_download(files: list, node: dict):
    for each_file in files:
        if node["title"] in each_file["filename"]:
            return True if node["modify_time"] > each_file["modify_time"] else False
    return True

def main():
    nodes = []
    query_all_nodes(nodes, get_cookies(), None)
    print("==============================")
    print("wiki数量：", len(nodes))
    detection(nodes, all_files(DIC))

if __name__ == "__main__":
    main()
