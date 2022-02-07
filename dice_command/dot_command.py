import re

import requests
from json import dump
import random

from config import *
from bot_command.command import change_json_file, read_json_file, get_nickname, text_to_img
from dice_command.dice_expression import express


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
    if not raw_str.strip():
        change_json_file(DICE_DATA, qq, 'set', 100)
        return f'已将{nickname}的默认骰类型更改为D100'
    if raw_str[:6] == 'coc':
        try:
            set_point = int(raw_str[6:].strip())
            if set_point < 0 or set_point > 5:
                set_point = 3
        except:
            set_point = 3
        data:dict = read_json_file(DATA_PATH)
        data['setcoc'][str(group_qq)] = set_point
        with open(DATA_PATH, 'w') as f:
            dump(data, f)
        if set_point == 0:
            return '默认检定房规已设置：' + str(set_point) + '\n出1大成功\n不满50出96-100大失败，满50出100大失败'
        elif set_point == 1:
            return '默认检定房规已设置：' + str(set_point) + '不满50出1大成功，满50出1-5大成功\n' \
                                                   '不满50出96-100大失败，满50出100大失败'
        elif set_point == 2:
            return '默认检定房规已设置：' + str(set_point) + '\n出1-5且<=成功率大成功\n出100或出96-99且>成功率大失败'
        elif set_point == 3:
            return '默认检定房规已设置：' + str(set_point) + '\n出1-5大成功\n出96-100大失败'
        elif set_point == 4:
            return '默认检定房规已设置：' + str(set_point) + '\n出1-5且<=成功率/10大成功\n' \
                                                   '不满50出>=96+成功率/10大失败，满50出100大失败'
        elif set_point == 5:
            return '默认检定房规已设置：' + str(set_point) + '\n出1-2且<成功率/5大成功\n' \
                                                   '不满50出96-100大失败，满50出99-100大失败'
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
    # command_list = message.split()
    # 中间出现空格时也能正确处理
    pattern = re.compile('([cenzhjp]+) *(\d{1,2})')
    match = re.search(pattern, message)
    if match:
        command_list = list(match.groups())
        for item in command_list:
            if item == '':
                command_list.remove(item)

    else:
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


def set_name(message_info):
    message: str = message_info['message'][3:]
    nickname = message_info['nickname']
    QQ = message_info['sender_qq']
    data: dict = read_json_file(DICE_DATA)
    send_string = f'已经将{nickname}更名为:'
    if not message:
        data[str(QQ)]['nickname'] = ''
        with open(DICE_DATA, 'w') as f:
            dump(data, f)
        return f'已经将{nickname}这个名字忘掉了哦'
    #是否设置限定随机昵称
    elif message[0] == 'n':
        type = message[1:].strip()
        if type == 'cn':
            nickname = ''.join(get_random_name(1, 'cn'))
            data[str(QQ)]['nickname'] = nickname
        elif type == 'en':
            nickname = ''.join(get_random_name(1, 'en'))
            data[str(QQ)]['nickname'] = nickname
        elif type == 'enzh':
            nickname = ''.join(get_random_name(1, 'enzh'))
            data[str(QQ)]['nickname'] = nickname
        elif type == 'jp':
            nickname = ''.join(get_random_name(1, 'jp'))
            data[str(QQ)]['nickname'] = nickname
        else:
            nickname = ''.join(get_random_name())
            data[str(QQ)]['nickname'] = nickname
    else:
        nickname = message.strip()
        data[str(QQ)]['nickname'] = nickname
    with open(DICE_DATA, 'w') as f:
        dump(data, f)
    return send_string + nickname


def get_coc_card(num=1):
    if num > 10 or num < 1:
        num = 1
    card_list = []
    for i in range(num):
        card = {'力量':get_dice_point(3, 6) * 5, '体质':get_dice_point(3, 6) * 5,
                '体型':(get_dice_point(2, 6) + 6) * 5, '敏捷':get_dice_point(3, 6) * 5,
                '外貌':get_dice_point(3, 6) * 5, '智力':(get_dice_point(2, 6) + 6) * 5,
                '意志':get_dice_point(3, 6) * 5, '教育':(get_dice_point(2, 6) + 6) * 5,
                '幸运':get_dice_point(3, 6) * 5}
        sum = 0
        for point in card.values():
            sum += point
        no_luck_sum = sum - card['幸运']
        sum = f'{no_luck_sum}/{sum}'
        card['hp'] = round((card['体质'] + card['体型']) / 10)
        card['san'] = card['意志']
        card['总计'] = sum
        card_list.append(card)
    return card_list


