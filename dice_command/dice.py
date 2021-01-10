import random
import re

from bot_command.command import read_json_file
from config import DICE_DATA


def r_expression(message_info):
    raw_str:str = message_info['message'][2:]
    nickname = message_info['nickname']
    QQ = message_info['sender_qq']
    raw_str = raw_str.upper().replace('X', '*')
    print(raw_str)
    all_pattern = '([0-9D]+)D([0-9D]+)'
    illegal_char = re.search('[^0-9Dpkbhs#+-/*]', raw_str).start()
    if illegal_char:
        dice_name = '有关 ' + raw_str[illegal_char:] + ' 的'
    else:
        dice_name = ''
    if raw_str.__contains__('#'):
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
                send_string += str(random.randint(1, point)) + ', '
            return send_string[:-1]
        else:
            send_string = nickname + '掷出了' + dice_name + '骰子' + time_str + '次:\n'
            for index in range(times):
                print(point_express)
                if point_express.__contains__('P'):
                    send_string += punish(point_express)
                elif point_express.__contains__('B'):
                    send_string += reward(point_express)
                elif point_express.__contains__('K'):
                    send_string = k_expression(point_express)
                else:
                    result = express(point_express)[0]
                    if not result:
                        return '命令或掷骰表达式输入错误'
                    send_string += result + '\n'
            return send_string[:-1]
    else:
        point_express:str = raw_str
        send_string = nickname + '掷出了' + dice_name + '骰子,结果是什么呢\n'
        if point_express.__contains__('P'):
            send_string += punish(point_express)
        elif point_express.__contains__('B'):
            send_string += reward(point_express)
        elif point_express.__contains__('K'):
            send_string = k_expression(point_express)
        else:
            result = express(point_express)[0]
            if not result:
                return '命令或掷骰表达式输入错误.'
            send_string += result + '\n'
        return send_string[:-1]


def express(raw_str):
    pattern = re.compile('\d{0,2}D\d{1,3}')
    pattern2 = re.compile('(\d{0,2})D(\d{1,3})')
    offset = 0
    while re.search(pattern, raw_str[offset:]):
        match = re.search(pattern, raw_str[offset:])
        match2 = re.search(pattern2, match.group(0))
        times, limit = match2.groups()
        times = 1 if not times else times
        if times == 1:
            num_str = str(random.randint(1, int(limit)))
        else:
            num_str = '('
            for i in range(0, int(times)):
                random_num = random.randint(1, int(limit))
                if i == 0:
                    num_str += str(random_num)
                else:
                    num_str += '+' + str(random_num)
            num_str += ')'
        raw_str = raw_str.replace(match.group(0), num_str, 1)
        offset += match.span(0)[1] - len(match.group(0)) + len(num_str)
    print(raw_str)
    try:
        send_string = f'{raw_str}={str(round(eval(raw_str)))}'
        return send_string, round(eval(raw_str))
    except:
        return None, None


def punish(expression):
    return '程序猿正在爆肝开发中'


def reward(expression):
    return '程序猿正在爆肝开发中'


def k_expression(expression):
    return '程序猿正在爆肝开发中'