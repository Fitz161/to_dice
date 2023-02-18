from queue import Queue
from datetime import datetime

from bot_command import event_handle
from bot_command.admin_command import *
from bot_command.command import *
from config import MULTI_THREADING


def get_message(message_queue: Queue):
    if not message_queue.empty():
        message_info = extract_message(message_queue.get())
        print(strftime("%Y-%m-%d %H:%M:%S", localtime()), end=' ')
        print('收到 ', message_info.get('sender_qq'), '消息:', message_info.get('message'))
        black_list, is_active = get_black_active(message_info)
        threading.Thread(target=log_handle, args=(message_info,), daemon=True).start()
        #私聊消息is_active会返回None
        if message_info['is_at_bot']:
            #bot被at后始终会响应命令，不受/bot off限制，会受listen_at群属性限制
            message_info['message'] = message_info['message'][11 + len(str(message_info['bot_qq'])):].strip()
            if not message_info['message']: return
            if message_info['message'][1:].startswith('bot on'):
                bot_on(message_info, is_active)
                return None
            return message_info
        elif message_info['message'][1:].startswith('bot on'):
            bot_on(message_info, is_active)
            return None
        if message_info['group_qq'] in black_list or message_info['sender_qq'] in black_list or is_active == False:
            return None
        #通知消息处理
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
            elif message_info['is_poke']:
                message_info['message'] = '.r'
                return message_info
            return None
        # 好友请求消息处理
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
    message_info['is_message'] = True if post_type == 'message' else False
    message_info['is_notice'] = True if post_type == 'notice' else False
    message_info['is_request'] = True if post_type == 'request' else False
    message_info['is_group'] = True if message_type == 'group' else False
    message_info['is_private'] = True if message_type == 'private' else False
    message_info['is_anonymous'] = True if message.get('anonymous') else False
    message_info['flag'] = message.get('flag')
    message_info['message'] = message.get('message') if message.get('message') else ''
    message_info['message_id'] = message.get('message_id') if message.get('message_id') else 0
    message_info['group_qq'] = message.get('group_id')
    message_info['sender_qq'] = message.get('user_id')
    message_info['sub_type'] = message.get('sub_type')
    message_info['raw_message'] = message.get('raw_message')
    message_info['bot_qq'] = message.get('self_id')
    message_info['nickname'] = get_nickname(message)
    message_info['is_at_bot'] = True if is_at_bot(message_info) else False
    message_info['is_group_increase'] = True if notice_type == 'group_increase' else False
    message_info['is_group_kick'] = True if notice_type == 'group_decrease' \
                                            and message_info['sub_type'] == 'kick_me' else False
    message_info['is_group_recall'] = True if notice_type == 'group_recall' else False
    message_info['is_friend_add'] = True if  request_type == 'friend' else False
    message_info['is_group_ban'] = True if notice_type == 'group_ban' \
                                           and message_info['sender_qq'] == message_info['bot_qq'] else False
    message_info['is_group_add'] = True if request_type == 'group' and message.get('sub_type') == 'invite' else False
    message_info['is_poke'] = True if notice_type == 'notify' and message.get('sub_type') == 'poke' else False
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
                        threading.Thread(target=command_dict.get(message[:2]), args=(message_info,), daemon=True).start()
                    elif message[:3] in command_dict.keys():
                        threading.Thread(target=command_dict.get(message[:3]), args=(message_info,), daemon=True).start()
                    elif message[0] in command_dict.keys():
                        threading.Thread(target=command_dict.get(message[0]), args=(message_info,), daemon=True).start()
                    elif message[:3] in admin_command_dict.keys() and message_info['sender_qq'] in ADMIN_LIST:
                        threading.Thread(target=admin_command_dict.get(message[:3]), args=(message_info,)).start()
                    learn_response(message_info)
        else:
            sleep(PAUSE_TIME)