def get_dice_point(num=1, scale=100)->int:
    point = 0
    for i in range(num):
        point += random.randint(1, scale)
    return point


def random_check(message_info):
    message: str = message_info['message'][3:].strip()
    if not message:
        return '用法：.ra/rc ([检定轮数]#)[属性名] ([成功率])\n//角色卡设置了属性时，可省略成功率'
    nickname = message_info['nickname']
    QQ = message_info['sender_qq']
    group_qq = message_info['group_qq']
    pattern = re.compile('([^0-9+*/-]+)([-+*/]?)(\d*)')
    data: dict = read_json_file(DICE_DATA)
    card: dict = data[str(QQ)]['card']['default']
    set = read_json_file(DICE_DATA)[str(QQ)]['set']     #默认骰面数
    data: dict = read_json_file(DATA_PATH)
    if group_qq in data['setcoc'].keys():
        set_coc = data['setcoc'][str(group_qq)]     #房规
    else:
        set_coc = 3
        data['setcoc'][str(group_qq)] = 3
        with open(DATA_PATH, 'w') as f:
            dump(data, f)
    if re.match('(\d+)([^0-9+*/-]*)', message) and not message.__contains__('#'):
        #match从头开始匹配，当命令含有#时也会匹配到，因此需要去除这种情况
        check_point, reason = re.match('(\d+)([^0-9]*)', message).groups()
        if reason:
            dice_name = '由于' + reason
        else:
            dice_name = ''
        point = random.randint(1, set)
        result = point_check(int(check_point), point, set_coc)
        if result == '大成功':
            return f'{dice_name}{nickname}进行检定: D{set}={point}/' \
                   f'{check_point} [{result}] 竟然成功了，创造出奇迹了呢'
        elif result == '失败':
            return f'{dice_name}{nickname}进行检定: D{set}={point}/' \
                   f'{check_point} [{result}] 失败了呢，真是遗憾呀'
        elif result == '大失败':
            return f'{dice_name}{nickname}进行检定: D{set}={point}/' \
                   f'{check_point} [{result}] 啊，大失败，看来这次没有神明眷顾呢'
        else:
            return f'{dice_name}{nickname}进行检定: D{set}={point}/' \
                   f'{check_point} [{result}] 成功了呢，真不错呢'
    elif message[:2] == '困难':
        match = re.search(pattern, message[2:])
        # 判断是否有掷骰原因，并将原因分离出来
        if message[match.end():]:
            dice_name = '由于 ' + message[match.end():]
        else:
            dice_name = ''
        property, operator, point = map(str.strip, match.groups())
        if property == '理智':
            property = 'san'
        if property in card.keys():
            point = card[property] if not point else point
        elif property.upper() in DICE_SYNONYMS.keys() and card.get(DICE_SYNONYMS[property.upper()]):
            point = card[DICE_SYNONYMS[property.upper()]] if not point else point
            property = DICE_SYNONYMS[property.upper()]
        else:
            if not point:
                return f'未设定{property}成功率，请先.st {property} 技能值 或查看.help rc'
        check_point = round(point / 2)
        point = random.randint(1, set)
        result = point_check(check_point, point, set_coc)
        if result == '大成功':
            return f'{dice_name}{nickname}进行{property}检定: D{set}={point}/' \
                   f'{check_point} [{result}] 竟然成功了，创造出奇迹了呢'
        elif result == '失败':
            return f'{dice_name}{nickname}进行{property}检定: D{set}={point}/' \
                   f'{check_point} [{result}] 失败了呢，真是遗憾呀'
        elif result == '大失败':
            return f'{dice_name}{nickname}进行{property}检定: D{set}={point}/' \
                   f'{check_point} [{result}] 啊，大失败，看来这次没有神明眷顾呢'
        else:
            return f'{dice_name}{nickname}进行{property}检定: D{set}={point}/' \
                   f'{check_point} [{result[-2:]}] 成功了呢，真不错呢'
    elif message[:2] == '极难':
        match = re.search(pattern, message[2:])
        property, operator, point = map(str.strip, match.groups())
        if property == '理智':
            property = 'san'
        # 判断是否有掷骰原因，并将原因分离出来
        if message[match.end():]:
            dice_name = '由于 ' + message[match.end():]
        else:
            dice_name = ''
        if property in card.keys():
            point = card[property] if not point else point
        elif property.upper() in DICE_SYNONYMS.keys() and card.get(DICE_SYNONYMS[property.upper()]):
            point = card[DICE_SYNONYMS[property.upper()]] if not point else point
            property = DICE_SYNONYMS[property.upper()]
        else:
            if not point:
                return f'未设定{property}成功率，请先.st {property} 技能值 或查看.help rc'
        check_point = round(point / 10)
        point = random.randint(1, set)
        result = point_check(check_point, point, set_coc)
        if result == '大成功':
            return f'{dice_name}{nickname}进行{property}检定: D{set}={point}/' \
                   f'{check_point} [{result}] 竟然成功了，创造出奇迹了呢'
        elif result == '失败':
            return f'{dice_name}{nickname}进行{property}检定: D{set}={point}/' \
                   f'{check_point} [{result}] 失败了呢，真是遗憾呀'
        elif result == '大失败':
            return f'{dice_name}{nickname}进行{property}检定: D{set}={point}/' \
                   f'{check_point} [{result}] 啊，大失败，看来这次没有神明眷顾呢'
        else:
            return f'{dice_name}{nickname}进行{property}检定: D{set}={point}/' \
                   f'{check_point} [{result[-2:]}] 成功了呢，真不错呢'
    elif not message.__contains__('#'):
        match = re.search(pattern, message)
        property, operator, point = map(str.strip, match.groups())
        if property == '理智':
            property = 'san'
        # 判断是否有掷骰原因,并将原因分离出来
        oper_num, point = point, None
        #有运算符时oper_num即为待运算的操作数,否则即为通过参数指定的成功率
        if message[match.end():]:
            dice_name = '由于 ' + message[match.end():]
        else:
            dice_name = ''
        if property in card.keys():
            point = card[property]
        elif property.upper() in DICE_SYNONYMS.keys() and card.get(DICE_SYNONYMS[property.upper()]):
            point = card[DICE_SYNONYMS[property.upper()]]
            property = DICE_SYNONYMS[property.upper()]
        else:
            #不存在该属性时才会进入
            if operator and oper_num:
            #只有运算符和操作数,没有属性值
                return f'未设定{property}成功率，请先.st {property} 技能值 或查看.help rc'
            elif not operator and not oper_num:
            #无需运算
                return f'未设定{property}成功率，请先.st {property} 技能值 或查看.help rc'
            elif operator and not oper_num:
            #只有操作数,此时将操作数看作检定原因
                dice_name = operator + dice_name
            else:
            #此时通过参数形式指定了成功率,且此时由oper_num保存
                pass
        try:
            if operator == '+':
                check_point = int(point) + int(oper_num)
            elif operator == '-':
                check_point = int(point) - int(oper_num)
            elif operator == '*':
                check_point = int(point) * int(oper_num)
            elif operator == '/':
                check_point = round(int(point) / int(oper_num))
            else:
                #此时无运算符,point不为None则表明属性存在并且point为属性值,否则表明通过参数指定了成功率,且保存于oper_num
                check_point = int(point) if point else int(oper_num)
        except:
            return '操作数和操作符间不能有空格'
        point = random.randint(1, set)
        result = point_check(check_point, point, set_coc)
        if result == '大成功':
            return f'{dice_name}{nickname}进行{property}{operator}{oper_num}检定: D{set}={point}/' \
                   f'{check_point} [{result}] 竟然成功了，创造出奇迹了呢'
        elif result == '失败':
            return f'{dice_name}{nickname}进行{property}{operator}{oper_num}检定: D{set}={point}/' \
                   f'{check_point} [{result}] 失败了呢，真是遗憾呀'
        elif result == '大失败':
            return f'{dice_name}{nickname}进行{property}{operator}{oper_num}检定: D{set}={point}/' \
                   f'{check_point} [{result}] 啊，大失败，看来这次没有神明眷顾呢'
        else:
            return f'{dice_name}{nickname}进行{property}{operator}{oper_num}检定: D{set}={point}/' \
                   f'{check_point} [{result}] 成功了，真不错呢'
    else:
        #判断奖励骰和轮数的次数
        multi_match = re.search('(\d{0,1})#([bpBP])(\d{0,1})', message)
        dice_times, type, times = multi_match.groups()
        dice_times = 1 if not dice_times else dice_times
        times = '1' if not times else times
        type = type.upper()

        message = message[multi_match.end():]
        match = re.search(pattern, message)
        if not match:
            return '未设置属性或技能成功率，请先.st 属性或技能 技能值'
        property, operator, point = map(str.strip, match.groups())
        if property == '理智':
            property = 'san'
        # 判断是否有掷骰原因，并将原因分离出来
        oper_num = point
        if message[match.end():]:
            dice_name = '由于 ' + message[match.end():]
        else:
            dice_name = ''
        if property in card.keys():
            point = card[property]
        elif property.upper() in DICE_SYNONYMS.keys() and card.get(DICE_SYNONYMS[property.upper()]):
            point = card[DICE_SYNONYMS[property.upper()]]
            property = DICE_SYNONYMS[property.upper()]
        else:
            # 不存在该属性时才会进入
            if operator and point:
                # 只有运算符和操作数，没有属性值
                return f'未设定{property}成功率，请先.st {property} 技能值 或查看.help rc'
            elif not operator and not point:
                # 无需运算
                return f'未设定{property}成功率，请先.st {property} 技能值 或查看.help rc'
            elif operator and not point:
                # 只有操作数，此时将操作数看作检定原因
                dice_name = operator + dice_name
            else:
                # 此时通过参数形式指定了成功率
                pass
        try:
            if operator == '+':
                check_point = int(point) + int(oper_num)
            elif operator == '-':
                check_point = int(point) - int(oper_num)
            elif operator == '*':
                check_point = int(point) * int(oper_num)
            elif operator == '/':
                check_point = round(int(point) / int(oper_num))
            else:
                check_point = int(point)
        except:
            return '操作数和操作符间不能有空格'

        send_string = f'{dice_name}{nickname}进行{dice_times}次{property}{operator}{oper_num}检定:\n'
        for index in range(int(dice_times)):
            point_str, point = express(type + times)
            print(point)
            if point is None:
                return point_str
            result = point_check(check_point, point, set_coc)
            send_string += f'{point_str}={point}/{check_point} {result}\n'
        return send_string[:-1]


