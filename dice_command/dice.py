import re
from random import randint

from bot_command.command import read_json_file
from config import DICE_DATA


def r_expression(message_info):
    raw_str:str = message_info['message'][2:]
    nickname = message_info['nickname']
    QQ = message_info['sender_qq']
    raw_str = raw_str.upper().replace('X', '*')
    print(raw_str)
    illegal_char = re.search('[^0-9DPKBHS#+-/*]', raw_str)
    if illegal_char:
        dice_name = '有关 ' + raw_str[illegal_char.start():] + ' 的'
    else:
        dice_name = ''
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
            return send_string[:-1]
        else:
            send_string = nickname + '掷出了' + dice_name + '骰子' + time_str + '次:\n'
            for index in range(times):
                print(point_express)
                send_str, result = express(point_express)
                if result is None:
                    return send_str
                send_string += send_str + '\n'
            return send_string[:-1]
    else:
        point_express:str = raw_str
        send_string = nickname + '掷出了' + dice_name + '骰子,结果是什么呢\n'
        send_str, result = express(point_express)
        if result is None:
            return send_str
        send_string += send_str + '\n'
        return send_string[:-1]


def express(raw_str):
    """有两个返回值，第二个返回值为None时表示主函数r_expression直接return第一个返回值"""
    temp = raw_str
    pattern = re.compile('(\d{0,2}D\d+)(K{0,1}\d+)')
    pattern2 = re.compile('(\d{0,2})D(\d{1,3})')
    pattern3 = re.compile('([PB])(\d{0,2})')
    offset = 0
    #对含有D和K的掷骰表达式进行处理
    while re.search(pattern, raw_str[offset:]):
        match = re.search(pattern, raw_str[offset:])
        match2 = re.search(pattern2, match.group(0))
        times, limit = map(int, match2.groups())
        times = 1 if not times else times
        if limit < 0:
            return  '你见过负数面的骰子吗？', None
        elif limit > 100:
            return '你给我找个面数超过100的骰子？', None
        try:
            count = int(match.group(2)[1:])
            if count > 9:
                return '好多好多骰子啊（晕', None
            elif count > times:
                return '骰子数目好像不对吧，您再算算？', None
        except:
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
        # 奖惩骰消息的偏移量和算数表达式的偏移量
        while re.search(pattern3, exp_string[exp_offset:]):
            exp_match = re.search(pattern3, exp_string[exp_offset:])
            msg_match = re.search(pattern3, msg_string[msg_offset:])
            print(exp_match.span(0), exp_match.group(0))
            # span获取match的范围，group(0)获得match到的内容
            type, times = exp_match.groups()
            times = 1 if not times else int(times)
            print(times, type)
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
            msg_offset += msg_match.span(0)[1] - len(msg_match.group(0)) + len(msg_str)
            exp_offset += exp_match.span(0)[1] - len(exp_match.group(0)) + len(exp_str)
    try:
        if raw_str.__contains__('P') or raw_str.__contains__('B'):
            point = str(round(eval(exp_string)))
            send_string = f'{raw_str}={msg_string}={exp_string}={point}'
        else:
            point = str(round(eval(raw_str)))
            send_string = f'{temp}={raw_str}={point}'
        return send_string, point
    except:
        return '命令或掷骰表达式输入错误', None

