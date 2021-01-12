import requests
from json import dump
import random

from config import apiBaseUrl, apiGroupInfo, LANGUAGE_DICT, DICE_DATA, OB_DATA, BOT_NAME, ACTIVE_PATH, NAME_DATA
from bot_command.command import change_json_file, read_json_file, get_nickname


def dot_send_msg(message_info:dict):
    """向bot管理员发送消息"""
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
        else:
            return
    else:
        send_string = f'来自QQ:{message_info["sender_qq"]}的消息:\n{raw_message}'
    return send_string


def show_command_doc(message_info):
    command = message_info['message'][5:].strip()
    if not command:
        send_string = '签到 打卡\n单抽 十连 百连[1-7]\n要礼物 热榜\n点歌/点歌 网易云 [歌名]\n冷知识 av BV\n' \
                      '百度/搜索[1-3] [内容]\n翻译成[语言] [文本]\n热评[条数](编号) [歌名]\n' \
                      '/send向管理员发送消息\n/bot on /bot off可以开启/关闭bot\n如果想让bot退群，请输入/leave哦'
    elif command == '翻译':
        send_string = '翻译格式:\n翻译成[目标语言] [带翻译文本]支持翻译的语言:\n'
        for language in LANGUAGE_DICT:
            send_string += language + ' '
    elif command == '搜索':
        send_string = '搜索格式:[格式] [待搜索的词]\n可用搜索格式:\n百度：百度百科\n搜索1：wikipedia(暂不可用)' \
                      '\n搜索2：萌娘百科\n搜索3：touhouwiki\n'
    elif command == '热评':
        send_string = '网易云热评格式:\n热评[显示热评条数][歌曲编号(可选)] [歌名]\n热评条数,歌曲编号要为一位数字'
    elif command == '点歌':
        send_string = '点歌格式:\n点歌[歌曲编号(可选)] [歌曲名]\n默认使用网易云,点歌命令前加/可切换成QQ音乐点歌'
    elif command == '抽卡':
        send_string = '抽卡格式:\n[抽卡类型][卡包编号]\n抽卡类型包括 单抽 十连 百连\n卡包编号可选数字1-7'
    elif command == 'phasor':
        send_string = '命令格式:\n/phasor[运算符] [第一个相量的模] [角度(rad)] [第二个相量的模] [角度(rad)]'
    elif command == '词云图':
        send_string = '命令格式:\n词云图[模式][字体类型(可选)] [文本]\n命令说明:\n[模式]参数可选1-5,1表示使用[文本]制作词云图\n' \
                      '2-5表示使用不同搜索引擎搜索[文本]关键字,并使用搜索到的内容绘制词云图\n' \
                      '6表示使用知乎热榜前50条制作词云图\n7表示使用网易云热评制作词云图,其命令格式为\n' \
                      '词云图7[歌曲编号][字体类型(可选)] [歌名]\n[字体类型]参数可选数字1-4, 1-宋体 2-黑体 3-书宋 4-楷体'
    else:
        send_string = '没有找到这个命令呢\n可以试试:/help\n'
        command_list = ['翻译', '搜索', '热评', '点歌', '抽卡', 'phasor', '词云图']
        for item in command_list:
            if item.__contains__(command):
                send_string += item + '\n'
    return send_string[:-1]


def calculate_phasor(message_info):
    """计算相量"""
    from math import sin, cos, radians, sqrt, atan, degrees
    raw_message:str = message_info['message'][7:]
    if raw_message[0] == '+':
        args:list = list(map(lambda x:float(x), raw_message[1:].split()))
        real = args[0] * cos(radians(args[1])) + args[2] * cos(radians(args[3]))
        imag = args[0] * sin(radians(args[1])) + args[2] * sin(radians(args[3]))
        magnitude = sqrt(real ** 2 + imag ** 2)
        angle = degrees(atan(float(real) / imag)) if imag != 0 else 0
        send_string = f'{args[0]}e^{args[1]}j + {args[2]}e^{args[3]}j = ' + '%.2fe^%.2fj'%(magnitude,angle)
    elif raw_message[0] == '-':
        args: list = list(map(lambda x:float(x), raw_message[1:].split()))
        real = args[0] * cos(radians(args[1])) - args[2] * cos(radians(args[3]))
        imag = args[0] * sin(radians(args[1])) - args[2] * sin(radians(args[3]))
        magnitude = sqrt(real ** 2 + imag ** 2)
        angle = degrees(atan(float(real) / imag)) if imag != 0 else 0
        send_string = f'{args[0]}e^{args[1]}j + {args[2]}e^{args[3]}j = ' + '%.2fe^%.2fj'%(magnitude, angle)
    elif raw_message[0] == '*':
        args: list = list(map(lambda x:float(x), raw_message[1:].split()))
        real = args[0] * args[2]
        imag = (args[1] + args[3]) % 360
        send_string = f'{args[0]}e^{args[1]}j * {args[2]}e^{args[3]}j = ' + '%.2fe^%.2fj'%(real, imag)
    elif raw_message[0] == '/':
            args: list = list(map(lambda x:float(x), raw_message[1:].split()))
            real = float(args[0]) / args[2] if float(args[2]) != 0 else 0
            imag = (args[1] - args[3]) % 360
            if not real:
                send_string = '分母不能为等于或接近0的数'
            else:
                send_string = f'{args[0]}e^{args[1]}j * {args[2]}e^{args[3]}j = ' + '%.2fe^%.2fj'%(real, imag)
    else:
        send_string = '表达式错误或不支持'
    return send_string


