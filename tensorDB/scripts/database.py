import requests
import pymysql
import numpy as np
import os
from tqdm import tqdm
from scripts import split
from scripts import embedding


class Mysql:
    """
    TODO: 应先创建数据库
    +--------+------+------+-----+---------+-------+
    | Field  | Type | Null | Key | Default | Extra |
    +--------+------+------+-----+---------+-------+
    | index  | int  | NO   | PRI | NULL    |       |
    | text   | text | YES  |     | NULL    |       |
    | tensor | blob | YES  |     | NULL    |       |
    +--------+------+------+-----+---------+-------+
    :param user: 用户名
    :param pw: 密码
    :param db_name: 数据库名称
    :param tb_name: 表名称
    :param host: 地址(缺省值‘localhost’)
    :param port: 端口(缺省值3306)
    """

    def __init__(self, user, pw, db_name, tb_name, host='localhost', port=3306):
        self.__user = user
        self.__pw = pw
        self.__db_name = db_name
        self.__tb_name = tb_name
        self.__host = host
        self.__port = port

    def __set(self, index, text, tensor):
        """
        添加向量集到数据库
        :param index: 序号
        :param text: 文本
        :param tensor: 向量
        """
        # 连接MySQL数据库
        try:
            db = pymysql.connect(host=self.__host, user=self.__user, passwd=self.__pw, port=self.__port)
            # print('database connected')
            cursor = db.cursor()

            # 将向量存入数据库
            cursor.execute('USE ' + self.__db_name)
            tensor_bytes = tensor.tobytes()
            cursor.execute(
                'INSERT INTO ' + self.__tb_name + ' (`index`,text,tensor) VALUES (%s,%s,%s)',
                (index, text, tensor_bytes,))
            try:
                db.commit()  # 提交事务
                # print('insertion completed')
                db.close()  # 关闭数据库连接
            except Exception as e:
                print('ERROR: ', e)
                db.rollback()
                cursor.close()
                db.close()
        except Exception as e:
            print('ERROR: ', e)

    def __set_pdf(self):
        """
        将data/pdf中的文件存入数据库
        notion: 保存前会清空数据库中原有数据,本函数不是追加功能
        """
        self.__clear()
        data_path = 'data/PDF'
        index = 0
        if not os.path.isdir(data_path):
            print(f"Error: '{data_path}' is not a valid directory.")
            return

        files = os.listdir(data_path)
        file_count = len(files)

        for i, filename in enumerate(files):
            old_path = os.path.join(data_path, filename)
            new_filename = f"article{i}.pdf"
            new_path = os.path.join(data_path, new_filename)
            os.rename(old_path, new_path)

        for i in tqdm(range(file_count), desc='article'):
            pdf_path = data_path + '/article' + str(i) + '.pdf'

            # 分割文本并词嵌入
            sp = split.SplitPDF(pdf_path)
            sr = sp.split()
            er = []
            for text in sr:
                er.append(embedding.embedding(text))
            er = np.array(er)
            for j in tqdm(range(len(sr)), desc='inserting'):
                self.__set(index, sr[j], er[j])
                index += 1

    def __get_max_ind(self):
        try:
            db = pymysql.connect(host=self.__host, user=self.__user, passwd=self.__pw, port=self.__port)
            cursor = db.cursor()
            cursor.execute('USE ' + self.__db_name)
            cursor.execute('SELECT MAX(`index`) FROM ' + self.__tb_name)
            result = cursor.fetchone()
            if result:
                index = result[0]
            else:
                index = 0
            cursor.close()
            db.close()
            return index
        except Exception as e:
            print('ERROR: ', e)

    def __clear(self):
        """
        删库
        """
        try:
            db = pymysql.connect(host=self.__host, user=self.__user, passwd=self.__pw, port=self.__port)
            # print('database connected')
            cursor = db.cursor()
            cursor.execute('USE ' + self.__db_name)
            cursor.execute('DELETE FROM ' + self.__tb_name)
            try:
                db.commit()  # 提交事务
                db.close()  # 关闭数据库连接
            except Exception as e:
                print('ERROR: ', e)
                db.rollback()
                cursor.close()
                db.close()
        except Exception as e:
            print('ERROR: ', e)

    def get_tensors_by_ind(self, start_index=0, end_index=-1):
        """
        通过序号范围读取向量
        :param start_index: 起始序号（缺省为0）
        :param end_index: 结束序号（缺省为最大）
        :return: 向量列表
        """
        if end_index == -1:
            end_index = self.__get_max_ind()
        if start_index == -1:
            start_index = self.__get_max_ind()
        try:
            db = pymysql.connect(host=self.__host, user=self.__user, passwd=self.__pw, port=self.__port)
            cursor = db.cursor()
            cursor.execute('USE ' + self.__db_name)
            cursor.execute('SELECT tensor FROM ' + self.__tb_name + ' WHERE `index` BETWEEN %s AND %s',
                           (start_index, end_index))
            tensors = [np.frombuffer(row[0], dtype=np.float32) for row in cursor.fetchall()]
            tensors = np.array(tensors)
            cursor.close()
            db.close()
            return tensors
        except Exception as e:
            print('ERROR: ', e)

    def get_texts_by_ind(self, start_index=0, end_index=-1):
        """
        通过序号范围读取文本
        :param start_index: 起始序号（缺省为0）
        :param end_index: 结束序号（缺省为最大）
        :return: 文本列表
        """
        if end_index == -1:
            end_index = self.__get_max_ind()
        if start_index == -1:
            start_index = self.__get_max_ind()
        try:
            db = pymysql.connect(host=self.__host, user=self.__user, passwd=self.__pw, port=self.__port)
            cursor = db.cursor()
            cursor.execute('USE ' + self.__db_name)
            cursor.execute('SELECT text FROM ' + self.__tb_name + ' WHERE `index` BETWEEN %s AND %s',
                           (start_index, end_index))
            texts = [row[0] for row in cursor.fetchall()]
            cursor.close()
            db.close()
            return texts
        except Exception as e:
            print('ERROR: ', e)

    def add_pdf(self, url):
        """
        根据链接将pdf入库
        :param url: 下载链接
        """
        print("downloading article...")
        destination = 'data/pdf/tmp_article.pdf'

        response = requests.get(url)
        with open(destination, 'wb') as file:
            file.write(response.content)

        index = self.__get_max_ind() + 1 if self.__get_max_ind() != 0 else 0
        data_path = 'data/PDF'
        pdf_path = data_path + '/tmp_article.pdf'

        # 分割文本并词嵌入
        sp = split.SplitPDF(pdf_path)
        sr = sp.split()
        er = []
        for text in sr:
            er.append(embedding.embedding(text))
        er = np.array(er)
        for j in tqdm(range(len(sr)), desc='inserting'):
            self.__set(index, sr[j], er[j])
            index += 1
        os.remove('data/pdf/tmp_article.pdf')

    def reset(self):
        """
        通过data/PDF文件夹中的文章重建数据库
        """
        self.__set_pdf()
