import torch
import torch.nn as nn
import jieba


def embedding(sentence):
    """
    TODO: 需要优化
    :param sentence: 文本
    :return: 文本向量
    """
    # 将句子分词
    # tokenized_sentences = sentence.split()
    # 将句子分词
    tokenized_sentences = list(jieba.cut(sentence))

    # 构建词汇表
    word2idx = {}
    idx = 0
    for word in tokenized_sentences:
        if word not in word2idx:
            word2idx[word] = idx
            idx += 1

    # 设置随机种子
    torch.manual_seed(7)

    # 构建嵌入矩阵
    embedding_dim = 64
    eb = nn.Embedding(len(word2idx), embedding_dim)

    # 将句子转换为嵌入向量
    indexed_sentence = [word2idx[word] for word in tokenized_sentences]
    tensor_sentence = torch.LongTensor(indexed_sentence)
    embedded_sentence = eb(tensor_sentence)

    # 使用平均池化操作将嵌入向量转换为长度为64的一维向量
    pooled_sentence = torch.mean(embedded_sentence, dim=0)

    # 将输出张量展平成一维数组
    flattened_output = pooled_sentence.flatten().detach().numpy()
    return flattened_output
