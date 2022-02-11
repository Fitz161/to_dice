import traceback

from dice_command.dice_expression import *
from dice_command.dot_command import *
from config import BOT_NAME, ADMIN_LIST
from bot_command.command import send_private_msg, send_public_msg, send_long_msg


def main_handle(message_info):
    try:
        message:str = message_info['message'][1:]
        group_qq = message_info['group_qq']
        QQ = message_info['sender_qq']
        nickname = message_info['nickname']
        if message[:2].lower() == 'ra' or message[:2] == 'rc':
            send_string = random_check(message_info)
        elif message[:3].lower() == 'set':
            send_string = set_handle(message_info)
        elif message[:3].lower() == 'coc':
            send_string = f'{nickname}的调查员作成:'
            trans_tab = str.maketrans(',', ' ', " '{}")
            try:
                cards = get_coc_card(int(message[3:]))
                for card in cards:
                    send_string += str(card).translate(trans_tab) + '^^'
                send_string = send_string[:-2]
            except:
                send_string += str(get_coc_card()[0]).translate(trans_tab)
        elif message[:2].lower() == 'dk':
            send_string = sign_in(message_info)
        elif message[:5].lower() == 'rules':
            send_string = '程序猿正在爆肝开发中'
        elif message[:1].lower() == 'r':
            send_string = r_expression(message_info)
        elif message[:2].lower() == 'st':
            send_string =st_handle(message_info)
        elif message[:2].lower() == 'sc':
            send_string = san_check(message_info)
        elif message[:2].lower() == 'li':
            send_string = temporary_insane()
        elif message[:4].lower() == 'help':
            send_string = show_command_doc(message_info)
        elif message[:4].lower() == 'draw':
            send_string = draw_card(message_info)
        elif message.lower() == 'jrrp':
            send_string = today_fortune(message_info)
        elif message[:2].lower() == 'ob':
            send_string = observer_handle(message_info)
        elif message[:4].lower() == 'name':
            send_string = random_name(message_info)
        elif message[:2].lower() == 'nn':
            send_string = set_name(message_info)
        elif message[:4].lower() == 'send':
            send_string = dot_send_msg(message_info)
        elif message[:6].lower() == 'phasor':
            send_string = calculate_phasor(message_info)
        else:
            send_string = None
        #只有群消息才会触发的命令
        if message_info['is_group']:
            from bot_command.event_handle import get_group_admin, leave_group
            if message.lower() == 'leave' or message.lower() == 'dismiss':
                if QQ in get_group_admin(message_info):
                    leave_group(message_info)
                else:
                    send_string = '请让管理员发送该命令'
            elif message.lower() == 'bot off':
                if not message_info['sender_qq'] in get_group_admin(message_info):
                    send_string = BOT_NAME + '只聆听管理员的召唤哦'
                else:
                    from main_handle import set_active
                    set_active(message_info, False)
                    send_string = BOT_NAME + '已经去休息了哦'
            elif message.lower().find('recall') != -1:
                from bot_command.admin_command import recall_on
                if message.lower().find('on'):
                    recall_on(message_info, True)
                    return
                elif message.lower().find('off'):
                    recall_on(message_info, False)
                    return
                else:
                    send_string = '请使用.recall on 和.recall off'

        if not send_string:
            return
        send_long_msg(message_info, send_string)
    except:
        #将报错信息发给管理员
        send_private_msg(message_info['message'] + '\n' + traceback.format_exc(), ADMIN_LIST[1])