def timing_task():
    while True:
        now = datetime.now()
        if now.second == 0:
            threading.Thread(target=heart_beat_check, daemon=True).start()
        if now.minute == 0 and now.second == 0:
            if bot_status() == "bot已下线\n":
                send_private_msg('go-cqhttp已下线', ADMIN_LIST[0])
                break
        if now.hour == 0 and now.minute == 0 and now.second == 0:
            admin_command_dict.get('重置')(0)
            with open(PATTERN_PATH) as f:
                data:dict = load(f)['evening']
                send_message = data.get(str(randint(1, len(data))))
            for group_qq in read_json_file(DATA_PATH)['send_list']:
                send_public_msg(send_message, group_qq)
            backup_files()
        elif now.hour == 7 and now.minute == 0 and now.second == 0:
            with open(PATTERN_PATH) as f:
                data:dict = load(f)['morning']
                send_message = data.get(str(randint(1, len(data))))
            for group_qq in read_json_file(DATA_PATH)['send_list']:
                send_public_msg(send_message, group_qq)
        sleep(1)


def get_black_active(message_info):
    with open(DATA_PATH) as f:
        black_list: list = load(f)['black_list']
    if not message_info['is_group']:
        return black_list, None
    group_qq = message_info['group_qq']
    with open(ACTIVE_PATH) as f:
        active_dict:dict = load(f)
    if str(group_qq) not in active_dict.keys():
        active_dict.setdefault(str(group_qq), {'active': True, 'observer': True, 'entertain_mode': True,
                                               'jrrp': True, 'welcome': True, 'listen_at': True,
                                               'deck': True, 'draw': True, 'debug': True,
                                               'log' : False, 'recall': False})
    is_active = active_dict[str(group_qq)]['active']
    with open(ACTIVE_PATH, 'w') as f:
        dump(active_dict, f)
    return black_list, is_active


def set_active(message_info, b:bool, key='active'):
    """初始化群设置"""
    if not message_info['is_group']:
        return
    # from bot_command.event_handle import get_group_admin
    # if message_info['sender_qq'] not in get_group_admin(message_info):
    #     return
    with open(ACTIVE_PATH) as f:
        active_dict: dict = load(f)
    group_qq = message_info['group_qq']
    if str(group_qq) not in active_dict.keys():
        active_dict.setdefault(str(group_qq), {'active': True, 'observer': True, 'entertain_mode' : True,
                                               'jrrp': True, 'welcome' : True, 'listen_at' : True,
                                               'deck' : True, 'draw' : True, 'debug' : True,
                                               'log' : False, 'recall': False})
    active_dict[str(group_qq)][key] = b
    with open(ACTIVE_PATH, 'w') as f:
        dump(active_dict, f)


def is_at_bot(message_info)->bool:
    """判断是否处理at命令 以及bot是否被at"""
    message = message_info['message']
    if not message:
        return False
    index = message.find(']')
    if not index == -1:
        cq_msg = message_info['message'][:index+1]
    else:
        cq_msg = 0
    if cq_msg == f'[CQ:at,qq={message_info["bot_qq"]}]':
        with open(ACTIVE_PATH) as f:
            active_dict: dict = load(f)
        return True if active_dict[str(message_info['group_qq'])]['listen_at'] else False
    else:
        return False


def get_nickname(message):
    #group_qq = message.get('group_id')
    QQ = message.get('user_id')
    data:dict = read_json_file(DICE_DATA)
    # 初始化用户信息
    if str(QQ) not in data.keys():
        data.setdefault(str(QQ), {'nickname' : '', 'set' : 100, 'card' : {'default' : {}},
                                  'current_card' : 'default', 'favorability' : 0})
    # 无昵称时获取并添加昵称
    nickname:str = data[str(QQ)]['nickname']
    if not nickname:
        if not message.get('sender'):
            return
        if message.get('message_type') == 'group':
            card = message['sender']['card']
        else:
            card = None
        nickname = card if card else message['sender']['nickname']
        data[str(QQ)]['nickname'] = nickname
    # 保持昵称和绑定角色卡昵称一致
    card = data[str(QQ)]['current_card']
    if card != 'default':
        data[str(QQ)]['nickname'] = card
    with open(DICE_DATA, 'w') as f:
        dump(data, f)
    return nickname