def st_handle(message_info):
    message: str = message_info['message'][3:].strip()
    nickname = message_info['nickname']
    QQ = message_info['sender_qq']
    data: dict = read_json_file(DICE_DATA)
    card:dict = data[str(QQ)]['card']['default']
    print(message)
    if message == 'clr' or message == 'clear':
        data[str(QQ)]['card']['default'] = {}
        with open(DICE_DATA, 'w') as f:
            dump(data, f)
        return f'已删除{nickname}当前角色卡的所有属性'
    elif message[:4] == 'show':
        if message == 'show':
            trans_tab = str.maketrans(',', ' ', " '{}")
            return nickname + '的角色卡属性为\n' + str(card).translate(trans_tab)
        else:
            property = message[4:].strip()
            if property in card.keys():
                return  f'{nickname}的{property}属性为{card[property]}'
            elif property == '理智':
                return f'{nickname}的{property}属性为{card["san"]}'
            elif property.upper() in DICE_SYNONYMS.keys() and card.get(DICE_SYNONYMS[property.upper()]):
                return f'{nickname}的{property}属性为{card[DICE_SYNONYMS[property.upper()]]}'
            else:
                return '属性不存在'
    elif message[:3] == 'del':
        if message == 'del':
            return '请输入要删除的属性哦'
        else:
            property = message[3:].strip()
            if property == '理智':
                property = 'san'
            if property in card.keys():
                #使用del关键字直接删除字典中的键值对
                del data[str(QQ)]['card']['default'][property]
                with open(DICE_DATA, 'w') as f:
                    dump(data ,f)
                return f'已删除{nickname}的{property}属性'
            elif property.upper() in DICE_SYNONYMS.keys() and card.get(DICE_SYNONYMS[property.upper()]):
                del data[str(QQ)]['card']['default'][DICE_SYNONYMS[property.upper()]]
                with open(DICE_DATA, 'w') as f:
                    dump(data, f)
                return f'已删除{nickname}的{DICE_SYNONYMS[property.upper()]}({property})属性'
            else:
                '属性不存在'
    else:
        if message.__contains__(':'):
            # 带冒号类型键值对处理，一般用于添加属性
            items = message.split()
            send_string = '已添加属性:\n'
            for item in items:
                try:
                    property, point = item.split(':')
                    if property == '总计':
                        continue
                    elif property == '理智':
                        property = 'san'
                    if property in card.keys():
                        card[property] = int(point)
                        send_string += property
                    elif property.upper() in DICE_SYNONYMS.keys() and card.get(DICE_SYNONYMS[property.upper()]):
                        card[DICE_SYNONYMS[property.upper()]] = int(point)
                        send_string += DICE_SYNONYMS[property.upper()]
                    else:
                        card[property] = int(point)
                        send_string += property
                    send_string += ' '
                except:
                    pass
            with open(DICE_DATA, 'w') as f:
                dump(data, f)
            return send_string[:-1]
        else:
            # 不带冒号类型键值对处理，一般用于修改属性
            message = ''.join(message.split())
            #message = message.replace(' ', '')
            pattern = re.compile('([^0-9*/+-]+)([+*/-]?)([dD0-9]+)')
            offset = 0
            send_string = '已添加或修改属性:\n'
            while re.search(pattern, message[offset:]):
                match = re.search(pattern, message[offset:])
                property, operator, point = match.groups()
                offset += match.end()
                if not operator:
                    try:
                        if property == '总计':
                            continue
                        elif property == '理智':
                            property = 'san'
                        if property in card.keys():
                            card[property] = int(point)
                            send_string += property
                        elif property.upper() in DICE_SYNONYMS.keys() and card.get(DICE_SYNONYMS[property.upper()]):
                            card[DICE_SYNONYMS[property.upper()]] = int(point)
                            send_string += DICE_SYNONYMS[property.upper()]
                        else:
                            card[property] = int(point)
                            send_string += property
                        if property == 'san' and point <= 0:
                            send_string += '已丧失全部理智，那么调查员将会成为一个无药可救的永久性疯狂角色，真是不幸呢'
                            break
                    except Exception as e:
                        print(e)
                    send_string += ' '
                else:
                    try:
                        # 检查是否出现类似 .st理智+d10 的表达式
                        if 'D' in point.upper():
                            log, point = express(point)
                            point = str(point)
                            log = '{' + log + '}'
                            if point is None:
                                return log
                        else:
                            log = ''
                        if property == '总计':
                            continue
                        elif property == '理智':
                            property = 'san'
                        if property in card.keys():
                            new_point = round(eval(f'{card[property]}{operator}{point}'))
                            card[property] = new_point
                            send_string += property + operator + log + point + '=' + str(new_point) + '已修改'
                            if property == 'san' and new_point <= 0:
                                send_string += '已丧失全部理智，那么调查员将会成为一个无药可救的永久性疯狂角色，真是不幸呢.'
                                break
                        elif property.upper() in DICE_SYNONYMS.keys() and card.get(DICE_SYNONYMS[property.upper()]):
                            new_point = round(eval(f'{card[property]}{operator}{point}'))
                            card[DICE_SYNONYMS[property.upper()]] = new_point
                            send_string += DICE_SYNONYMS[property.upper()]\
                                           + operator + log + point + '=' + str(new_point) + '已修改'
                            if property == 'san' and new_point <= 0:
                                send_string += '已丧失全部理智，那么调查员将会成为一个无药可救的永久性疯狂角色，真是不幸呢.'
                                break
                        else:
                            send_string += '无' + property + '属性'
                    except Exception as e:
                        print(e)
                    send_string += ' '
            with open(DICE_DATA, 'w') as f:
                dump(data, f)
            return send_string[:-1]


