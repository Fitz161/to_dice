import requests
from time import sleep
from json import load

from config import *
from bot_command.command import send_public_msg, send_private_msg

def get_group_admin(message_info):
    if not message_info['is_group']:
        return
    data = {
        'group_id':message_info['group_qq']
    }
    admin_list = []
    members:list = requests.post(apiBaseUrl + apiGroupMemberList, data=data).json()['data']
    for member in members:
        admin_list.append(member['user_id']) if member['role'] == 'admin' or member['role'] == 'owner' else None
    return admin_list


def welcome(message_info:dict):
    QQ = message_info['sender_qq']
    group_qq = message_info.get('group_qq')
    with open(ACTIVE_PATH) as f:
        active_dict: dict = load(f)
    try:
        is_enable:bool = active_dict[str(group_qq)]['welcome']
    except:
        is_enable = True
    if not is_enable:
        return
    api_url = apiBaseUrl + apiGroupInfo
    data = {
        'group_id': group_qq
    }
    response = requests.post(api_url, data=data)
    if response.status_code == 200 and QQ != message_info['bot_qq']:
        group_name = response.json()['data']['group_name']
        send_string = f'欢迎[CQ:at,qq={QQ}]来到{group_name}这个大家庭'
        send_public_msg(send_string, group_qq)




def friend_add_request(message_info:dict):
    QQ = message_info['sender_qq']
    data = {
        'flag': message_info['flag'],
        'approve' : 'true',
        'remark' : f'最可爱的bot{BOT_NAME}'
    }
    requests.post(apiBaseUrl + apiFriendRequest, data=data)
    print(f'已添加好友{QQ}')
    send_private_msg(f'已添加好友{QQ}', ADMIN_LIST[0])
    sleep(10)
    send_private_msg(f'Bot{BOT_NAME}です。\n发送.help查看帮助', QQ)


def group_add_request(message_info:dict):
    group_qq = message_info["group_qq"]
    data = {
        'flag': message_info['flag'],
        'approve': 'true',
        'sub_type': message_info['sub_type']
    }
    requests.post(apiBaseUrl + apiGroupRequest, data=data)
    print(f'已添加群{group_qq}')
    send_private_msg(f'已添加群{group_qq}', ADMIN_LIST[0])
    sleep(10)
    send_public_msg(f"Bot{BOT_NAME}です。\n发送.help查看帮助", group_qq)


def add_black_list(message_info):
    from json import load, dump
    with open(DATA_PATH) as f:
        total_data: dict = load(f)
    black_list: list = total_data['black_list']
    white_list:list = total_data['white_list']
    group_qq = message_info.get('group_qq')
    black_list.append(group_qq) if group_qq not in black_list and group_qq not in white_list else None
    total_data['black_list'] = black_list
    with open(DATA_PATH, 'w') as f:
        dump(total_data, f)


def leave_group(message_info):
    group_qq = message_info.get('group_qq')
    data = {
        'group_id': group_qq
    }
    response = requests.post(apiBaseUrl + apiSetGroupLeave, data=data)
    if response.status_code == 200:
        print(f'已离开群{group_qq}')


def group_ban(message_info):
    add_black_list(message_info)
    leave_group(message_info)
