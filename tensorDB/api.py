import numpy as np
from flask import Flask, request, jsonify
from gevent import pywsgi
from scripts.database import Mysql
from scripts import embedding
from scripts import search

app = Flask(__name__)


@app.route('/get_tensors', methods=['GET'])
def get_tensors():
    start_index = request.args.get('start_index', default=0, type=int)
    end_index = request.args.get('end_index', default=-1, type=int)
    user = request.args.get('user')
    pw = request.args.get('pw')
    db_name = request.args.get('db_name')
    tb_name = request.args.get('tb_name')
    db_host = request.args.get('host', default='localhost', type=str)
    db_port = request.args.get('port', default=3306, type=int)
    mysql_instance = Mysql(user=user, pw=pw, db_name=db_name, tb_name=tb_name, host=db_host, port=db_port)
    tensors = mysql_instance.get_tensors_by_ind(start_index=start_index, end_index=end_index)
    return jsonify({'tensors': tensors.tolist()})


@app.route('/get_texts', methods=['GET'])
def get_texts():
    start_index = request.args.get('start_index', default=0, type=int)
    end_index = request.args.get('end_index', default=-1, type=int)
    user = request.args.get('user')
    pw = request.args.get('pw')
    db_name = request.args.get('db_name')
    tb_name = request.args.get('tb_name')
    db_host = request.args.get('host', default='localhost', type=str)
    db_port = request.args.get('port', default=3306, type=int)
    mysql_instance = Mysql(user=user, pw=pw, db_name=db_name, tb_name=tb_name, host=db_host, port=db_port)
    texts = mysql_instance.get_texts_by_ind(start_index=start_index, end_index=end_index)
    return jsonify({'texts': texts})


@app.route('/add_pdf', methods=['POST'])
def add_pdf():
    data = request.get_json()
    url = data['url']
    user = data.get('user')
    pw = data.get('pw')
    db_name = data.get('db_name')
    tb_name = data.get('tb_name')
    db_host = request.args.get('host', default='localhost', type=str)
    db_port = request.args.get('port', default=3306, type=int)
    mysql_instance = Mysql(user=user, pw=pw, db_name=db_name, tb_name=tb_name, host=db_host, port=db_port)
    mysql_instance.add_pdf(url)
    return jsonify({'message': 'PDF added successfully.'})


@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    text = data['text']
    query_tensor = [embedding.embedding(text)]
    query_tensor = np.array(query_tensor).astype('float32')
    user = data.get('user')
    pw = data.get('pw')
    db_name = data.get('db_name')
    tb_name = data.get('tb_name')
    db_host = request.args.get('host', default='localhost', type=str)
    db_port = request.args.get('port', default=3306, type=int)
    mysql_instance = Mysql(user=user, pw=pw, db_name=db_name, tb_name=tb_name, host=db_host, port=db_port)
    tensors = mysql_instance.get_tensors_by_ind()
    # faiss查询————精确搜索
    ind = search.faiss_flat(64, tensors, query_tensor, 1)
    res = mysql_instance.get_texts_by_ind(ind, ind)[0]
    return jsonify({'index': int(ind), 'result': res})


if __name__ == '__main__':
    port = 8080
    print('Running on http://127.0.0.1:' + str(port))
    server = pywsgi.WSGIServer(('0.0.0.0', port), app)
    server.serve_forever()