def san_check(message_info):
    message: str = message_info['message'][3:].strip()
    nickname = message_info['nickname']
    group_qq = message_info['group_qq']
    QQ = message_info['sender_qq']
    data: dict = read_json_file(DICE_DATA)
    card: dict = data[str(QQ)]['card']['default']
    if re.search('([^0-9/dD ])', message):
        match = re.search('([^0-9/dD ])', message)
        dice_name = '由于' + message[match.start():]
        message = message[:match.start()]
    else:
        dice_name = ''
    if not message:
        return '用法：.sc[成功损失]/[失败损失] ([当前san值])\n已经.st了理智/san时，可省略最后的参数\n'

    coc_data: dict = read_json_file(DATA_PATH)
    if not message_info['is_group']:
        set_coc = 3
    elif group_qq in coc_data['setcoc'].keys():
        set_coc = coc_data['setcoc'][str(group_qq)]     #房规
    else:
        set_coc = 3
        coc_data['setcoc'][str(group_qq)] = 3
        with open(DATA_PATH, 'w') as f:
            dump(coc_data, f)
    # 已经设置san属性
    if  'san' in card.keys() or '理智' in card.keys():
        san:int = card.get('san') if 'san' in card.keys() else card.get('理智')
        try:
            sc_expression, san = message.split()
            san = int(san)
            is_give_san = True
        except:
            sc_expression = message
            is_give_san = False
        success_loss, fail_loss = sc_expression.split('/')
        if san == 0:
            return '当前理智值为0，无法进行SAN CHECK'
        elif san < 0:
            return '当前理智值为负，无法进行SAN CHECK'
        else:
            pattern = re.compile('(\d{0,2})[Dd](\d{0,3})')
            # 获取sc成功时使用的骰子数和面数
            if re.search(pattern, success_loss):
                suc_dice_num, suc_dice_face = re.search(pattern, success_loss).groups()
                # 未指定骰子数或面数，使用默认值
                suc_dice_num = 1 if not suc_dice_num else int(suc_dice_num)
                suc_dice_face = 2 if not suc_dice_face else int(suc_dice_face)
            else:
                suc_dice_num, suc_dice_face = None, int(success_loss)
            # 获取sc失败时使用的骰子数和面数
            if re.search(pattern, fail_loss):
                fail_dice_num, fail_dice_face = re.search(pattern, fail_loss).groups()
                # 未指定骰子数或面数，使用默认值
                fail_dice_num = 1 if not fail_dice_num else int(fail_dice_num)
                fail_dice_face = 10 if not fail_dice_face else int(fail_dice_face)
            else:
                fail_dice_num, fail_dice_face = None, fail_loss
            #dice_num为None时表示成功/失败损失为已给的数，反之则给的掷骰表达式

            success_str, success_loss = express(str(success_loss))
            fail_str, fail_loss = express(str(fail_loss))
            if not success_loss:
                return success_str
            elif not fail_loss:
                return fail_str
            else:
                point = random.randint(1, 100)
                result = point_check(san, point, set_coc)
                original_san = san
                if result == '失败':
                    san = (san - fail_loss) if (san - fail_loss) > 0 else 0
                    if san <= 0:
                        suffix = '\n已丧失全部理智，那么调查员将会成为一个无药可救的永久性疯狂角色，真是不幸呢'
                    else:
                        suffix = ''
                    if not is_give_san:
                        with open(DICE_DATA, 'w') as f:
                            data[str(QQ)]['card']['default']['理智'] = san
                            data[str(QQ)]['card']['default']['san'] = san
                            dump(data, f)
                    if fail_dice_num is None:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{fail_loss}点，当前剩余{san}点' + suffix
                    elif fail_dice_num == 1:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{fail_dice_num}D{fail_dice_face}=' \
                               f'{fail_loss}点，当前剩余{san}点' + suffix
                    else:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{fail_str}点，当前剩余{san}点' + suffix
                elif result == '大失败':
                    san = (san - fail_loss) if (san - fail_loss) > 0 else 0
                    if san <= 0:
                        suffix = '\n已丧失全部理智，那么调查员将会成为一个无药可救的永久性疯狂角色，真是不幸呢'
                    else:
                        suffix = ''
                    if not is_give_san:
                        with open(DICE_DATA, 'w') as f:
                            data[str(QQ)]['card']['default']['理智'] = san
                            data[str(QQ)]['card']['default']['san'] = san
                            dump(data, f)
                    if fail_dice_num is None:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{fail_dice_num}D{fail_dice_face}=' \
                               f'{fail_loss}点，当前剩余{san}点' + suffix
                    else:
                        fail_loss = fail_dice_num * fail_dice_face
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{fail_dice_num}*{fail_dice_face}=' \
                               f'{fail_loss}点，当前剩余{san}点' + suffix
                else:
                    # sc成功的情况
                    san = (san - success_loss) if (san - success_loss) > 0 else 0
                    if san <= 0:
                        suffix = '\n已丧失全部理智，那么调查员将会成为一个无药可救的永久性疯狂角色，真是不幸呢'
                    else:
                        suffix = ''
                    if not is_give_san:
                        with open(DICE_DATA, 'w') as f:
                            data[str(QQ)]['card']['default']['理智'] = san
                            data[str(QQ)]['card']['default']['san'] = san
                            dump(data, f)
                    if suc_dice_num is None:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{success_loss}点，当前剩余{san}点' + suffix
                    elif suc_dice_num == 1:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{suc_dice_num}D{suc_dice_face}=' \
                               f'{success_loss}点，当前剩余{san}点' + suffix
                    else:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{success_str}点，当前剩余{san}点' + suffix
    else:
        try:
            sc_expression, san = message.split()
            san = int(san)
        except:
            return '用法：.sc[成功损失]/[失败损失] ([当前san值])\n已经.st了理智/san时，可省略最后的参数.'
        success_loss, fail_loss = sc_expression.split('/')
        if san == 0:
            return '当前理智值为0，无法进行SAN CHECK'
        elif san < 0:
            return '当前理智值为负，无法进行SAN CHECK'
        else:
            pattern = re.compile('(\d{0,2})[Dd](\d{0,3})')
            if re.search(pattern, success_loss):
                suc_dice_num, suc_dice_face = re.search(pattern, success_loss).groups()
                suc_dice_num = 1 if not suc_dice_num else int(suc_dice_num)
                suc_dice_face = 2 if not suc_dice_face else int(suc_dice_face)
            else:
                suc_dice_num, suc_dice_face = None, int(success_loss)
            if re.search(pattern, fail_loss):
                fail_dice_num, fail_dice_face = re.search(pattern, fail_loss).groups()
                fail_dice_num = 1 if not fail_dice_num else int(fail_dice_num)
                fail_dice_face = 10 if not fail_dice_face else int(fail_dice_face)
            else:
                fail_dice_num, fail_dice_face = None, fail_loss
            #dice_num为None时表示成功/失败损失为已给的数，反之则给的掷骰表达式

            success_str, success_loss = express(str(success_loss))
            fail_str, fail_loss = express(str(fail_loss))
            if not success_loss:
                return success_str
            elif not fail_loss:
                return fail_str
            else:
                point = random.randint(1, 100)
                result = point_check(san, point, set_coc)
                original_san = san
                if result == '失败':
                    san = (san - fail_loss) if (san - fail_loss) > 0 else 0
                    if san <= 0:
                        suffix = '\n已丧失全部理智，那么调查员将会成为一个无药可救的永久性疯狂角色，真是不幸呢'
                    else:
                        suffix = ''
                    if fail_dice_num is None:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{fail_loss}点，当前剩余{san}点' + suffix
                    elif fail_dice_num == 1:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{fail_dice_num}D{fail_dice_face}=' \
                               f'{fail_loss}点，当前剩余{san}点' + suffix
                    else:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{fail_str}点，当前剩余{san}点' + suffix
                elif result == '大失败':
                    fail_loss = fail_dice_num * fail_dice_face
                    san = (san - fail_loss) if (san - fail_loss) > 0 else 0
                    if san <= 0:
                        suffix = '\n已丧失全部理智，那么调查员将会成为一个无药可救的永久性疯狂角色，真是不幸呢'
                    else:
                        suffix = ''
                    if fail_dice_num is None:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{fail_dice_num}D{fail_dice_face}=' \
                               f'{fail_loss}点，当前剩余{san}点' + suffix
                    else:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{fail_dice_num}*{fail_dice_face}=' \
                               f'{fail_loss}点，当前剩余{san}点' + suffix
                else:
                    san = (san - fail_loss) if (san - fail_loss) > 0 else 0
                    if san <= 0:
                        suffix = '\n已丧失全部理智，那么调查员将会成为一个无药可救的永久性疯狂角色，真是不幸呢'
                    else:
                        suffix = ''
                    if suc_dice_num is None:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{success_loss}点，当前剩余{san}点' + suffix
                    elif suc_dice_num == 1:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{suc_dice_num}D{suc_dice_face}=' \
                               f'{success_loss}点，当前剩余{san}点' + suffix
                    else:
                        return f'{dice_name}{nickname}进行理智检定(San Check):\n D100={point}/' \
                               f'{original_san} [{result}]\n{nickname}的理智减少{success_str}点，当前剩余{san}点' + suffix


