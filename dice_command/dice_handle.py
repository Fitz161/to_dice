import traceback

from dice_command.dice_expression import *
from dice_command.dot_command import *
from config import BOT_NAME, ADMIN_LIST
from bot_command.command import send_private_msg, send_public_msg, send_long_msg


def main_handle(message_info):
    try:
        send_string = '程序猿正在爆肝开发中'
        message = message_info['message'][1:]
        group_qq = message_info['group_qq']
        QQ = message_info['sender_qq']
        nickname = message_info['nickname']
        if message[:3] == 'set':
            send_string = set_handle(message_info)
        elif message[:5] == 'rules':
            pass
        elif message[:1] == 'r':
            send_string = r_expression(message_info)
        elif message[:4] == 'help':
            send_string = show_command_doc(message_info)
        elif message == 'jrrp':
            send_string = today_fortune(message_info)
        elif message[:2] == 'ob':
            send_string = observer_handle(message_info)
        elif message[:4] == 'name':
            send_string = random_name(message_info)
        elif message[:4] == 'send':
            send_string = dot_send_msg(message_info)
        elif message[:6] == 'phasor':
            send_string = calculate_phasor(message_info)
        else:
            send_string = None
        if not send_string:
            return
        send_long_msg(message_info, send_string)
        #只有群消息才会触发的命令
        if not message_info['is_group']:
            return
        from bot_command.event_handle import get_group_admin, leave_group
        if message[1:] == 'leave' or message[1:] == 'dismiss':
            if QQ in get_group_admin(message_info):
                leave_group(message_info)
            else:
                send_public_msg('请让管理员发送该命令', group_qq)
        elif message[1:] == 'bot off':
            if not message_info['sender_qq'] in get_group_admin(message_info):
                send_public_msg(BOT_NAME + '只聆听管理员的召唤哦', group_qq)
            else:
                from main_handle import set_active
                set_active(message_info, False)
    except:
        #将报错信息发给管理员
        send_private_msg(message_info['message'] + '\n' + traceback.format_exc(), ADMIN_LIST[1])




