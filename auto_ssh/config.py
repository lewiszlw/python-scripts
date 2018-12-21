# coding: utf-8

# 登录跳板机命令
SSH_CMD = "ssh ***"
# 登录跳板机密码
PASSWORD = "***"

# 主机列表
HOSTS: dict = {
    "appkey1": {
        "online": [],
        "staging": [],
        "test": [
            "host1",
            "host2"
            ]
        },
    "appkey2": {
        "online": [],
        "staging": [],
        "test": [
            "host1",
            "host2"
            ]
        }
    }

# 登录目标机器后执行的命令
# 进入日志目录
CMDS = {
    "appkey1": "cd /opt/logs/***/",
    "appkey2": "cd /opt/logs/***/"
    }
