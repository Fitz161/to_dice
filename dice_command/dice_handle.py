import re, random
from json import load, dump
import traceback

from dice_command.dice import *
from bot_command.dot_command import dot_send_msg, show_command_doc, today_fortune, calculate_phasor
from config import DICE_DATA, BOT_NAME, ADMIN_LIST
from bot_command.command import send_private_msg, send_public_msg, read_json_file, add_command, send_long_msg


@add_command('.')
def main_handle(message_info):
    try:
        develop_str = '程序猿正在爆肝开发中'
        message = message_info['message'][1:]
        group_qq = message_info['group_qq']
        QQ = message_info['sender_qq']
        nickname = message_info['nickname']
        if message == 'r':
            set_point = read_json_file(DICE_DATA)[str(QQ)]['set']
            point = random.randint(1, set_point)
            send_string = f'{nickname}掷出了一颗骰子，结果会是怎样呢，真令人期待啊\nD{set}={point}'
        elif message[:5] == 'rules':
            send_string = develop_str
        elif message[1:2] == 'r':
            send_message = r_expression(message_info)
        elif message[1:5] == 'send':
            send_message = dot_send_msg(message_info)
        elif message[1:5] == 'help':
            send_message = show_command_doc(message_info)
        elif message[1:] == 'jrrp':
            send_message = today_fortune(message_info)
        elif message[1:7] == 'phasor':
            send_message = calculate_phasor(message_info)
        send_long_msg(message_info)
        if not message_info['is_group']:
            return
        from bot_command.event_handle import get_group_admin, leave_group
        if message[1:] == 'leave' or message[1:] == 'dismiss':
            if message_info['sender_qq'] in get_group_admin(message_info):
                leave_group(message_info)
            else:
                send_public_msg('请让管理员发送该命令', message_info['group_qq'])
        elif message[1:] == 'bot off':
            if not message_info['sender_qq'] in get_group_admin(message_info):
                send_public_msg(BOT_NAME + '只聆听管理员的召唤哦', message_info['group_qq'])
            else:
                from main_handle import set_active
                set_active(message_info, False)
    except:
        send_private_msg(message_info['message'] + '\n' + traceback.format_exc(), ADMIN_LIST[1])




