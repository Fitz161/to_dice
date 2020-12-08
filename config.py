PAUSE_TIME=0.5
PORT = 5701

#command_list=['单抽','十连','百连','签到','信息','冷知识','跟我学','指令','百度','搜索','点歌','要礼物']
#admin_command_list=['重置','删库','去面壁','状态','召唤']
CARD_PATH = ["/packages/cards1/", "/packages/cards2/","/packages/cards3/",
        "/packages/cards4/","/packages/cards5/", "/packages/cards6/", "/packages/cards7/"]
ADMIN_LIST = []
#BLACK_LIST = []
REPEAT_SELECT = True
MULTI_THREADING = True
SAVE_QUALITY = 50
# IS_ACTIVE = True
# def get_active()->bool: #python中，不同进程之间不能共享全局变量，在创建进程时，python会把当前存在的全局变量全部copy一份，
#     return IS_ACTIVE    # 放进自己的空间中，之后各个进程之间的同名变量不再有任何关系。。各管各的。
# def set_active(b:bool): #跨文件之间的修改，只能通过函数调用这种方式来实现
#     global IS_ACTIVE
#     IS_ACTIVE = b

SAVE_PATH = '/packages/pics/'
DATA_PATH = '/bot/data.json'
LEARN_PATH = '/bot/learn.json'
SONG_PATH = '/bot/search_song.json'
SEARCH_LENGTH = 150
KNOWLEDGE_PATH = '/bot/knowledge.json'
MEMO_INFO_PATH = '/proc/meminfo'
CPU_INFO_PATH = '/proc/loadavg'
BLACK_LIST_PATH = '/bot/black_list.json'
ACTIVE_PATH = '/bot/is_active.json'

#UserAgent = r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
#UserAgent = r"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36 OPR/60.0.3255.83"
#UserAgent = r'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
UserAgent = r"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"

ZHIHU_COOKIE = ''
ZHIHU_LENGTH = 10

apiBaseUrl = 'http://127.0.0.1:5700'
apiPrivateMsg = '/send_private_msg'
apiGroupMsg = '/send_group_msg'
#apiSendMsg = '/send_msg'
apiDeleteMsg = '/delete_msg'
#apiSendLike = '/send_like'
apiFriendRequest = '/set_friend_add_request'
apiGroupRequest = '/set_group_add_request'
#apiGroupList = '/get_group_list'
#apiGroupMemberInfo = '/get_group_member_info'
apiGroupMemberList = '/get_group_member_list'
apiGroupInfo = '/get_group_info'
#apiGetRecord = '/get_record'
#apiGetImage = '/get_image'
apiSetGroupLeave = '/set_group_leave'
#apiCleanCache = '/clean_cache'
#apiRestart = '/set_restart'
