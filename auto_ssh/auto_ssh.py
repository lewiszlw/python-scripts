# coding: utf-8

"""
自动登录机器，并进入日志目录

尝试过过subproces、pexpect、paramiko利用管道实现ssh自动登录机器，
但是都卡在跳板机这环，不好通过，最后采用这个丑陋的办法，利用控制
鼠标键盘方式实现自动登录如果有建议希望不吝赐教
"""

import time
from pymouse import PyMouse
from pykeyboard import PyKeyboard
from config import HOSTS, CMDS, SSH_CMD, PASSWORD

def main():
    mouse, keyboard, appkey, host = init()
    ssh_jumper(mouse, keyboard)
    ssh_host(mouse, keyboard, host)
    exec_cmd(mouse, keyboard, appkey)

def init():
    appkey = chose_appkey()
    env = chose_env(appkey)
    host = chose_host(appkey, env)
    return PyMouse(), PyKeyboard(), appkey, host

def chose_appkey():
    appkey_no = 1
    appkeys = {}
    for key in HOSTS.keys():
        appkeys[str(appkey_no)] = key
        print("序号: {}, appkey: {}".format(appkey_no, key))
        appkey_no +=1
    input_appkey_no = input("请输入序号: ")
    return appkeys[input_appkey_no]

def chose_env(appkey):
    env_no = 1
    envs = {}
    for env in HOSTS[appkey].keys():
        envs[str(env_no)] = env
        print("序号: {}, 环境: {}".format(env_no, env))
        env_no += 1
    input_env_no = input("请输入序号: ")
    if input_env_no:
        return envs[input_env_no]
    else:
        return "online"

def chose_host(appkey, env):
    hosts = {}
    host_no = 1
    for host in HOSTS[appkey][env]:
        hosts[str(host_no)] = host
        print("序号: {}, 主机名: {}".format(host_no, host))
        host_no += 1
    input_host_no = input("请输入序号: ")
    return hosts[input_host_no]

def ssh_jumper(mouse, keyboard):
    #import pdb;pdb.set_trace()
    click_window(mouse)
    keyboard.type_string(SSH_CMD + "\n")
    time.sleep(2)
    click_window(mouse)
    keyboard.type_string(PASSWORD + "\n")
    code = input("please input verification code: ")
    click_window(mouse)
    keyboard.type_string(code + "\n")
    time.sleep(2)

def ssh_host(mouse, keyboard, host):
    click_window(mouse)
    keyboard.type_string("ssh {}\n".format(host))
    time.sleep(2)

def exec_cmd(mouse, keyboard, appkey):
    cmd = CMDS[appkey]
    click_window(mouse)
    keyboard.type_string(cmd + "\n")

def click_window(mouse):
    width, height = mouse.screen_size()
    mouse.click(width/2, height/2, 1)

if __name__ == "__main__":
    main()
