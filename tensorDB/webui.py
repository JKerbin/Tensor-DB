import numpy as np
from scripts import embedding
from scripts.database import Mysql
from scripts import search
from flask import Flask, render_template, request
from gevent import pywsgi

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    query = [embedding.embedding(message)]  # 查询集
    query = np.array(query).astype('float32')
    ind, reply = generate_reply(query)
    with open('log/messages.txt', 'a') as f:
        f.write('User: ' + message + '\n')
        f.write('Bot: ' + reply + '\n')  # 保存回复
    return 'faiss查询成功，index=' + str(ind) + ' 文本：' + reply  # 返回回复给客户端


def generate_reply(query):
    # # TODO: 输入MySQL用户名、密码、数据库名称、表名称、地址(缺省localhost)、端口(缺省3306)
    db = Mysql(user='guest', pw='12345', db_name='301med', tb_name='data')
    data = db.get_tensors_by_ind()
    # faiss查询————精确搜索
    ind = search.faiss_flat(64, data, query, 1)
    return ind, db.get_texts_by_ind(ind, ind)[0]


if __name__ == '__main__':
    port = 80
    print('Running on http://127.0.0.1:' + str(port))
    server = pywsgi.WSGIServer(('0.0.0.0', port), app)
    server.serve_forever()
