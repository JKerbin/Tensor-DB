import faiss


def faiss_flat(d, data, query, rn):
    """
    faiss查询————精确搜索
    :param d: 维数
    :param data: 向量集
    :param query: 查询集
    :param rn: 查询数
    :return: 结果索引(ind)
    """
    # print('faiss查询————精确搜索')
    try:
        index = faiss.IndexFlatL2(d)
        index.add(data)
        dis, ind = index.search(query, rn)
        return ind[0][0]
    except Exception as e:
        print('ERROR: ', e)


def faiss_pq(d, m, nbits, data, query, rn):
    """
    faiss查询————乘积量化搜索(Product Quantizer)(更快)
    :param d: 维数
    :param m: 乘积量化因子(应为维数的因数)
    :param nbits: 压缩后大小
    :param data: 向量集
    :param query: 查询集
    :param rn: 查询数
    :return: 结果索引(ind)
    """
    # print('faiss查询————乘积量化搜索(Product Quantizer)')
    try:
        index = faiss.IndexPQ(d, m, nbits)
        index.train(data)
        index.add(data)
        dis, ind = index.search(query, rn)
        return ind[0][0]
    except Exception as e:
        print('ERROR: ', e)
