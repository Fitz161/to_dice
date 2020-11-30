from flask import Flask, request
import logging, os, json
from queue import Queue
from main_handle import handle_message
from config import PORT

# 去除flask提示
os.environ['WERKZEUG_RUN_MAIN'] = "true"
# 去除 Flask的log
logging.getLogger('werkzeug').setLevel(logging.ERROR)

bot = Flask(__name__)
message_queue = Queue()

@bot.route('/message')
def message():
    data = request.get_data().decode('utf-8')
    data = json.loads(data)
    if not 'sender' in data or 'meta_event_type' in data:
        return ''
    message_queue.put(data)
    return ''


if __name__ == '__main__':
    logging.log(logging.INFO,f'机器人开始运行，监听端口：{PORT}')
    handle_message(message_queue)
    bot.run(host='0.0.0.0', port=PORT)
