from queue import Queue
import json
from time import sleep
from config import pause_time,command_list,admin_command_list
from command import *
#from command import  command_dict,admin_command_dict


def get_message(message_queue:Queue):
    if not message_queue.empty():
        message = json.loads(message_queue.get())
        message_info = extract_message(message)
        print('收到消息:', message_info.get('sender_qq'),':    ',message_info.get('message'))
        if not message_info['is_notice'] and not message_info['is_anonymous']:
            return message_info
            # if user_queue.get(user_qq) is None:
            #     user_queue[user_qq] = Queue()
            # user_queue[user_qq].put(message_info)
        elif message_info['is_notice'] and message_info['is_group_increse']:
            return None
            #bot_function.welcome(user_qq,group_qq)

def extract_message(message:dict):
    message_info = {}
    post_type = message.get('post_type')
    message_type = message.get('message_type')
    message_info['message_id'] = message.get('message_id') if message.get('message_id') else 0
    message_info['is_message'] = True if post_type == 'message' else False
    message_info['is_notice'] = True if post_type == 'notice' else False
    message_info['is_group'] = True if message_type == 'group' else False
    message_info['is_private'] = True if message_type == 'private' else False
    message_info['is_anonymous'] = True if message.get('anonymous') else False
    message_info['message'] = message.get('message')
    message_info['group_qq'] = str(message.get('group_id')) if message.get('group_id') else ''
    message_info['sender_qq'] = str(message.get('user_id'))
    message_info['raw_message'] = message.get('raw_message')
    message_info['bot_qq'] = str(message.get('self_id'))
    message_info['is_group_increse'] = True if message.get('notice_type') == 'group_increase' else False
    return message_info

def handle_message(message_queue:Queue):
    while True:
        if not message_queue.empty():
            message_info = get_message(message_queue)
            if not message_info:
                message = message_info['message']
                # is_private = message_info['is_private']
                # is_group = message_info['is_group']
                # group_qq = message_info.get('group_qq')
                if message[:2] in command_list:
                    command_dict.get(message[:2])(message[2:].strip(), message_info)
                elif message[:3] in command_list:
                    command_dict.get(message[:3])(message[3:].strip(), message_info)
                elif message[:2] in admin_command_list:
                    admin_command_dict.get(message[:2])(message[2:].strip(), message_info)
        else:
            sleep(pause_time)