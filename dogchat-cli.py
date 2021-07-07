import os
import sys
import time
import json
import getopt
import threading

import requests

config = {
        "url":"http://2eeefc39.cpolar.cn/api/",
        "token_path":f"{os.getenv('HOME')}/.dogchat_token"
        }

def get_help():
    print(sys.argv[0], "login")
    print("\t登录")
    print(sys.argv[0], "chat <dst>")
    print("\t与<dst>聊天")

def sendmsg(token, dst, msg):
    data = {"token":token, "dst_name":dst, "msg":msg}
    res = requests.post(config['url']+"send/", data=data)
    res.coding = "utf-8"
    return json.loads(res.text)['code']

def get_msg(token, dst, id):
    url = config['url']+f"getlogs/?token={token}&dst_name={dst}&id={id}"
    res = requests.get(url)
    res.coding = "utf-8"
    return json.loads(res.text)

def login(name, pwd):
    url = config['url']+f"login/?username={name}&password={pwd}"
    res = requests.get(url)
    res.coding = "utf-8"
    result = json.loads(res.text)
    if result['code'] == 200:
        return result['data']['token']
    elif result['code'] == 404:
        sys.stderr.write("错误: 没有此用户\n")
        sys.stderr.flush()
        sys.exit(1)
    elif result['code'] == 403:
        sys.stderr.write("错误: 用户名或密码错误\n")
        sys.stderr.flush()
        sys.exit(1)

def save_token(token):
    with open(config['token_path'], "w") as f:
        f.write(token)

def read_token():
    with open(config['token_path'], "r") as f:
        token = f.read()
    return token

def print_msg(token, dst):
    id = 0
    while 1:
        result = get_msg(token, dst, id)
        if result['code'] == 404:
            sys.stderr.write("此用户不存在\n")
            sys.stderr.flush()
            sys.exit(1)
        for msg in result['data']['logs']:
            print(msg['src']+":", msg['msg'])
            id = msg['id']
        time.sleep(1)

def send(token, dst):
    while 1:
        while (msg := input(">>> ")) != "\n":
            pass
        status = sendmsg(token, dst, msg)
        if status == 404:
            sys.stderr.write("此用户不存在\n")
            sys.stderr.flush()
            sys.exit(1)
        time.sleep(0.2)

def main(argv):
    _, args = getopt.gnu_getopt(argv[1:], "h")
    if len(args) == 1:
        if args[0] == "login":
            if os.path.exists(config['token_path']):
                token = read_token()
            else:
                token = login(input("用户名:"), input("密码:"))
            save_token(token)
    elif len(args) == 2:
        if args[0] == "chat":
            dst = args[1]
            if os.path.exists(config['token_path']):
                token = read_token()
            else:
                sys.stderr.write("请先登录\n")
                sys.stderr.flush()
                sys.exit(1)
            threading.Thread(target=print_msg, args=(token, dst), daemon=1).start()
            time.sleep(0.6)
            send(token, dst)
        else:
            get_help()
    else:
        get_help()

main(sys.argv)
