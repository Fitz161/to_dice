#encoding=utf8
import os
from PIL import Image
from random import sample, choices
import requests, random
from json import loads,load,dump
from bs4 import BeautifulSoup as bp
from requests import RequestException
import urllib.parse
command_dict={}
admin_command_dict={}

# def add_command(command):  # 工厂函数，用来接受@add_command('签到')的'签到'
#     def add_func(func):
#         def decorater():
#             command_dict[command] = func
#         return decorater
#     return add_func

def add_command(command):  # 工厂函数，用来接受@add_command('签到')的'签到'
    def add_func(func):
        command_dict[command] = func
    return add_func

@add_command('签到') #参数传入command
def send_message(send_string, QQ=None, group_id=None):
    data = {
            'message':send_string,
            'auto_escape':False
    }
    data.update({'user_id': QQ} if not group_id else {'group_id': group_id})
    api_url = 'http://127.0.0.1:5700/send_private_msg' if not group_id else 'http://127.0.0.1:5700/send_group_msg'
    r = requests.post(api_url, data=data)
    if r.status_code == 200:
        print("消息发送成功")

def send_image(card_type=0, type=1, QQ=None, group_id=None):
    concat_images(get_image_names(PATH[card_type], type), PATH[card_type], type)
    print("图片生成成功")
    data = {
        'message':"[CQ:image,file=file:///packages/pic.jpg]",
        'auto_escape':False
    }
    data.update({'user_id': QQ} if not group_id else {'group_id': group_id})
    api_url = 'http://127.0.0.1:5700/send_private_msg' if not group_id else 'http://127.0.0.1:5700/send_group_msg'
    requests.post(api_url, data=data)

def concat_images(image_names, path, type):
    if type == 2:
        COL = 5
        ROW = 2
    elif type == 3:
        COL = 10
        ROW = 10
    else :
        COL = 1
        ROW = 1
    UNIT_HEIGHT_SIZE = 900
    UNIT_WIDTH_SIZE = 600
    image_files = []
    for index in range(COL*ROW):
        image_files.append(Image.open(path + image_names[index]))
    target = Image.new('RGB', (UNIT_WIDTH_SIZE * COL, UNIT_HEIGHT_SIZE * ROW))
    for row in range(ROW):
        for col in range(COL):
            target.paste(image_files[COL*row+col], (0 + UNIT_WIDTH_SIZE*col, 0 + UNIT_HEIGHT_SIZE*row))
    if COL == 10:
        global SAVE_QUALITY
        SAVE_QUALITY = 40
        width = target.size[0]
        height = target.size[1]
        target = target.resize((int(width * 0.5), int(height * 0.5)), Image.ANTIALIAS)
    target.save(r'/packages/pic.jpg', quality=SAVE_QUALITY)


def get_image_names(path, type):
    if type == 2:
        COL = 5
        ROW = 2
    elif type == 3:
        COL = 10
        ROW = 10
    else:
        COL = 1
        ROW = 1
    image_names = list(os.walk(path))[0][2]
    selected_images = choices(image_names, k=COL*ROW) if REPEAT_SELECT else sample(image_names, COL*ROW)
    return selected_images

def sign_in_response(QQ, nickname, group_id):
    with open("/bot/data.json") as f:
        total_data = load(f)
    total_data.setdefault('%s'%QQ, {'days': 0, 'today': 0, 'points': 0})
    data = total_data['%s'%QQ]
    days = data['days']
    today = data['today']
    points = data['points']
    if today==0:
        today = 1
        days += 1
        point = random.randint(20,50) + days*5
        points += point
        send_string = '[CQ:at,qq=%d]\n签到成功~!\n本次获得香火钱:%d\n剩余香火钱:%d\n累计签到:%d天'%(
            QQ, point, points, days)
        total_data["%s"%QQ] = {'days': days, 'today': today, 'points': points}
    else:
        send_string = '[CQ:at,qq=%d]\n今天已经签到过了呢~'%QQ
    send_message(send_string, QQ, group_id)
    with open("/bot/data.json","w") as f:
        dump(total_data, f)

def sign_in_info(QQ, nickname, group_id):
    with open("/bot/data.json") as f:
        total_data = load(f)
    data = total_data.get(str(QQ), None)
    if not data:
        send_message("[CQ:at,qq=%d]\n无签到信息"%QQ, QQ, group_id)
    else:
        days = data['days']
        points = data['points']
        send_string = "[CQ:at,qq=%d]\n香火钱:%d\n累计签到%d天"%(QQ, points, days)
        send_message(send_string, QQ, group_id)

def learn(message):
    with open("/bot/learn.json") as f:
        total_dict = load(f)
        key,value = message[3:].strip().split("*")
        total_dict[key] = value
    with open("/bot/learn.json", "w") as f:
        dump(total_dict,f)
    print("%s:%s保存成功"%(key,value))

def learn_response(message, QQ, group_id):
    with open("/bot/learn.json") as f:
        total_dict = load(f)
        send_message('%s'%total_dict[message], QQ, group_id)

