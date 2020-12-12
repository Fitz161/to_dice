import threading
from flask import Flask, request
import logging, os, json
from queue import Queue
from main_handle import handle_message, timing_task
from config import PORT, ADMIN_LIST

# 去除flask提示
os.environ['WERKZEUG_RUN_MAIN'] = "true"
# 去除 Flask的log
logging.getLogger('werkzeug').setLevel(logging.ERROR)

bot = Flask(__name__)
message_queue = Queue()

@bot.route('/api/message',methods=['POST'])
def message():
    data = request.get_data().decode('utf-8')
    data:dict = json.loads(data)
    if 'meta_event_type' in data:
        return ''
    elif data.get('message') == '/exit' and data.get('user_id') in ADMIN_LIST:
        exit()
    message_queue.put(data)
    return ''


if __name__ == '__main__':
    #logging.log(logging.INFO,f'机器人开始运行，监听端口：{PORT}')
    threading.Thread(target=handle_message, args=(message_queue,), daemon=True).start()
    threading.Thread(target=timing_task, daemon=True).start()
    #设置为守护进程，这样主程序结束时线程也会结束
    #handle_message(message_queue) 由于该函数是个死循环，不会执行下面的bot.run，要创建新线程
    bot.run(port=PORT)
