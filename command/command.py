# encoding=utf8
import os
import re
import threading
import hashlib
import urllib.parse
from json import loads, load, dump
from random import sample, choices, randint
from time import sleep, localtime, strftime

from PIL import Image
from bs4 import BeautifulSoup as bp

from config import *

command_dict = {}

"""普通命令的装饰器"""
def add_command(command):
    def add_func(func):
        command_dict[command] = func
    return add_func


def dot_command(command):
    def add_func(func):
        command_dict[command] = func
    return add_func


def send_private_msg(send_string, QQ):
    data = {
        'message': send_string,
        'auto_escape': False,
        'user_id': QQ
    }
    api_url = apiBaseUrl + apiPrivateMsg
    response = requests.post(api_url, data=data)
    if response.status_code == 200:
        print("消息发送成功")


def send_public_msg(send_string, group_qq):
    data = {
        'message': send_string,
        'auto_escape': False,
        'group_id': group_qq
    }
    api_url = apiBaseUrl + apiGroupMsg
    response = requests.post(api_url, data=data)
    if response.status_code == 200:
        print("消息发送成功")


def send_long_msg(message_info, send_string):
    for index in range(0, round((len(send_string) + 99) / 100)):
        message = send_string[SEND_LENGTH*index : SEND_LENGTH*(index+1)]
        if not message or index > 4:
            return
        if message_info['is_private']:
            send_private_msg(message, message_info['sender_qq'])
        elif message_info['is_group']:
            send_public_msg(message, message_info['group_qq'])
        sleep(PAUSE_TIME)


def get_one_page(url, type='content'):
    requests.session().keep_alive = False
    headers = {
        "Connection": "close",
        "User-Agent": UserAgent}
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200 or response.status_code == 304:
            if type == 'text':
                return response.text
            elif type == 'json':
                return response.json()
            elif type == 'content':
                return response.content
        else:
            return "failed"
    except requests.RequestException as e:
        print("request failed: time out", e)
        return "time_out"


from command.dot_command import *
#避免command和dot_command两个文件循环import

def concat_images(image_names, path, type):
    COL = [1, 5, 10][type]
    ROW = [1, 2, 10][type]
    UNIT_HEIGHT_SIZE = 900
    UNIT_WIDTH_SIZE = 600
    image_files = []
    for index in range(COL * ROW):
        image_files.append(Image.open(path + image_names[index]))
    target = Image.new('RGB', (UNIT_WIDTH_SIZE * COL, UNIT_HEIGHT_SIZE * ROW))
    for row in range(ROW):
        for col in range(COL):
            target.paste(image_files[COL * row + col], (UNIT_WIDTH_SIZE * col, UNIT_HEIGHT_SIZE * row))
    if COL == 10:
        width = target.size[0]
        height = target.size[1]
        target = target.resize((int(width * 0.5), int(height * 0.5)), Image.ANTIALIAS)
    pic_name = threading.current_thread().name
    target.save(SAVE_PATH + pic_name + '.jpg', quality=SAVE_QUALITY)


def get_image_names(path, type: int):
    COL = [1, 5, 10][type]
    ROW = [1, 2, 10][type]
    image_names = list(os.walk(path))[0][2]
    selected_images = choices(image_names, k=COL *ROW) if REPEAT_SELECT else sample(image_names, COL * ROW)
    return selected_images


@add_command('单抽')
def single_draw(message_info):
    message = message_info['message']
    try:
        card_type = int(message[2])
    except BaseException:
        return
    if card_type > 0 and card_type < 8:
        concat_images(get_image_names(
            CARD_PATH[card_type - 1], type=0), CARD_PATH[card_type - 1], type=0)
        print("图片生成成功")
        pic_path = SAVE_PATH + threading.current_thread().name + '.jpg'
        send_string = f"[CQ:image,file=file://{pic_path}]"
        if message_info['is_private']:
            send_private_msg(send_string, message_info['sender_qq'])
        elif message_info['is_group']:
            send_public_msg(send_string, message_info['group_qq'])


