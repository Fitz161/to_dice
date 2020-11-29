from flask import Flask, request
import logging
import os
import json
from queue import Queue
from main_handle import handle_message
import config

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
    message_queue.put(data)
    return ''


if __name__ == '__main__':
    logging.log(logging.INFO,'机器人开始运行，监听端口：5701')
    handle_message(message_queue)
    bot.run(host='0.0.0.0', port=5701)
