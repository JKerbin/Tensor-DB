import numpy as np
import requests

# 定义 API 地址
base_url = 'http://127.0.0.1:8080/'
mysql_config = {'user': 'guest', 'pw': '12345', 'db_name': '301med', 'tb_name': 'data', 'host': 'localhost',
                'port': 3306}


# 示例函数：获取张量
def get_tensors(start_index=0, end_index=-1):
    url = base_url + 'get_tensors'
    params = {'start_index': start_index, 'end_index': end_index, 'user': mysql_config['user'],
              'pw': mysql_config['pw'], 'db_name': mysql_config['db_name'], 'tb_name': mysql_config['tb_name'],
              'host': mysql_config['host'], 'port': mysql_config['port']}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        tensors = np.array(response.json()['tensors'])
        return tensors
    else:
        print('requests failed')


# 示例函数：获取文本
def get_texts(start_index=0, end_index=-1):
    url = base_url + 'get_texts'
    params = {'start_index': start_index, 'end_index': end_index, 'user': mysql_config['user'],
              'pw': mysql_config['pw'], 'db_name': mysql_config['db_name'], 'tb_name': mysql_config['tb_name'],
              'host': mysql_config['host'], 'port': mysql_config['port']}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        texts = response.json()['texts']
        return texts
    else:
        print('requests failed')


# 示例函数：添加 PDF
def add_pdf(pdf_url):
    url = base_url + 'add_pdf'
    data = {'url': pdf_url, 'user': mysql_config['user'], 'pw': mysql_config['pw'], 'db_name': mysql_config['db_name'],
            'tb_name': mysql_config['tb_name'], 'host': mysql_config['host'], 'port': mysql_config['port']}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print(response.json()['message'])
    else:
        print('requests failed')


def query(text):
    url = base_url + 'query'
    data = {'text': text, 'user': mysql_config['user'], 'pw': mysql_config['pw'], 'db_name': mysql_config['db_name'],
            'tb_name': mysql_config['tb_name'], 'host': mysql_config['host'], 'port': mysql_config['port']}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        ind = response.json().get('index')
        res = response.json().get('result')
        return ind, res
    else:
        print('Request failed')
        return None, None


# 调用示例函数
if __name__ == "__main__":
    # 示例：获取张量
    data_tensors = get_tensors(start_index=-1)
    print(data_tensors.shape)

    # 示例：获取文本
    data_texts = get_texts(start_index=-1)
    print(data_texts)

    # 示例：添加 PDF
    add_pdf('https://www.gjtool.cn/pdfh5/git.pdf')

    data_qi, data_qr = query(text='这是一个测试语句，我是开发者')
    print(data_qi)
    print(data_qr)
