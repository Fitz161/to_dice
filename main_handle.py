from queue import Queue
from time import sleep, localtime, strftime
from datetime import datetime

from command import event_handle
from command.admin_command import *
from command.command import *
from config import MULTI_THREADING


def get_message(message_queue: Queue):
    if not message_queue.empty():
        message_info = extract_message(message_queue.get())
        print(strftime("%Y-%m-%d %H:%M:%S", localtime()), end=' ')
        print('收到 ', message_info.get('sender_qq'), '消息:', message_info.get('message'))
        black_list, is_active = get_black_active(message_info)
        if message_info['message'] == '/bot on':
            set_active(message_info, True)
        if message_info['group_qq'] in black_list or message_info['sender_qq'] in black_list or is_active == False:
            return None
        elif not message_info['is_notice'] and not message_info['is_anonymous'] and not message_info['is_request']:
            return message_info
        elif message_info['is_notice'] :
            if message_info['is_group_increase']:
                event_handle.welcome(message_info)
            elif message_info['is_group_recall']:
                event_handle.group_recall(message_info)
            elif message_info['is_group_kick']:
                event_handle.add_black_list(message_info)
            elif message_info['is_group_ban']:
                event_handle.group_ban(message_info)
            return None
        elif message_info['is_request']:
            if message_info['is_friend_add']:
                event_handle.friend_add_request(message_info)
            elif message_info['is_group_add']:
                event_handle.group_add_request(message_info)
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
    message_info['sub_type'] = message.get('sub_type')
    message_info['raw_message'] = message.get('raw_message')
    message_info['bot_qq'] = message.get('self_id')
    message_info['is_group_increase'] = True if notice_type == 'group_increase' else False
    message_info['is_group_kick'] = True if notice_type == 'group_decrease' \
                                            and message_info['sub_type'] == 'kick_me' else False
    message_info['is_group_recall'] = True if notice_type == 'group_recall' else False
    message_info['is_friend_add'] = True if  request_type == 'friend' else False
    message_info['is_group_ban'] = True if notice_type == 'group_ban' \
                                           and message_info['sender_qq'] == message_info['bot_qq'] else False
    message_info['is_group_add'] = True if request_type == 'group' and message.get('sub_type') == 'invite' else False
    return message_info


def handle_message(message_queue: Queue):
    while True:
        if not message_queue.empty():
            message_info: dict = get_message(message_queue)
            if message_info:
                message = message_info['message']
                if not MULTI_THREADING:
                    if message[:2] in command_dict.keys():
                        command_dict.get(message[:2])(message_info)
                    elif message[:3] in command_dict.keys():
                        command_dict.get(message[:3])(message_info)
                    elif message[0] in command_dict.keys():
                        command_dict.get(message[0])(message_info)
                    elif message in admin_command_dict.keys() and message_info['sender_qq'] in ADMIN_LIST:
                        admin_command_dict.get(message)(message_info)
                    learn_response(message_info)
                else:
                    if message[:2] in command_dict.keys():
                        threading.Thread(target=command_dict.get(message[:2]), args=(message_info,)).start()
                    elif message[:3] in command_dict.keys():
                        threading.Thread(target=command_dict.get(message[:3]), args=(message_info,)).start()
                    elif message[0] in command_dict.keys():
                        threading.Thread(target=command_dict.get(message[0]), args=(message_info,)).start()
                    elif message in admin_command_dict.keys() and message_info['sender_qq'] in ADMIN_LIST:
                        threading.Thread(target=admin_command_dict.get(message), args=(message_info,)).start()
                    learn_response(message_info)
        else:
            sleep(PAUSE_TIME)


def timing_task():
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0 and now.second == 0:
            admin_command_dict.get('重置')(0)
            with open(PATTERN_PATH) as f:
                data:dict = load(f)['evening']
                send_message = data.get(str(randint(1, len(data))))
            for group_qq in SEND_LIST:
                send_public_msg(send_message, group_qq)
            sleep(25000)
        elif now.hour == 7 and now.minute == 0 and now.second == 0:
            with open(PATTERN_PATH) as f:
                data:dict = load(f)['morning']
                send_message = data.get(str(randint(1, len(data))))
            for group_qq in SEND_LIST:
                send_public_msg(send_message, group_qq)
            sleep(61000)
        sleep(1)


def get_black_active(message_info):
    with open(BLACK_LIST_PATH) as f:
        black_list: list = load(f)['black_list']
    if not message_info['is_group']:
        return black_list, None
    group_qq = message_info['group_qq']
    with open(ACTIVE_PATH) as f:
        active_dict:dict = load(f)
    if str(group_qq) not in active_dict.keys():
        active_dict[str(group_qq)] = True
    is_active = active_dict.get(str(group_qq))
    with open(ACTIVE_PATH, 'w') as f:
        dump(active_dict, f)
    return black_list, is_active

def set_active(message_info, b:bool):
    if not message_info['is_group']:
        return
    group_qq = message_info['group_qq']
    QQ = message_info['sender_qq']
    from command.event_handle import get_group_admin
    if QQ not in get_group_admin(message_info):
        return
    with open(ACTIVE_PATH) as f:
        active_dict: dict = load(f)
    if str(group_qq) not in active_dict.keys():
        active_dict[str(group_qq)] = True
    active_dict[str(group_qq)] = b
    with open(ACTIVE_PATH, 'w') as f:
        dump(active_dict, f)
