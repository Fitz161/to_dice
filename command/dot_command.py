import requests

from config import apiBaseUrl, apiGroupInfo, ADMIN_LIST
from command.command import send_public_msg, send_private_msg


def dot_send_msg(message_info:dict):
    raw_message = message_info['message'][5:].strip()
    if message_info['is_group']:
        api_url = apiBaseUrl + apiGroupInfo
        data = {
            'group_id':message_info.get('group_qq')
        }
        response = requests.post(api_url,data=data)
        if response.status_code == 200:
            group_name = response.json()['data']['group_name']
            send_string = f'来自群:{group_name},QQ:{message_info["sender_qq"]}的消息:\n{raw_message}'
            send_private_msg(send_string, ADMIN_LIST[0])
        else:
            return
    else:
        send_string = f'来自QQ:{message_info["sender_qq"]}的消息:\n{raw_message}'
        send_private_msg(send_string, ADMIN_LIST[0])


def show_command_doc(message_info):
    send_string = '签到/打卡\n单抽/十连/百连1-7\n要礼物 热榜\n冷知识 点歌\n'\
                  '搜索格式:\n百度/搜索1-3 内容\n百度：百度百科\n搜索1'\
                  '：wikipedia(暂不可用)\n搜索2：萌娘百科\n搜索3：touhouwiki'
    if message_info['is_private']:
        send_private_msg(send_string, message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])