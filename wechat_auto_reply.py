# coding: utf-8

"""
微信自动回复机器人
"""

import requests, json, itchat, datetime

URL = "http://openapi.tuling123.com/openapi/api/v2"
API_KEY = "***"
USER_ID = "***"

# 缓存用户访问
USER_ACCESS_CACHE: dict = dict()
# 第一次回复内容
FIRST_REPLY = "主人正在工作中，无法及时回复哦~\n您要是等待得无聊，可以找我聊聊天呢~"
# 时间差/秒
DELTA = 600

@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    if msg.fromUserName != msg.user.UserName:
        # 本人回复
        print("{name}: {msg}".format(name="我", msg=msg.text))
        return ""
    print("{name}: {msg}".format(name=msg.user.NickName, msg=msg.text))
    if msg.fromUserName not in USER_ACCESS_CACHE.keys():
        USER_ACCESS_CACHE[msg.fromUserName] = now()
        reply = FIRST_REPLY
    else:
        delta = now() - USER_ACCESS_CACHE[msg.fromUserName]
        USER_ACCESS_CACHE[msg.fromUserName] = now()
        if delta.seconds > DELTA:
            reply = FIRST_REPLY
        else:
            reply = auto_replay(msg.text)
    print("{name}: {msg}".format(name="我", msg=reply))
    return reply

def now():
    return datetime.datetime.now()

def auto_replay(msg: str) -> str:
    headers, data = headers_and_data(msg)
    response = requests.post(URL, headers=headers, data=data)
    content = json.loads(response.content)
    try:
        return content["results"][0]["values"]["text"]
    except Exception:
        return ""

def headers_and_data(msg: str) -> tuple:
    headers: dict = {"Content-Type": "application/json"}
    data = {"reqType": 0, "perception": {"inputText": {"text": msg}}, "userInfo": {"apiKey": API_KEY, "userId": USER_ID}}
    return headers, json.dumps(data)

if __name__ == "__main__":
    itchat.auto_login(hotReload=True)
    itchat.run()