@add_command('十连')
def dozen_draw(message_info):
    message = message_info['message']
    try:
        card_type = int(message[2])
    except BaseException:
        return
    if card_type > 0 and card_type < 8:
        concat_images(get_image_names(
            CARD_PATH[card_type - 1], type=1), CARD_PATH[card_type - 1], type=1)
        print("图片生成成功")
        pic_path = SAVE_PATH + threading.current_thread().name + '.jpg'
        send_string = f"[CQ:image,file=file://{pic_path}]"
        if message_info['is_private']:
            send_private_msg(send_string, message_info['sender_qq'])
        elif message_info['is_group']:
            send_public_msg(send_string, message_info['group_qq'])


@add_command('百连')
def dozen_draw(message_info):
    message = message_info['message']
    try:
        card_type = int(message[2])
    except BaseException:
        return
    if card_type > 0 and card_type < 8:
        concat_images(get_image_names(
            CARD_PATH[card_type - 1], type=2), CARD_PATH[card_type - 1], type=2)
        print("图片生成成功")
        pic_path = SAVE_PATH + threading.current_thread().name + '.jpg'
        send_string = f"[CQ:image,file=file://{pic_path}]"
        if message_info['is_private']:
            send_private_msg(send_string, message_info['sender_qq'])
        elif message_info['is_group']:
            send_public_msg(send_string, message_info['group_qq'])


@add_command('签到')
def sign_in_response(message_info: dict):
    if message_info['message'] != '签到':
        return
    QQ = message_info['sender_qq']
    with open(DATA_PATH) as f:
        total_data: dict = load(f)
    total_data.setdefault(str(QQ), {'days': 0, 'today': 0, 'points': 0})
    data = total_data[str(QQ)]
    days = data['days']
    points = data['points']
    if not data['today']:
        point = randint(20, 50) + days * 5
        send_string = '[CQ:at,qq=%d]\n签到成功~!\n本次获得香火钱:%d\n剩余香火钱:%d\n累计签到:%d天' % (
            QQ, point, points + point, days + 1)
        total_data[str(QQ)] = {'days': days + 1, 'today': 1, 'points': points + point}
    else:
        send_string = '[CQ:at,qq=%d]\n今天已经签到过了呢~' % QQ
    if message_info['is_private']:
        send_private_msg(send_string, QQ)
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])
    with open(DATA_PATH, "w") as f:
        dump(total_data, f)


@add_command('打卡')
def sign_in_response(message_info: dict):
    if message_info['message'] != '打卡':
        return
    QQ = message_info['sender_qq']
    with open(DATA_PATH) as f:
        total_data: dict = load(f)
    total_data.setdefault('%s' % QQ, {'days': 0, 'today': 0, 'points': 0})
    data = total_data['%s' % QQ]
    days = data['days']
    points = data['points']
    if not data['today']:
        point = randint(20, 50) + days * 5
        send_string = '[CQ:at,qq=%d]\n签到成功~!\n本次获得香火钱:%d\n剩余香火钱:%d\n累计签到:%d天' % (
            QQ, point, points + point, days + 1)
        total_data["%s" % QQ] = {'days': days + 1, 'today': 1, 'points': points + point}
    else:
        send_string = '[CQ:at,qq=%d]\n今天已经签到过了呢~' % QQ
    if message_info['is_private']:
        send_private_msg(send_string, QQ)
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])
    with open(DATA_PATH, "w") as f:
        dump(total_data, f)


@add_command('信息')
def sign_in_info(message_info: dict):
    if message_info['message'] != '信息':
        return
    QQ = message_info['sender_qq']
    with open(DATA_PATH) as f:
        total_data: dict = load(f)
    data = total_data.get(str(QQ), None)
    if not data:
        send_string = "[CQ:at,qq=%d]\n无签到信息" % QQ
    else:
        send_string = "[CQ:at,qq=%d]\n香火钱:%d\n累计签到%d天" % (
            QQ, data['points'], data['days'])
    if message_info['is_private']:
        send_private_msg(send_string, QQ)
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])


