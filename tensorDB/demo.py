import numpy as np
from scripts import embedding
from scripts.database import Mysql
from scripts import search

if __name__ == '__main__':
    # 生成查询集
    query_sentence = 'I extend this account in two ways'
    query = [embedding.embedding(query_sentence)]  # 查询集
    query = np.array(query).astype('float32')

    # 生成数据集,并存入数据库
    # TODO: 输入MySQL用户名、密码、数据库名称、表名称、地址(缺省localhost)、端口(缺省3306)
    db = Mysql(user='guest', pw='12345', db_name='301med', tb_name='data')
    url = 'https://www.gjtool.cn/pdfh5/git.pdf'
    db.add_pdf(url)
    data = db.get_tensors_by_ind()

    # faiss查询————精确搜索
    ind = search.faiss_flat(64, data, query, 1)
    print('index:', ind)
    print(db.get_texts_by_ind(ind, ind)[0])

    # faiss查询————乘积量化搜索(Product Quantizer)
    ind = search.faiss_pq(64, 8, 6, data, query, 1)
    print('index:', ind)
    print(db.get_texts_by_ind(ind, ind)[0])

    db.reset()