def backup_files():
    path = BOT_PATH + '/data/data/'
    dice_path = BOT_PATH + '/data/dice_data/'
    backup_path = BOT_PATH + '/data/backup_data/'
    dice_backup = BOT_PATH + '/data/dice_backup/'
    date = strftime("%Y_%m_%d", localtime()) + '/'
    os.mkdir(backup_path + date)
    os.mkdir(dice_backup + date)
    file_names = list(os.walk(path))[0][2]
    for file_name in file_names:
        with open(path + file_name) as f:
            with open(backup_path + date + file_name, 'w') as fp:
                fp.write(f.read())
    send_private_msg(f'昨日BOT数据已备份到 {backup_path + date} 文件夹下', ADMIN_LIST[0])
    file_names = list(os.walk(dice_path))[0][2]
    for file_name in file_names:
        with open(dice_path + file_name) as f:
            with open(dice_backup + date + file_name, 'w') as fp:
                fp.write(f.read())
    send_private_msg(f'昨日DICE数据已备份到 {dice_backup + date} 文件夹下', ADMIN_LIST[0])


def log_handle(message_info):
    """判断群是否开启了日志并进行记录，结束后将日志文件上传到服务器上"""
    message: str = message_info['message']
    group_qq = message_info['group_qq']
    is_log = read_json_file(ACTIVE_PATH)[str(group_qq)]['log'] if message_info['is_group'] else False
    if is_log:
        print('logging', message[:20])
    if message_info['is_at_bot']:
        message = message[11 + len(str(message_info['bot_qq'])):].strip()
    if not message_info['is_group']:
        try:
            if message[1:4] == 'log':
                send_private_msg('日志记录只能用于群聊中哦', message_info['sender_qq'])
                return
        except:
            return
    message = message[1:]
    if not message[:3] == 'log' and not is_log:
        return
    path = BOT_PATH + '/data/log_data/'
    log_path = f'{path}{group_qq}.txt'
    command = message[3:].strip()
    if message[:3] == 'log' and not command:
        send_string = '跑团日志记录\n.log new //新建日志并开始记录\n.log on //开始记录\n.log off //暂停记录\n' \
                      '.log end //完成记录并发送日志文件'
    elif message[:3] == 'log' and command == 'on':
        if is_log:
            send_string = BOT_NAME + '正在记录中哦'
        else:
            change_json_file(ACTIVE_PATH, group_qq, 'log', True)
            send_string = BOT_NAME + '开始记录日志，可使用.log off暂停记录'
    elif message[:3] == 'log' and command == 'off':
        if not is_log:
            send_string = BOT_NAME + '日志记录已经暂停了'
        else:
            change_json_file(ACTIVE_PATH, group_qq, 'log', False)
            send_string = BOT_NAME + '暂停记录日志，可使用.log on恢复记录'
    elif message[:3] == 'log' and command == 'end':
        if os.path.exists(log_path):
            log_name = str(group_qq) +strftime("_%Y_%m_%d_%H_%M_%S", localtime())
            from shutil import copyfile
            copyfile(log_path, f'/var/www/html/{log_name}.txt')
            send_string = f'{BOT_NAME}已完成日志记录并上传到{SERVER_IP}:80/{log_name}.txt，可直接点击链接下载'
            os.remove(log_path)
            change_json_file(ACTIVE_PATH, group_qq, 'log', False)
        else:
            send_string = '请先使用.log new创建新的日志'
    elif message[:3] == 'log' and command == 'new':
        change_json_file(ACTIVE_PATH, group_qq, 'log', True)
        with open(log_path, 'w') as f:
            f.write('新日志记录开始\n\n')
        send_string = BOT_NAME + '已开始记录日志,使用.log end可结束日志记录'
    elif is_log:
        time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        nickname = message_info['nickname']
        QQ = message_info['sender_qq']
        with open(log_path, 'a+') as f:
            f.write(f'{nickname}({QQ}) {time}\n{message_info["message"]}\n\n')
        send_string = None
    else:
        send_string = None
    if send_string:
        send_public_msg(send_string, group_qq)


def heart_beat_check():
    url = f''
    try:
        res = requests.get(url, timeout=8)
        if not res.status_code == 200:
            print('heart-beat check request failed: status is not 200')
    except requests.RequestException as e:
        print("heart-beat check request failed: time out", e)