@add_command('跟我学')
def learn(message_info: dict):
    if not message_info['message'] == '跟我学':
        return
    message = message_info['message']
    with open(LEARN_PATH) as f:
        total_dict = load(f)
        key, value = message[3:].strip().split("*")
        total_dict[key] = value
    with open(LEARN_PATH, "w") as f:
        dump(total_dict, f)
    send_string = "跟我学: %s-%s保存成功" % (key, value)
    print(send_string)
    if message_info['is_private']:
        send_private_msg(send_string, message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])


@add_command('指令')
def show_command(message_info: dict):
    if message_info['message'] != '指令':
        return
    send_string = "签到/打卡\n单抽/十连/百连1-7\n搜索1-3/百度\n要红包 热榜\n冷知识 点歌"
    if message_info['is_private']:
        send_private_msg(send_string, message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])


def learn_response(message_info: dict):
    message = message_info['message']
    with open("/bot/learn.json") as f:
        total_dict:dict = load(f)
    send_string = total_dict.get(message)
    if not send_string:
        return
    if message_info['is_private']:
        send_private_msg(str(send_string), message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(str(send_string), message_info['group_qq'])


def parse_one_page(html, option) -> str:
    soup = bp(html, "lxml")
    select_list = [
        'body #content #bodyContent #mw-content-text .mw-parser-output > p',
        'body #content #bodyContent #mw-content-text .mw-parser-output .mw-parser-output > p'
        'body #content #bodyContent #mw-content-text .mw-parser-output > p']
    content = soup.select(select_list[option])
    string = ''
    for item in content:
        string += item.get_text()
    print(string)
    return string


def search_wiki(message) -> str:
    url = 'https://zh.wikipedia.org/wiki/' + urllib.parse.quote(message)
    html = get_one_page(url)
    if html == 'failed':
        return "搜索 %s 失败\n该条目不存在" % message
    elif html == 'time_out':
        return "搜索 %s 超时，请重试" % message.strip()
    else:
        new_message = parse_one_page(html, 2)
        if new_message is None:
            return "搜索 %s 失败\n没有该条目" % message
        else:
            return "搜索 %s :\n%s" % (message, new_message)


def search_moegirl(message) -> str:
    url = 'https://zh.moegirl.org/' + urllib.parse.quote(message)
    html = get_one_page(url)
    if html == 'failed':
        return "搜索 %s 失败\n该条目不存在" % message
    elif html == 'time_out':
        return "搜索 %s 超时，请重试" % message
    else:
        new_message = parse_one_page(html, 0)
        if new_message is None:
            return "搜索 %s 失败\n没有该条目" % message
        else:
            return "搜索 %s :\n%s" % (message, new_message)


def search_thwiki(message) -> str:
    url = 'https://thwiki.cc/' + urllib.parse.quote(message)
    html = get_one_page(url)
    if html == 'failed':
        return "搜索 %s 失败\n该条目不存在" % message
    elif html == 'time_out':
        return "搜索 %s 超时，请重试" % message
    else:
        new_message = parse_one_page(html, 1)
        if new_message is None:
            return "搜索 %s 失败\n没有该条目" % message
        else:
            return "搜索 %s :\n%s" % (message, new_message)


@add_command('百度')
def search_baidu(message_info: dict):
    message = message_info['message'][2:].strip()
    url = 'https://baike.baidu.com/item/' + urllib.parse.quote(message)
    print(url)
    html = get_one_page(url)
    if html == 'failed':
        send_string = "搜索 %s 失败\n该条目不存在" % message
    elif html == 'time_out':
        send_string = "搜索 %s 超时，请重试" % message
    else:
        soup = bp(html, "lxml")
        content = soup.head.find_all(name='meta')
        try:
            respond_content = content[3].attrs["content"]
            send_string = "搜索 %s :\n%s" % (message, respond_content)
        except IndexError:
            send_string = '搜索 %s 失败\n没有该条目' % message
    send_long_msg(message_info, send_string)


def search_song_history(message)->int:
    with open(SONG_PATH) as f:
        search_dict: dict = load(f)
        last_search = search_dict['last_search']
        index = search_dict['index']
    if last_search == message:
        index += 1
    else:
        index = 0
    if index == 10:
        index = 0
    search_dict['last_search'] = message
    search_dict['index'] = index
    dump(search_dict, open(SONG_PATH, 'w'))
    return index


def parse_song_page(json, message) -> str:
    mid_data_list = []
    id_data_list = []
    index = search_song_history(message)
    json = loads(json)
    song_list:list = json['data']['song']['list']
    for item in song_list:
        mid_data_list.append(item['mid'])
        id_data_list.append(item['id'])
    url = r'https://y.qq.com/n/yqq/song/{}.html'.format(mid_data_list[index])
    data = f'[CQ:music,type=qq,id={id_data_list[index]}]'
    return data


def parse_netease_song(json, message):
    id_data_list = []
    index = search_song_history(message)
    song_list: list = json['result']['songs']
    for item in song_list:
        id_data_list.append(item['id'])
    data = f'[CQ:music,type=163,id={id_data_list[index]}]'
    return data, id_data_list[index]


def parse_netease_comment(json):
    data_list = []
    comment_list: list = json['hotComments']
    for comment in comment_list:
        content: list = comment['content']
        nickname = comment['user']['nickname']
        data_list.append(nickname + ': ' + content)
    return data_list


@add_command('搜索')
def search_item(message_info: dict):
    message: str = message_info['message']
    try:
        search_type = int(message[2])
    except BaseException:
        return
    item = message[3:].strip()
    if search_type == 1:
        send_string = search_wiki(item)
    elif search_type == 2:
        send_string = search_moegirl(item)
    elif search_type == 3:
        send_string = search_thwiki(item)
    else:
        return
    if send_string:
        send_long_msg(message_info, send_string)


@add_command('/点歌')
def search_song(message_info: dict):
    search_item = message_info['message'][3:].strip()
    url = r'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.center&searchid=46369776929740470&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n=10&w={}&g_tk_new_20200303=138867905&g_tk=138867905&loginUin=2224546887&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0'.format(
        search_item.replace(' ', '%20'))
    html = get_one_page(url)
    if html == 'failed':
        send_string = "点歌 %s 失败\n该条目不存在" % search_item
    elif html == 'time_out':
        send_string = "点歌 %s 超时，请重试" % search_item
    else:
        new_message = parse_song_page(html, search_item)
        if new_message is None:
            send_string = "点歌 %s 失败\n没有该条目" % search_item
        else:
            send_string = new_message
    if message_info['is_private']:
        send_private_msg(send_string, message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])


