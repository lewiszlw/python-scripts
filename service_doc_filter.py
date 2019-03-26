#coding: utf-8

"""
筛选SOA服务文档方法脚本
"""

import requests, json

#文档接口api
INTERFACE_API = "https://***/catalog/api/v1/services/{appkey}/document/interface"
#方法文档api
METHOD_DOC_API = "https://***/catalog/api/v1/services/{appkey}/document/interface/{interface_uuid}/method/{method_uuid}"
#应用appkey
APPKEYS = [
        "***",
        "***",
        "***",
        "***"
        ]


class Appkey():
    def __init__(self, appkey):
        self.appkey = appkey
        self.uuids = {}
        self.method_docs = {}

    def set_interface_uuid(self, interface_uuid):
        if interface_uuid not in self.uuids.keys():
            self.uuids[interface_uuid] = []

    def put_method_uuid(self, interface_uuid, method_uuid):
        self.set_interface_uuid(interface_uuid)
        self.uuids[interface_uuid].append(method_uuid)

    def put_method_doc(self, method_uuid, doc):
        self.method_docs[method_uuid] = doc

    def get_appkey(self):
        return self.appkey

    def get_uuids(self):
        return self.uuids

    def get_method_docs(self):
        return self.method_docs
    
    def __str__(self):
        return "Appkey[appkey={}, uuids={}, method_docs={}]"\
                .format(self.appkey, json.dumps(self.uuids), json.dumps(self.method_docs))

    def __repr__(self):
        return self.__str__()


def input_cookies():
    """获取cookies字典
    """
    cookies_str = input("输入cookies:\n")
    return extract_cookies(cookies_str)

def extract_cookies(cookies: str) -> dict:
    """转换cookies为dict
    """
    return {l.split("=")[0]:l.split("=")[1] for l in cookies.split("; ")}

def all_methods(cookies):
    """获取所有soa服务文档方法
    """
    result = []
    for appkey in APPKEYS:
        appkey_obj = Appkey(appkey)
        resp = requests.get(INTERFACE_API.format(appkey=appkey), cookies=cookies)
        content = json.loads(resp.content)
        for item in content["data"]["items"]:
            interface_uuid = item["uuid"]
            appkey_obj.set_interface_uuid(interface_uuid)
            for method in item["methods"]:
                appkey_obj.put_method_uuid(interface_uuid, method["uuid"])
        result.append(appkey_obj)
    print("============soa所有服务文档===========")
    print(result)
    return result
                
def method_doc(appkey):
    """获取方法文档
    """
    uuids = appkey.get_uuids()
    for interface_uuid in uuids.keys():
        method_uuids = uuids[interface_uuid]
        for method_uuid in method_uuids:
            resp = requests.get(METHOD_DOC_API.format(appkey=appkey.get_appkey(), \
                                            interface_uuid=interface_uuid, \
                                            method_uuid=method_uuid))
            content = json.loads(resp.content)
            appkey.put_method_doc(method_uuid, content["data"])
    return appkey

def filter_rule(appkey):
    """过滤规则
    """
    method_docs = appkey.get_method_docs()
    # 不符合的方法
    not_correspond_method_uuids = []
    for method_uuid, doc in method_docs.items():
        correspond = False
        extensions = doc["model"]["extensions"]
        for extension in extensions:
            if extension["name"] == "SECURITY_PRIVILEGE_STATUS":
                correspond = True
                break
        if not correspond:
            not_correspond_method_uuids.append(method_uuid)
    for method_uuid in not_correspond_method_uuids:
        del method_docs[method_uuid]
    return appkey

def gen_html(appkeys):
    """生成html
    """
    html_head = """
    <head>
        <style>
            #table-4 thead, #table-4 tr {
            border-top-width: 1px;
            border-top-style: solid;
            border-top-color: rgb(211, 202, 221);
            }
            #table-4 {
            border-bottom-width: 1px;
            border-bottom-style: solid;
            border-bottom-color: rgb(211, 202, 221);
            }
            
            #table-4 td, #table-4 th {
            padding: 5px 10px;
            font-size: 12px;
            font-family: Verdana;
            color: rgb(95, 74, 121);
            }
            
            #table-4 tr:nth-child(even) {
            background: rgb(223, 216, 232)
            }
            #table-4 tr:nth-child(odd) {
            background: #FFF
            }
        </style>
    </head>
    """

    html_template = """
        <table id="table-4">
            <tr>
                <th>appkey</th>
                <th>接口</th>
                <th>方法</th>
            </tr>
            {trs}
        </table>
    """

    tr_template = """
        <tr>
            <td>{appkey}</td>
            <td>{interface}</td>
            <td>{method}</td>
        </tr>
    """
    trs = ""
    for appkey in appkeys:
        appkey_name = appkey.get_appkey()
        uuids = appkey.get_uuids()
        for interface_uuid, method_uuids in uuids.items():
            interface = interface_uuid.split("_")[0]
            for method_uuid in method_uuids:
                if method_uuid in appkey.get_method_docs().keys():
                    trs += tr_template.format(appkey=appkey_name, interface=interface, method=method_uuid)
    html = html_head + html_template.format(trs=trs)
    with open("service_doc.html", "w") as f:
        f.write(html)

def main():
    cookies = input_cookies()
    appkeys = all_methods(cookies)
    appkeys = list(map(method_doc, appkeys))
    appkeys = list(filter(filter_rule, appkeys))
    #print("=========过滤结果=========")
    #for appkey in appkeys:
    #    print(appkey.get_appkey(), len(appkey.get_method_docs().keys()))
    #    for method_uuid, doc in appkey.get_method_docs().items():
    #        print(method_uuid, doc["model"]["extensions"])
    gen_html(appkeys)

if __name__ == "__main__":
    main()
