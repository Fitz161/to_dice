from json import load, dump
import requests
from command.command import send_private_msg, send_public_msg
from config import DATA_PATH, MEMO_INFO_PATH, CPU_INFO_PATH


admin_command_dict = {}

"""管理员命令的装饰器"""
def add_admin_command(command):
    def add_func(func):
        admin_command_dict[command] = func
    return add_func


@add_admin_command("重置")
def reset(message_info):
    with open(DATA_PATH) as f:
        data_dict = load(f)
    for name in data_dict.keys():
        data_dict[name]["today"] = 0
    with open(DATA_PATH, "w") as f:
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