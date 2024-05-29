# 环境要求

基于mysql和faiss的词向量生成搜索工具。

## 支持功能

- 支持简单的文章分词和内容向量化
- 支持将向量化的内容保存在数据库中
- 通过词向量对比搜索数据库中近似内容

## 相关依赖

- mysql
- Python 3.12.2

```bash
pip install -r requirements.txt
conda install faiss-cpu -c pytorch #cpu 版本
```
