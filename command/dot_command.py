import requests

from config import apiBaseUrl, apiGroupInfo, ADMIN_LIST, LANGUAGE_DICT
from command.command import send_public_msg, send_private_msg, send_long_msg


def dot_send_msg(message_info:dict):
    raw_message = message_info['message'][5:].strip()
    if message_info['is_group']:
        api_url = apiBaseUrl + apiGroupInfo
        data = {
            'group_id':message_info.get('group_qq')
        }
        response = requests.post(api_url,data=data)
        if response.status_code == 200:
            group_name = response.json()['data']['group_name']
            send_string = f'来自群:{group_name},QQ:{message_info["sender_qq"]}的消息:\n{raw_message}'
            send_private_msg(send_string, ADMIN_LIST[0])
        else:
            return
    else:
        send_string = f'来自QQ:{message_info["sender_qq"]}的消息:\n{raw_message}'
        send_private_msg(send_string, ADMIN_LIST[0])


def show_command_doc(message_info):
    if message_info['message'][5:].strip() == '翻译':
        send_string = '支持翻译的语言:\n'
        for language in LANGUAGE_DICT:
            send_string += language + ' '
    elif message_info['message'][5:].strip() == '翻译':
        send_string = '搜索格式 待搜索的词\n百度：百度百科\n搜索1：wikipedia(暂不可用)\n搜索2：萌娘百科\n搜索3：touhouwiki\n'
    else:
        send_string = '签到/打卡\n单抽/十连/百连1-7\n要礼物 热榜\n点歌 /点歌\n' \
                      '搜索格式:\n百度/搜索1-3 内容\n翻译成 冷知识' \
                      '/send向管理员发送消息\n/bot on /bot off可以开启/关闭bot\n如果想让bot退群，请输入/leave哦'
    send_long_msg(message_info, send_string)



def calculate_phasor(message_info):
    from math import sin, cos, radians, sqrt, atan, degrees
    raw_message:str = message_info['message'][7:]
    if raw_message[0] == '+':
        try:
            args:list = list(map(lambda x:int(x), raw_message[1:].split()))
            real = args[0] * cos(radians(args[1])) + args[2] * cos(radians(args[3]))
            imag = args[0] * sin(radians(args[1])) + args[2] * sin(radians(args[3]))
            magnitude = sqrt(real ** 2 + imag ** 2)
            angle = degrees(atan(float(real) / imag)) if imag != 0 else 0
            send_string = f'{args[0]}e^{args[1]}j + {args[2]}e^{args[3]}j = ' + '%.2fe^%.2fj'%(magnitude,angle)
            if message_info['is_private']:
                send_private_msg(send_string, message_info['sender_qq'])
            elif message_info['is_group']:
                send_public_msg(send_string, message_info['group_qq'])
        except Exception as e:
            send_private_msg(e, message_info['sender_qq'])
    elif raw_message[0] == '-':
        try:
            args: list = list(map(lambda x:int(x), raw_message[1:].split()))
            real = args[0] * cos(radians(args[1])) - args[2] * cos(radians(args[3]))
            imag = args[0] * sin(radians(args[1])) - args[2] * sin(radians(args[3]))
            magnitude = sqrt(real ** 2 + imag ** 2)
            angle = degrees(atan(float(real) / imag)) if imag != 0 else 0
            send_string = f'{args[0]}e^{args[1]}j + {args[2]}e^{args[3]}j = ' + '%.2fe^%.2fj'%(magnitude,angle)
            if message_info['is_private']:
                send_private_msg(send_string, message_info['sender_qq'])
            elif message_info['is_group']:
                send_public_msg(send_string, message_info['group_qq'])
        except Exception as e:
            send_private_msg(e, message_info['sender_qq'])
    elif raw_message[0] == '*':
        try:
            args: list = list(map(lambda x:int(x), raw_message[1:].split()))
            real = args[0] * args[2]
            imag = (args[1] + args[3]) % 360
            send_string = f'{args[0]}e^{args[1]}j * {args[2]}e^{args[3]}j = ' + '%.2fe^%.2fj'%(real, imag)
            if message_info['is_private']:
                send_private_msg(send_string, message_info['sender_qq'])
            elif message_info['is_group']:
                send_public_msg(send_string, message_info['group_qq'])
        except Exception as e:
            send_private_msg(e, message_info['sender_qq'])
    elif raw_message[0] == '/':
        try:
            args: list = list(map(lambda x:int(x), raw_message[1:].split()))
            real = float(args[0]) / args[2] if int(args[2]) != 0 else 0
            imag = (args[1] - args[3]) % 360
            if not real:
                send_string = '分母不能为等于或接近0的数'
            else:
                send_string = f'{args[0]}e^{args[1]}j * {args[2]}e^{args[3]}j = ' + '%.2fe^%.2fj'%(real, imag)
            if message_info['is_private']:
                send_private_msg(send_string, message_info['sender_qq'])
            elif message_info['is_group']:
                send_public_msg(send_string, message_info['group_qq'])
        except Exception as e:
            send_private_msg(e, message_info['sender_qq'])
    else:
        send_string = '表达式错误或不支持'
        if message_info['is_private']:
            send_private_msg(send_string, message_info['sender_qq'])
        elif message_info['is_group']:
            send_public_msg(send_string, message_info['group_qq'])


def expression(message_info):
    import re, random
    raw_str = message_info['message'][2:]
    raw_str = raw_str.replace('x', '*').replace('X', '*').replace('d', 'D')
    print(raw_str)
    pattern = re.compile('\d{0,2}D\d+')
    pattern2 = re.compile('(\d{0,2})D(\d+)')
    offset = 0
    # print(re.search(pattern, raw_str))
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
        # print(raw_str)
        offset += match.span(0)[1] - len(match.group(0)) + len(num_str)
        # print('offset',offset)
    print(raw_str)
    try:
        send_string = f'{message_info["message"][2:]}={raw_str}={str(round(eval(raw_str)))}'
        print(send_string)
    except:
        send_string = '表达式无效'
    if message_info['is_private']:
        send_private_msg(send_string, message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])