@add_command('.点歌')
def search_song(message_info: dict):
    search_item = message_info['message'][3:].strip()
    session = requests.session()
    session.headers = {'User-Agent' : UserAgent}
    url = r'http://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={}&type=1&offset=0&total=true&limit=10'.format(search_item)
    #json = get_one_page(url, 'json')
    json = session.get(url).json()
    if json == 'failed':
        send_string = "点歌 %s 失败\n该条目不存在" % search_item
    elif json == 'time_out':
        send_string = "点歌 %s 超时，请重试" % search_item
    else:
        new_message = parse_netease_song(json, search_item)
        if new_message is None:
            send_string = "点歌 %s 失败\n没有该条目" % search_item
        else:
            send_string = new_message
    if message_info['is_private']:
        send_private_msg(send_string, message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])


@add_command('点歌')
def search_song(message_info: dict):
    search_item = message_info['message'][2:].strip()
    url = f'https://musicapi.leanapp.cn/search?keywords={urllib.parse.quote(search_item)}'
    json = get_one_page(url, 'json')
    if json == 'failed':
        send_string = "点歌 %s 失败\n该条目不存在" % search_item
    elif json == 'time_out':
        send_string = "点歌 %s 超时，请重试" % search_item
    else:
        new_message = parse_netease_song(json, search_item)[0]
        if new_message is None:
            send_string = "点歌 %s 失败\n没有该条目" % search_item
        else:
            send_string = new_message
    print(send_string)
    if message_info['is_private']:
        send_private_msg(send_string, message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])