def get_one_page(url):
    s = requests.session()
    s.keep_alive = False
    headers = {
        "Connection":"close",
        "User-Agent": r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
    try:
        response = requests.get(url, headers = headers, timeout = 8)
        if response.status_code == 200:
            print(response.status_code)
            return response.content
        else:
            print(response.status_code)
            return "failed"
    except RequestException as e:
        print("request failed",e)
        return "time_out"

def parse_one_page(html,option):
    soup = bp(html, "lxml")
    select_list = ['body #content #bodyContent #mw-content-text .mw-parser-output > p',
                   'body #content #bodyContent #mw-content-text .mw-parser-output .mw-parser-output > p']
    content = soup.select(select_list[option])
    string = ''
    for item in content:
        string += item.get_text()
    print(string[:150])
    return string[:150]+'...'

def search_moegirl(message, QQ, group_id):
    url = 'https://zh.moegirl.org/'+urllib.parse.quote(message.strip())
    html = get_one_page(url)
    if html == 'failed':
        send_message("搜索 %s 失败\n该条目不存在"%message.strip(), QQ, group_id)
    elif html == 'time_out':
        send_message("搜索 %s 超时，请重试"%message.strip(), QQ, group_id)
    else:
        new_message = parse_one_page(html,0)
        if new_message == None:
            send_message("搜索 %s 失败\n没有该条目"%(message.strip()), QQ, group_id)
        else:
            send_message("搜索 %s :\n%s"%(message.strip(), new_message), QQ, group_id)

def search_baidu(message, QQ, group_id):
    url = 'https://baike.baidu.com/item/'+urllib.parse.quote(message)
    print(url)
    html = get_one_page(url)
    if html == 'failed':
        send_message("搜索 %s 失败\n该条目不存在"%message)
    elif html == 'time_out':
        send_message("搜索 %s 超时，请重试"%message)
    else:
        soup = bp(html, "lxml")
        content = soup.head.find_all(name = 'meta')
        try:
            new_message = content[3].attrs["content"]
        except IndexError:
            new_message = None
        if new_message == None:
            send_message("搜索 %s 失败\n没有该条目"%message, QQ, group_id)
        else:
            send_message("搜索 %s :\n%s"%(message,new_message), QQ, group_id)

def parse_song_page(json, message):
    list2=[]
    dict1 = {}
    with open('/bot/search_song.json') as f:
        dict1 = load(f)
        last_search = dict1['last_search']
        index = dict1['index']
    if last_search == message:
        index += 1
    else:
        index = 0
    dict1['last_search'] = message
    dict1['index'] = index
    dump(dict1, open('/bot/search_song.json','w'))
    json = loads(json)
    list1 = json['data']['song']['list']
    for item in list1:
        list2.append(item['mid'])
    url = r'https://y.qq.com/n/yqq/song/{}.html'.format(list2[index])
    print(url)
    return url

def search_thwiki(message, QQ, group_id):
    url = 'https://thwiki.cc/' + urllib.parse.quote(message[3:].strip())
    html = get_one_page(url)
    if html == 'failed':
        send_message("搜索 %s 失败\n该条目不存在" % message[3:].strip(), QQ, group_id)
    elif html == 'time_out':
        send_message("搜索 %s 超时，请重试" % message[3:].strip(), QQ, group_id)
    else:
        new_message = parse_one_page(html,1)
        if new_message == None:
            send_message("搜索 %s 失败\n没有该条目" % (message[3:].strip()), QQ, group_id)
        else:
            send_message("搜索 %s :\n%s" % (message[3:].strip(), new_message), QQ, group_id)

def search_song(message, QQ, group_id):
    search_item = message[2:].strip()
    url = r'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.center&searchid=46369776929740470&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n=10&w={}&g_tk_new_20200303=138867905&g_tk=138867905&loginUin=2224546887&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0'.format(search_item.replace(' ','%20'))
    html = get_one_page(url)
    if html == 'failed':
        send_message("点歌 %s 失败\n该条目不存在"%search_item, QQ, group_id)
    elif html == 'time_out':
        send_message("点歌 %s 超时，请重试"%search_item, QQ, group_id)
    else:
        new_message = parse_song_page(html, message)
        if new_message == None:
            send_message("点歌 %s 失败\n没有该条目"%(search_item), QQ, group_id)
        else:
            send_message("%s"%new_message, QQ, group_id)

def knowledge(QQ, group_id):
    with open("/bot/knowledge.json") as f:
        data_dict = load(f)
    message = data_dict[str(random.randint(0, 46))]
    print(message)
    send_message(message, QQ, group_id)

def reset():
    with open("/bot/data.json") as f:
        data_dict = load(f)
    for name in data_dict.keys():
        data_dict[name]["today"] = 0
    with open("/bot/data.json", "w") as f:
        dump(data_dict, f)

def send_gift(QQ, group_id):
    type = random.randint(0, 13)
    message = "[CQ:gift,qq=%d,id=%d]"%(QQ, type)
    send_message(message, QQ, group_id)

def server_stat(QQ, group_id):
    mem = {}
    f = open('/proc/meminfo')
    lines = f.readlines()
    f.close()
    for line in lines:
        if len(line) < 2:
            continue
        name = line.split(':')[0]
        var = line.split(':')[1].split()[0]
        mem[name] = float(var)
    mem['MemUsed'] = mem['MemTotal'] - mem['MemFree'] - mem['Buffers'] - mem['Cached']
    mem_avg = '内存使用率:{}%\n已使用内存:{}GB\n总内存:{}GB\nBuffers:{}GB\n'.format(int(round(mem['MemUsed'] / mem['MemTotal'] * 100)),
                                                                   round(mem['MemUsed'] / (1024 * 1024), 2),
                                                                   round(mem['MemTotal'] / (1024 * 1024), 2),
                                                                   round(mem['Buffers'] / (1024 * 1024), 2))
    f = open("/proc/loadavg")
    con = f.read().split()
    f.close()
    cpu_avg = '5分钟内CPU负载:{}\n10分钟内CPU负载:{}\n15分钟内CPU负载:{}'.format(con[0], con[1], con[2])
    res = mem_avg + cpu_avg
    print(res)
    send_message(res, QQ, group_id)

def bot_status(QQ, group_id):
    api_url = 'http://127.0.0.1:5700/get_status'
    text = requests.post(api_url).json()
    if text['data']['online']:
        send_string = "bot运行正常"
    else:
        send_string = "bot已下线"
    send_message(send_string, QQ, group_id)