def expression(message_info):
    import re, random
    raw_str = message_info['message'][2:]
    raw_str = raw_str.replace('x', '*').replace('X', '*').replace('d', 'D')
    print(raw_str)
    pattern = re.compile('\d{0,2}D\d{1,3}')
    pattern2 = re.compile('(\d{0,2})D(\d{1,3})')
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
    return send_string


def today_fortune(message_info):
    from config import ACTIVE_PATH
    from json import load
    with open(ACTIVE_PATH) as f:
        active_dict: dict = load(f)
    if message_info['is_group']:
        enable_jrrp = active_dict[str(message_info['group_qq'])]
        if not enable_jrrp:
            return
    from random import randint
    send_string = f'{message_info["nickname"]}\n今天的人品值是:{randint(1, 100)}'
    return send_string


def set_handle(message_info):
    qq = message_info['sender_qq']
    group_qq = message_info['group_qq']
    nickname = message_info['nickname']
    raw_str:str = message_info['message'][4:]
    if not raw_str:
        change_json_file(DICE_DATA, qq, 'set', 100)
        return f'已将{nickname}的默认骰类型更改为D100'
    if raw_str[:6] == 'setcoc':
        try:
            set_point = int(raw_str.strip())
            if set_point < 0 or set_point > 5:
                set_point = 0
        except:
            set_point = 0
        return
    else:
        try:
            set_point = int(raw_str.strip())
            if set_point > 0 and set_point <= 100:
                change_json_file(DICE_DATA, qq, 'set', set_point)
                return f'已将{nickname}的默认骰类型更改为D{set_point}'
        except:
            return


def observer_handle(message_info):
    if not message_info['is_group']:
        return'旁观模式: .ob (exit/list/clr/on/off)\n.ob //加入旁观可以看到他人暗骰结果.ob exit //退出旁观模式\n' \
              '.ob list //查看群内旁观者\n.ob clr //清除所有旁观者\n.ob on //全群允许旁观模式\n' \
              '.ob off //禁用旁观模式\n暗骰与旁观仅在群聊中有效'
    message:str = message_info['message'][3:]
    group_qq = message_info['group_qq']
    QQ = message_info['sender_qq']
    nickname = message_info['nickname']
    active_data = read_json_file(ACTIVE_PATH)
    if not active_data[str(group_qq)]['observer']:
        return BOT_NAME + '在此群的旁观者模式已被禁用哦'
    ob_data: dict = read_json_file(OB_DATA)
    if str(group_qq) not in ob_data.keys():
        ob_data.setdefault(str(group_qq), [])
    ob_list:list = ob_data.get(str(group_qq))
    message = message.strip()
    if not message:
        ob_list.append(QQ) if QQ not in ob_list else None
        with open(OB_DATA, 'w') as f:
            dump(ob_data, f)
        return f'{nickname}已经加到{BOT_NAME}的旁观列表了哦'
    elif message == 'exit':
        ob_list.remove(QQ) if QQ in ob_list else None
        with open(OB_DATA, 'w') as f:
            dump(ob_data, f)
        return f'{nickname}已经退出{BOT_NAME}的旁观列表了哦'
    elif message == 'list' or message == 'show':
        #ob_data = { k:v for k in ob_list for v in get_nickname(k)}
        if ob_list is None:
            return '当前没有任何旁观者哦'
        send_string = f'当前{BOT_NAME}的旁观列表中有:\n'
        for qq in ob_list:
            send_string += f'{get_nickname(qq)}\n({qq})\n'
        return send_string[:-1]
    elif message == 'clr' or message == 'clear':
        ob_data[str(group_qq)].clear()
        with open(OB_DATA, 'w') as f:
            dump(ob_data, f)
        return BOT_NAME + '已成功删除所有旁观者'
    elif message == 'on':
        if not active_data[str(group_qq)]['observer']:
            change_json_file(ACTIVE_PATH, group_qq, 'observer', True)
            return BOT_NAME + '在此群的旁观者模式成功开启'
        else:
            return BOT_NAME + '在此群的旁观者模式未被禁用哦'
    elif message == 'off':
        if active_data[str(group_qq)]['observer']:
            change_json_file(ACTIVE_PATH, group_qq, 'observer', False)
            return BOT_NAME + '在此群的旁观者模式成功禁用'
        else:
            return BOT_NAME + '在此群的旁观者模式未被开启哦'
    else:
        return '旁观模式: .ob (exit/list/clr/on/off)\n.ob //加入旁观可以看到他人暗骰结果.ob exit //退出旁观模式\n' \
               '.ob list //查看群内旁观者\n.ob clr //清除所有旁观者\n.ob on //全群允许旁观模式\n' \
               '.ob off //禁用旁观模式\n暗骰与旁观仅在群聊中有效'


