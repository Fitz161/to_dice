from json import load, dump
import requests
from bot_command.command import send_private_msg, send_public_msg
from config import DATA_PATH, MEMO_INFO_PATH, CPU_INFO_PATH, SIGN_PATH


admin_command_dict = {}

"""管理员命令的装饰器"""
def add_admin_command(command):
    def add_func(func):
        admin_command_dict[command] = func
    return add_func


@add_admin_command("重置")
def reset(message_info):
    with open(SIGN_PATH) as f:
        data_dict = load(f)
    for name in data_dict.keys():
        data_dict[name]["today"] = 0
    with open(SIGN_PATH, "w") as f:
        dump(data_dict, f)


def server_stat()->str:
    mem = {}
    with open(MEMO_INFO_PATH) as f:
        lines = f.readlines()
    for line in lines:
        if len(line) < 2:
            continue
        name = line.split(':')[0]
        var = line.split(':')[1].split()[0]
        mem[name] = float(var)
    mem['MemUsed'] = mem['MemTotal'] - \
        mem['MemFree'] - mem['Buffers'] - mem['Cached']
    mem_avg = '内存使用率:{}%\n已使用内存:{}GB\n总内存:{}GB\nBuffers:{}GB\n'.format(int(round(mem['MemUsed'] / mem['MemTotal'] * 100)),
                                                                       round(mem['MemUsed'] / (1024 * 1024), 2),
                                                                       round(mem['MemTotal'] / (1024 * 1024), 2),
                                                                       round(mem['Buffers'] / (1024 * 1024), 2))
    with open(CPU_INFO_PATH) as f:
        con = f.read().split()
    cpu_avg = '5分钟内CPU负载:{}\n10分钟内CPU负载:{}\n15分钟内CPU负载:{}'.format(con[0], con[1], con[2])
    send_string = mem_avg + cpu_avg
    print(send_string)
    return send_string


def bot_status()->str:
    api_url = 'http://127.0.0.1:5700/get_status'
    text = requests.post(api_url).json()
    if text['data']['online']:
        return "bot运行正常\n"
    else:
        return "bot已下线\n"


@add_admin_command('状态')
def show_status(message_info: dict):
    send_string = bot_status() + server_stat()
    if message_info['is_private']:
        send_private_msg(send_string, message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])


@add_admin_command('删库')
def bot_exit(message_info):
    send_string = '跑路'
    if message_info['is_private']:
        send_private_msg(send_string, message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])
    exit()


@add_admin_command('黑名单')
def black_list(message_info):
    try:
        operate_type, qq = message_info['message'][3:].strip().split()
    except:
        return
    with open(DATA_PATH) as f:
        total_data: dict = load(f)
    black_list: list = total_data['black_list']
    if operate_type == 'add':
        black_list.append(int(qq)) if int(qq) not in black_list else None
        send_string = f'黑名单添加{qq}成功'
    elif operate_type == 'del':
        if int(qq) in black_list:
            black_list.remove(int(qq))
            send_string = f'从黑名单删除{qq}成功'
        else:
            send_string = f'{qq}不在黑名单中'
    elif operate_type == 'show':
        send_string = '黑名单:\n' + str(black_list)
    else:
        send_string = None
    total_data['black_list'] = black_list
    with open(DATA_PATH, 'w') as f:
        dump(total_data, f)
    if send_string:
        send_private_msg(send_string, message_info['sender_qq'])


@add_admin_command('白名单')
def white_list(message_info):
    try:
        operate_type, qq = message_info['message'][3:].strip().split()
    except:
        return
    with open(DATA_PATH) as f:
        total_data: dict = load(f)
    white_list: list = total_data['white_list']
    if operate_type == 'add':
        white_list.append(int(qq)) if int(qq) not in white_list else None
        send_string = f'白名单添加{qq}成功'
    elif operate_type == 'del':
        if int(qq) in white_list:
            white_list.remove(int(qq))
            send_string = f'从白名单删除{qq}成功'
        else:
            send_string = f'{qq}不在白名单中'
    elif operate_type == 'show':
        send_string = '白名单:\n' + str(white_list)
    else:
        send_string = None
    total_data['black_list'] = white_list
    with open(DATA_PATH, 'w') as f:
        dump(total_data, f)
    if send_string:
        send_private_msg(send_string, message_info['sender_qq'])


@add_admin_command('问候语')
def black_list(message_info):
    try:
        operate_type, qq = message_info['message'][3:].strip().split()
    except:
        return
    with open(DATA_PATH) as f:
        total_data: dict = load(f)
    send_list: list = total_data['send_list']
    if operate_type == 'add':
        send_list.append(int(qq)) if int(qq) not in send_list else None
        send_string = f'定时问候列表中添加{qq}成功'
    elif operate_type == 'del':
        if int(qq) in send_list:
            send_list.remove(int(qq))
            send_string = f'从定时问候列表中删除{qq}成功'
        else:
            send_string = f'{qq}不在定时问候列表中'
    elif operate_type == 'show':
        send_string = '定时问候列表:\n' + str(send_list)
    else:
        send_string = None
    total_data['send_list'] = send_list
    with open(DATA_PATH, 'w') as f:
        dump(total_data, f)
    send_private_msg(send_string, message_info['sender_qq'])


def bot_on(message_info, is_active):
    from config import BOT_NAME
    if not is_active:
        send_string = BOT_NAME + '可没有在偷懒哦'
    else:
        send_string = BOT_NAME + '已经开始工作了哦'
    if message_info['is_private']:
        send_private_msg(send_string, message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])