@add_command('帮助')
def show_help_doc(message_info: dict):
    send_pic = f"[CQ:image,file=file://{HELP_DOC_PATH}]"
    if message_info['is_private']:
        send_private_msg(send_pic, message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(send_pic, message_info['group_qq'])


@add_command('冷知识')
def knowledge(message_info: dict):
    if message_info['message'] != '冷知识':
        return
    with open(KNOWLEDGE_PATH) as f:
        data_dict = load(f)
    send_string = data_dict[str(randint(0, 46))]
    print(send_string)
    if message_info['is_private']:
        send_private_msg(send_string, message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])


@add_command('要礼物')
def send_gift(message_info: dict):
    if not message_info['message'] == '要礼物':
        return
    QQ = message_info['sender_qq']
    type = randint(0, 13)
    send_string = "[CQ:gift,qq=%d,id=%d]" % (QQ, type)
    if message_info['is_private']:
        send_private_msg(send_string, QQ)
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])


@add_command('保存')
def save_image(message_info: dict):
    now = strftime("%Y_%m_%d_%H_%M_%S", localtime())
    message = message_info['message']
    QQ = message_info['sender_qq']
    url_list = re.findall('url=(.+?)]', message)
    for index, url in zip(range(len(url_list)), url_list):
        path = f'{SAVE_PATH}{QQ}_{now}_{index}.jpg'
        print(url)
        response = get_one_page(url)
        if isinstance(response, bytes):
            print(f'从{url}获取图片成功')
            with open(path, 'wb') as f:
                f.write(response)
            print(path, '保存成功', sep=' ')
            if message_info['is_private']:
                send_private_msg('保存成功', QQ)
            elif message_info['is_group']:
                send_public_msg('保存成功', message_info['group_qq'])
        else:
            print(response)


@add_command('av')
def av_to_bv(message_info):
    message = message_info['message']
    try:
        av = int(message[2:])
    except:
        return
    table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr = {}
    for i in range(58):
        tr[table[i]] = i
    s = [11, 10, 3, 8, 4, 6]
    xor = 177451812
    add = 8728348608
    av = (av ^ xor) + add
    r = list('BV1  4 1 7  ')
    for i in range(6):
        r[s[i]] = table[av // 58**i % 58]
    send_string = ''.join(r)
    if message_info['is_private']:
        send_private_msg(send_string, message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])


@add_command('BV')
def bv_to_av(message_info):
    bv = message_info['message']
    table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr = {}
    for i in range(58):
        tr[table[i]] = i
    s = [11, 10, 3, 8, 4, 6]
    xor = 177451812
    add = 8728348608
    r = 0
    for i in range(6):
        r += tr[bv[s[i]]] * 58 ** i
    send_string =  'av' + str((r - add) ^ xor)
    if message_info['is_private']:
        send_private_msg(send_string, message_info['sender_qq'])
    elif message_info['is_group']:
        send_public_msg(send_string, message_info['group_qq'])


