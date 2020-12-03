import requests
from time import sleep
from config import apiBaseUrl, apiFriendRequest, apiGroupRequest, apiGroupInfo
from command.command import send_public_msg, send_private_msg


def welcome(message_info:dict):
    QQ = message_info['sender_qq']
    group_qq = message_info.get('group_qq')
    api_url = apiBaseUrl + apiGroupInfo
    data = {
        'group_id': group_qq
    }
    response = requests.post(api_url, data=data)
    if response.status_code == 200:
        group_name = response.json()['data']['group_name']
        send_string = f'欢迎[CQ:at,qq={QQ}]来到{group_name}这个大家庭'
        send_public_msg(send_string, group_qq)

def group_recall(message_info:dict):
    pass

def friend_add_request(message_info:dict):
    QQ = message_info['sender_qq']
    data = {
        'flag': message_info['flag']
    }
    response = requests.post(apiBaseUrl + apiFriendRequest, data=data)
    if response.status_code == 200:
        print(f'添加好友{QQ}')
        sleep(2)
        send_private_msg('Botです。\n输入.help查看帮助', QQ)


def group_add_request(message_info:dict):
    group_qq = message_info["group_qq"]
    data = {
        'flag': message_info['flag']
    }
    response = requests.post(apiBaseUrl + apiGroupRequest, data=data)
    if response.status_code == 200:
        print(f'添加群{group_qq}')
        sleep(2)
        send_public_msg('Botです。\n输入.help查看帮助', group_qq)