def random_name(message_info):
    message:str = message_info['message'][5:].strip()
    nickname = message_info['nickname']
    send_string = f'emm 让我想想，{nickname}的随即昵称:\n'
    command_list = message.split()
    if command_list is None:
        return send_string + ''.join(get_random_name())
    elif len(command_list) == 1:
        if command_list[0] == 'cn':
            return send_string + ''.join(get_random_name(1, 'cn'))
        elif command_list[0] == 'en':
            return send_string + ''.join(get_random_name(1, 'en'))
        elif command_list[0] == 'enzh':
            return send_string + ''.join(get_random_name(1, 'enzh'))
        elif command_list[0] == 'jp':
            return send_string + ''.join(get_random_name(1, 'jp'))
        else:
            try:
                num = int(command_list[0])
                if num > 10:
                    return '请输入1-10直接的数字哦,太多了的话一时想不出来呢'
                elif num < 1:
                    return send_string + ''.join(get_random_name())
                return send_string + '  '.join(get_random_name(num))
            except:
                return send_string + ''.join(get_random_name())
    else:
        try:
            type = command_list[0]
            num = int(command_list[1])
        except:
            try:
                type = command_list[1]
                num = int(command_list[0])
            except:
                return send_string + ''.join(get_random_name())
        if num > 10:
            return '请输入1-10直接的数字哦,太多了的话一时想不出来呢'
        elif num < 1:
            return send_string + ''.join(get_random_name())
        if type == 'cn':
            return send_string + '  '.join(get_random_name(num, 'cn'))
        elif type == 'en':
            return send_string + '  '.join(get_random_name(num, 'en'))
        elif type == 'enzh':
            return send_string + '  '.join(get_random_name(num, 'enzh'))
        elif type == 'jp':
            return send_string + '  '.join(get_random_name(num, 'jp'))
        else:
            return send_string + ''.join(get_random_name())


def get_random_name(num=1, type='random'):
    name_list = []
    name_data:dict = read_json_file(NAME_DATA)
    if type == 'random':
        type_list = random.choices(['cn', 'en', 'enzh', 'jp'], k=num)
        cn_num = type_list.count('cn')
        en_num = type_list.count('en')
        enzh_num = type_list.count('enzh')
        jp_num = type_list.count('jp')
        if en_num:
            first_name = random.choices(name_data['first_name_en'], k=en_num)
            last_name = random.choices(name_data['last_name_en'], k=en_num)
            for i in range(en_num):
                name_list.append(first_name[i] + '·' + last_name[i])
        if cn_num:
            first_name = random.choices(name_data['first_name_cn'], k=cn_num)
            single_char = random.choices(name_data['single_char_cn'], k=cn_num * 2)
            for i in range(cn_num):
                name_list.append(first_name[i] + ''.join(single_char[i * 2: i * 2 + random.randint(1, 2)]))
        if enzh_num:
            first_name = random.choices(name_data['first_name_enzh'], k=enzh_num)
            last_name = random.choices(name_data['last_name_enzh'], k=enzh_num)
            for i in range(enzh_num):
                name_list.append(first_name[i] + '·' + last_name[i])
        if jp_num:
            first_name = random.choices(name_data['first_name_jp'], k=jp_num)
            last_name = random.choices(name_data['last_name_jp'], k=jp_num)
            for i in range(jp_num):
                name_list.append(first_name[i] + last_name[i])
        return  name_list
    else:
        if type == 'en':
            first_name = random.choices(name_data['first_name_en'], k=num)
            last_name = random.choices(name_data['last_name_en'], k=num)
            for i in range(num):
                name_list.append(first_name[i] + '·' + last_name[i])
        elif type == 'cn':
            first_name = random.choices(name_data['first_name_cn'], k=num)
            single_char = random.choices(name_data['single_char_cn'], k=num * 2)
            print(first_name, single_char)
            for i in range(num):
                name_list.append(first_name[i] + ''.join(single_char[i * 2: i * 2 + random.randint(1, 2)]))
        elif type == 'enzh':
            first_name = random.choices(name_data['first_name_enzh'], k=num)
            last_name = random.choices(name_data['last_name_enzh'], k=num)
            for i in range(num):
                name_list.append(first_name[i] + '·' + last_name[i])
        elif type == 'jp':
            first_name = random.choices(name_data['first_name_jp'], k=num)
            last_name = random.choices(name_data['last_name_jp'], k=num)
            for i in range(num):
                name_list.append(first_name[i] + last_name[i])
        return name_list