@add_command('热榜')
def zhihu_hot(message_info):
    if message_info['message'] != '热榜':
        return
    requests.session().keep_alive = False
    headers = {
        'Cookie': ZHIHU_COOKIE,
        "Connection": "close",
        "User-Agent": r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
    try:
        response = requests.get(url="https://www.zhihu.com/hot", headers=headers, timeout=8)
        if response.status_code == 200:
            soup = bp(response.content, "lxml")
            titles = soup.find_all(attrs={"class" : "HotItem-title"})
            hots = soup.find_all(attrs={"class" : "HotItem-metrics HotItem-metrics--bottom"})
            send_string_list = []
            for index in range(0, ZHIHU_LENGTH, 3):
                send_string_list.append('知乎热榜\n')
            #for index, title, hot in zip(list(range(max(len(titles), len(hots)))), titles, hots):
            for index, title, hot in zip(list(range(1, ZHIHU_LENGTH + 1)), titles, hots):
                send_string_list[int((index-1)/3)] += f'{str(index)}.{title.get_text()}\n{hot.get_text()[:-3]}\n'
            print(send_string_list)
        else:
            send_string_list = ['获取热榜失败']
        # if message_info['is_private']:
        #     for send_string in send_string_list:
        #         send_private_msg(send_string, message_info['sender_qq'])
        # elif message_info['is_group']:
        #     for send_string in send_string_list:
        #         send_public_msg(send_string, message_info['group_qq'])
        send_string = ''
        for string in send_string_list:
            send_string += string
        send_long_msg(message_info, send_string)
    except requests.RequestException:
        send_string = '获取热榜超时,请重试'
        if message_info['is_private']:
            send_private_msg(send_string, message_info['sender_qq'])
        elif message_info['is_group']:
            send_public_msg(send_string, message_info['group_qq'])


@add_command('热评')
def zhihu_hot(message_info):
    message:str = message_info['message']
    try:
        length = int(message[2])
    except:
        return
    search_item:str = message[3:].strip()
    url = f'https://musicapi.leanapp.cn/search?keywords={urllib.parse.quote(search_item)}'
    json = get_one_page(url, 'json')
    if json == 'failed':
        send_string = "获取 %s 热评失败\n该歌曲不存在" % search_item
    elif json == 'time_out':
        send_string = "获取 %s 热评超时，请重试" % search_item
    else:
        song_id = parse_netease_song(json, search_item)[1]
        print('song_id', song_id)
        if not song_id:
            send_string = "获取 %s 热评失败\n该歌曲不存在" % search_item
        else:
            url = f'http://music.163.com/api/v1/resource/comments/R_SO_4_{song_id}?limit=20&offset=0'
            json = get_one_page(url, 'json')
            comment_list = parse_netease_comment(json)
            send_string = ''
            for index in range(length):
                send_string += f'{str(index + 1)}.{comment_list[index]}\n'
            print(send_string)
    send_long_msg(message_info, send_string[:-1])


@add_command('翻译成')
def translate(message_info):
    message:str = message_info['message']
    type, text =  message[:message.find(' ')][3:], message[message.find(' ') + 1:]
    new_type = LANGUAGE_DICT.get(type, message.find(' '))
    if message.find(' ') == -1 or not new_type:
        send_string = '格式错误，请使用\n[翻译成目标语言 待翻译文本]\n的格式发送消息。'
        if message_info['is_private']:
            send_private_msg(send_string, message_info['sender_qq'])
        elif message_info['is_group']:
            send_public_msg(send_string, message_info['group_qq'])
        return
    salt = randint(1000000000, 9999999999)
    md5 = hashlib.md5()
    md5.update(f'{BAIDU_TRANS_ID}{text}{salt}{BAIDU_TRANS_KEY}'.encode('utf8'))
    sign = md5.hexdigest()
    url = 'http://fanyi-api.baidu.com/api/trans/vip/translate'
    headers = {
        'User-Agent': UserAgent,
        'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'q': text,
        'from': 'auto',
        'to': new_type,
        'appid': BAIDU_TRANS_ID,
        'salt': salt,
        'sign': sign}
    result = loads(requests.post(url, data, headers=headers).text)
    while result.get('error_code') == '52003':
        sleep(1)
        result = loads(requests.post(url, data, headers=headers).text)
    try:
        new_text = result.get('trans_result')[0].get('dst')
        send_string = f'{text[:30]}...翻译成{type}:\n{new_text}'
    except:
        if 'error_code' in result:
            send_string = f'error_code{result.get("error_code")}'
        else:
            send_string = '格式错误，请使用\n[翻译成目标语言 待翻译文本]\n的格式发送消息.'
    print(send_string)
    send_long_msg(message_info, send_string)


@add_command('/')
def send_admin_msg(message_info):
    from command.event_handle import get_group_admin, leave_group
    message:str = message_info['message']
    if message[:5] == '/send':
        dot_send_msg(message_info)
    elif message[:2] == '/r':
        expression(message_info)
    elif message[:5] == '/help':
        show_command_doc(message_info)
    elif message[:7] == '/phasor':
        calculate_phasor(message_info)
    if not message_info['is_group']:
        return
    if message == '/leave':
        if message_info['sender_qq'] in get_group_admin(message_info):
            leave_group(message_info)
        else:
            send_public_msg('请让管理员发送该命令', message_info['group_qq'])
    elif message == '/bot off' and message_info['sender_qq'] in get_group_admin(message_info):
        from main_handle import set_active
        set_active(message_info, False)