def point_check(property_point, point, rule_num):
    """判断大成功或大失败"""
    if property_point >= point:
        if point <= round(property_point / 5):
            return_str = '极难成功'
        elif point <= round(property_point / 2):
            return_str = '困难成功'
        else:
            return_str = '成功'
    else:
        return_str =  '失败'
    if rule_num == 0:
        if property_point < 50:
            if point >= 96 and point <= 100:
                return '大失败'
            elif point == 1:
                return '大成功'
            else:
                return return_str
        else:
            if point == 100:
                return '大失败'
            elif point == 1:
                return '大成功'
            else:
                return return_str
    elif rule_num == 1:
        if property_point < 50:
            if point >= 96 and point <= 100:
                return '大失败'
            elif point == 1:
                return '大成功'
            else:
                return return_str
        else:
            if point == 100:
                return '大失败'
            elif point >= 1 and point <= 5:
                return '大成功'
            else:
                return return_str
    elif rule_num == 2:
        if point >= 96 and point <= 99:
            return '大失败' if return_str == '失败' else '成功'
        elif point == 100:
            return '大失败'
        elif point >= 1 and point <= 5:
            return '大成功' if return_str == '成功' else '失败'
        else:
            return return_str
    elif rule_num == 3:
        if point >= 96 and point <= 100:
            return '大失败'
        elif point >= 1 and point <= 5:
            return '大成功'
        else:
            return return_str
    elif rule_num == 4:
        if point >= 1 and point <= 5:
            if point <= property_point / 10:
                return '大成功'
            else:
                return return_str
        elif property_point >= 50:
            if point == 100:
                return '大失败'
            else:
                return return_str
        else:
            if point >= 96 + property_point / 10:
                return '大失败'
            else:
                return return_str
    elif rule_num == 5:
        if point == 1 or point ==2:
            if point < property_point / 5:
                return '大成功'
            else:
                return return_str
        elif property_point >= 50:
            if point == 99 or point == 100:
                return '大失败'
            else:
                return return_str
        else:
            if point >= 96 and point <= 100:
                return '大失败'
            else:
                return return_str


def sign_in(message_info: dict):
    QQ = message_info['sender_qq']
    total_data: dict = read_json_file(SIGN_PATH)
    total_data.setdefault('%s' % QQ, {'days': 0, 'today': 0, 'points': 0})
    data = total_data['%s' % QQ]
    days = data['days']
    points = data['points']
    if not data['today']:
        point = random.randint(20, 50) + days * 5
        send_string = 'QQ:%d\n签到成功~!\n本次获得香火钱:%d\n剩余香火钱:%d\n累计签到:%d天' % (
            QQ, point, points + point, days + 1)
        total_data["%s" % QQ] = {'days': days + 1, 'today': 1, 'points': points + point}
    else:
        send_string = f'QQ:{QQ}\n今天已经签到过了呢~\n累计签到:{days}天\n剩余香火钱:{points}'
    with open(SIGN_PATH, "w") as f:
        dump(total_data, f)
    return text_to_img(send_string)