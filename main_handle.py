from queue import Queue
import time, threading
from time import sleep

from command import event_handle
from command.command import *
from  command.admin_command import *


def get_message(message_queue: Queue):
    if not message_queue.empty():
        message_info = extract_message(message_queue.get())
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), end=' ')
        print('收到消息:', message_info.get('sender_qq'), ':  ', message_info.get('message'))
        if message_info['group_qq'] in BLACK_LIST or message_info['sender_qq'] in BLACK_LIST:
            return None
        elif not message_info['is_notice'] and not message_info['is_anonymous'] and not message_info['is_request']:
            return message_info
        elif message_info['is_notice'] :
            if message_info['is_group_increase']:
                event_handle.welcome(message_info)
            elif message_info['is_group_recall']:
                event_handle.group_recall(message_info)
            return None
        elif message_info['is_request']:
            if message_info['is_friend_add']:
                event_handle.friend_add_request(message_info)
            elif message_info['is_group_add']:
                event_handle.friend_add_request(message_info)
            return None


def extract_message(message: dict):
    message_info = {}
    post_type = message.get('post_type')
    message_type = message.get('message_type')
    notice_type = message.get('notice_type')
    request_type = message.get('request_type')
    #message_info['message_id'] = message.get('message_id') if message.get('message_id') else 0
    message_info['is_message'] = True if post_type == 'message' else False
    message_info['is_notice'] = True if post_type == 'notice' else False
    message_info['is_request'] = True if post_type == 'request' else False
    message_info['is_group'] = True if message_type == 'group' else False
    message_info['is_private'] = True if message_type == 'private' else False
    message_info['is_anonymous'] = True if message.get('anonymous') else False
    message_info['flag'] = message.get('flag')
    message_info['message'] = message.get('message')
    message_info['group_qq'] = message.get('group_id')
    message_info['sender_qq'] = message.get('user_id')
    message_info['raw_message'] = message.get('raw_message')
    #message_info['bot_qq'] = str(message.get('self_id'))
    message_info['is_group_increase'] = True if notice_type == 'group_increase' else False
    message_info['is_group_recall'] = True if notice_type == 'group_recall' else False
    message_info['is_friend_add'] = True if  request_type == 'friend' else False
    message_info['is_group_add'] = True if request_type == 'group' and message.get('sub_type') == 'invite' else False

    return message_info


def handle_message(message_queue: Queue):
    while True:
        if not message_queue.empty():
            message_info: dict = get_message(message_queue)
            if message_info:
                message = message_info['message']
                if message[:2] in command_dict.keys():
                    #threading.Thread(target=command_dict.get(message[:2]), args=(message_info,)).start()
                    command_dict.get(message[:2])(message_info)
                elif message[:3] in command_dict.keys():
                    #threading.Thread(target=command_dict.get(message[:3]), args=(message_info,)).start()
                    command_dict.get(message[:3])(message_info)
                elif message[0] in command_dict.keys():
                    # threading.Thread(target=command_dict.get(message[:3]), args=(message_info,)).start()
                    command_dict.get(message[0])(message_info)
                elif message in admin_command_dict.keys() and message_info['sender_qq'] in ADMIN_LIST:
                    #threading.Thread(target=admin_command_dict.get(message[:2]), args=(message_info,)).start()
                    admin_command_dict.get(message)(message_info)
        else:
            sleep(PAUSE_TIME)
