import re
from random import randint

from bot_command.command import read_json_file, send_private_msg, get_group_name
from config import DICE_DATA, ACTIVE_PATH, OB_DATA


def r_expression(message_info):
    """对所有掷骰表达式的处理函数"""
    raw_str:str = message_info['message'][2:]
    nickname = message_info['nickname']
    QQ = message_info['sender_qq']
    group_qq = message_info['group_qq']
    hide_str = f'惊！{nickname}好像偷偷骰了一颗骰子呢~'
    raw_str = raw_str.upper().replace('X', '*')
    print(raw_str, end=' ')
    illegal_char = re.search('[^0-9DPKBHS#+-/*]', raw_str)
    #判断是否有掷骰原因，并将原因分离出来
    if illegal_char:
        dice_name = '有关 ' + raw_str[illegal_char.start():] + ' 的'
        raw_str = raw_str[:illegal_char.start()]
    else:
        dice_name = ''
    if not raw_str:
        set_point = read_json_file(DICE_DATA)[str(QQ)]['set']
        point = randint(1, set_point)
        send_string = f'{nickname}掷出了{dice_name}骰子，结果会是怎样呢，真令人期待啊\nD{set_point}={point}'
        return send_string

    #判断是否为 直接发送最终点数(s) 或暗骰(h) s h均为可选参数 s需位于h前
    if raw_str[0] == 'S':
        is_skip = True
        try:
            if raw_str[1] == 'H':
                is_hide = True
                raw_str = raw_str[2:]
            else:
                raw_str = raw_str[1:]
                is_hide = False
        except:
            is_hide = False
            raw_str = raw_str[1:]
    elif raw_str[0] == 'H':
        raw_str = raw_str[1:]
        is_hide = True
        is_skip = False
    else:
        is_hide = False
        is_skip = False
    print(is_hide, is_skip, raw_str)
    #判断是否允许旁观
    if message_info['is_group']:
        active_data = read_json_file(ACTIVE_PATH)
        is_enable_ob = active_data[str(group_qq)]['observer']
    else:
        is_enable_ob = False

    if not raw_str:
        set_point = read_json_file(DICE_DATA)[str(QQ)]['set']
        point = randint(1, set_point)
        send_string = f'{nickname}掷出了{dice_name}骰子，结果会是怎样呢，真令人期待啊\nD{set_point}={point}'
        if not is_hide:
            return send_string
        else:
            group_name = get_group_name(group_qq)
            if not group_name:
                return send_string
            send_msg = f'在[{group_name}]({group_qq})中{send_string}'
            if not is_enable_ob:
                send_private_msg(send_msg, QQ)
            else:
                ob_list:list = read_json_file(OB_DATA).get(str(group_qq))
                ob_list.append(QQ) if QQ not in ob_list else None
                for QQ in ob_list:
                    send_private_msg(send_msg, QQ)
            return hide_str

    if raw_str.__contains__('#'):
        #使用相同表达式多次掷骰
        try:
            time, point_express = raw_str.split('#')
        except:
            return '命令或掷骰表达式输入错误。'
        time_str, times = express(time)
        if not times:
            times = 1
            time_str = '一'
        if times > 10 or times < 1:
            return f'掷骰轮数{time_str}超过了最大轮数了呢'
        if not point_express:
            point:int = read_json_file(DICE_DATA)[str(QQ)]['set']
            send_string = f'{nickname}掷出了{dice_name}骰子{times}次:\nD{point}='
            for index in range(times):
                send_string += str(randint(1, point)) + ', '
            if not is_hide:
                return send_string[:-1]
            else:
                group_name = get_group_name(group_qq)
                if not group_qq:
                    return send_string[:-1]
                send_msg = f'在[{group_name}]({group_qq})中{send_string[:-1]}'
                if not is_enable_ob:
                    send_private_msg(send_msg, QQ)
                else:
                    ob_list: list = read_json_file(OB_DATA).get(str(group_qq))
                    ob_list.append(QQ) if QQ not in ob_list else None
                    for QQ in ob_list:
                        send_private_msg(send_msg, QQ)
                return hide_str
        else:
            send_string = nickname + '掷出了' + dice_name + '骰子' + time_str + '次:\n'
            for index in range(times):
                send_str, result = express(point_express)
                if result is None:
                    return send_str
                if is_skip:
                    send_string += str(result) + ' '
                else:
                    send_string += send_str + '\n'
            if not is_hide:
                return send_string[:-1]
            else:
                group_name = get_group_name(group_qq)
                if not group_name:
                    return send_string[:-1]
                send_msg = f'在[{group_name}]({group_qq})中{send_string[:-1]}'
                if not is_enable_ob:
                    send_private_msg(send_msg, QQ)
                else:
                    ob_list: list = read_json_file(OB_DATA).get(str(group_qq))
                    ob_list.append(QQ) if QQ not in ob_list else None
                    for QQ in ob_list:
                        send_private_msg(send_msg, QQ)
                return hide_str
    else:
        point_express:str = raw_str
        send_string = nickname + '掷出了' + dice_name + '骰子,结果是什么呢\n'
        send_str, result = express(point_express)
        if result is None:
            return send_str
        if is_skip:
            send_string += str(result) + ' '
        else:
            send_string += send_str + '\n'
        if not is_hide:
            return send_string[:-1]
        else:
            group_name = get_group_name(group_qq)
            if not group_name:
                return send_string[:-1]
            send_msg = f'在[{group_name}]({group_qq})中{send_string[:-1]}'
            if not is_enable_ob:
                send_private_msg(send_msg, QQ)
            else:
                ob_list:list = read_json_file(OB_DATA).get(str(group_qq))
                ob_list.append(QQ) if QQ not in ob_list else None
                for QQ in ob_list:
                    send_private_msg(send_msg, QQ)
            return hide_str


def express(raw_str):
    """有两个返回值，第二个返回值为None时表示调用函数需直接return第一个返回值（即将消息发送）
    两个返回值均存在时，第一个为运算过程的str，第二个参数为最终结果（int）"""
    temp = raw_str
    pattern = re.compile('(\d{0,2}D\d{0,3})(K{0,1}\d{0,2})')
    pattern2 = re.compile('(\d{0,2})D(\d{0,3})')
    pattern3 = re.compile('([PB])(\d{0,2})')
    offset = 0
    #对含有D和K的掷骰表达式进行处理
    while re.search(pattern, raw_str[offset:]):
        match = re.search(pattern, raw_str[offset:])
        match2 = re.search(pattern2, match.group(0))
        times, limit = match2.groups()
        limit = 100 if not limit else int(limit)
        times = 1 if not times else int(times)
        if limit < 0:
            return  '你见过负数面的骰子吗？', None
        elif limit > 100:
            return '你给我找个面数超过100的骰子？', None
        k_express = match.group(2)
        if not k_express:
            count = -1
        elif k_express[0] == 'K':
            try:
                count = int(match.group(2)[1:])
                if count > 9:
                    return '好多好多骰子啊（晕', None
                elif count > times:
                    return '骰子数目好像不对吧，您再算算？', None
            except:
                count = 1
        else:
            count = -1
        if times == 1:
            num_str = str(randint(1, int(limit)))
        elif count == -1:
            if times == 1:
                num_str = str(randint(1, int(limit)))
            else:
                num_str = '('
                for i in range(0, int(times)):
                    random_num = randint(1, int(limit))
                    if i == 0:
                        num_str += str(random_num)
                    else:
                        num_str += '+' + str(random_num)
                num_str += ')'
        else:
            #掷骰表达式中含有K参数
            num_str = '('
            random_num = []
            for i in range(times):
                random_num.append(randint(1, limit))
            random_num.sort(reverse=True)
            if count == 1:
                num_str = str(random_num[0])
            else:
                for index, num in zip(range(count), random_num[:count]):
                    if index == 0:
                        num_str += str(num)
                    else:
                        num_str += '+' + str(num)
                num_str += ')'
        raw_str = raw_str.replace(match.group(0), num_str, 1)
        offset += match.span(0)[1] - len(match.group(0)) + len(num_str)

    #再对可能有的P和B参数进行处理
    exp_string = msg_string = raw_str
    if raw_str.__contains__('P') or raw_str.__contains__('B'):
        msg_offset = exp_offset = 0
        #奖惩骰消息的偏移量和对应算数表达式的偏移量
        while re.search(pattern3, exp_string[exp_offset:]):
            exp_match = re.search(pattern3, exp_string[exp_offset:])
            msg_match = re.search(pattern3, msg_string[msg_offset:])
            type, times = exp_match.groups()
            times = 1 if not times else int(times)
            if type == 'P':
                punish_list = []
                random_num = randint(1, 100)
                for i in range(times):
                    punish_list.append(randint(0, 10))
                max_num = max(punish_list)
                msg_str = f'{random_num}[惩罚骰:'
                for i in range(times):
                    msg_str += str(punish_list[i]) + ' '
                msg_str = msg_str[:-1] + ']'
                if max_num == 10:
                    exp_str = '100'
                elif max_num == 0:
                    exp_str = '0'
                else:
                    exp_str = f'{max_num}{random_num % 10}'
            elif type == 'B':
                reward_list = []
                random_num = randint(1, 100)
                for i in range(times):
                    reward_list.append(randint(0, 10))
                min_num = min(reward_list)
                msg_str = f'{random_num}[奖励骰:'
                for i in range(times):
                    msg_str += str(reward_list[i]) + ' '
                msg_str = msg_str[:-1] + ']'
                if min_num == 10:
                    exp_str = '100'
                elif min_num == 0:
                    exp_str = '0'
                else:
                    exp_str = f'{min_num}{random_num % 10}'
            else:
                msg_str = exp_str = ''
            msg_string = msg_string.replace(msg_match.group(0), msg_str, 1)
            exp_string = exp_string.replace(exp_match.group(0), exp_str, 1)
            # span获取match的范围，group(0)获得match到的内容
            msg_offset += msg_match.span(0)[1] - len(msg_match.group(0)) + len(msg_str)
            exp_offset += exp_match.span(0)[1] - len(exp_match.group(0)) + len(exp_str)
    print(raw_str)
    try:
        if raw_str.__contains__('P') or raw_str.__contains__('B'):
            point = round(eval(exp_string))
            send_string = f'{temp}={raw_str}={msg_string}={exp_string}={point}'
        else:
            point = round(eval(raw_str))
            send_string = f'{temp}={raw_str}={point}'
        return send_string, point
    except:
        return '命令或掷骰表达式输入错误', None

