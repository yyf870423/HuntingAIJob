import chromadb
from chromadb.config import Settings
import os
from app.llm import get_embedding_from_llm

# 初始化 Chroma 持久化客户端
CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "store", "chroma_db")
client = chromadb.PersistentClient(path=CHROMA_PATH)

# 获取/创建 collection
COLLECTION_NAME = "candidates"
collection = client.get_or_create_collection(COLLECTION_NAME)

def add_candidate(candidate_id, embedding, metadata):
    """
    candidate_id: str, 唯一标识
    embedding: List[float], 由经历文本生成的向量
    metadata: dict, 其他元数据字段
    """
    collection.upsert(
        ids=[candidate_id],
        embeddings=[embedding],
        metadatas=[metadata]
    )

def query_candidates(query_embedding, n_results=5, where=None):
    """
    query_embedding: List[float]
    n_results: int
    where: dict, 可选，元数据筛选条件
    """
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where
    )

if __name__ == "__main__":
    # 1. 向量检索：有没有适合做大模型推理性能优化的候选人？选 top 3
    query_text = "大模型推理性能优化"
    query_emb = get_embedding_from_llm(query_text)
    print("\n【向量检索：大模型推理性能优化，Top 3】")
    result = query_candidates(query_emb, n_results=3)
    for i, (id, meta, dist) in enumerate(zip(result['ids'][0], result['metadatas'][0], result['distances'][0]), 1):
        print(f"Top {i} | id: {id} | 距离: {dist:.4f} | 元数据: {meta}")

    # 2. 元数据搜索：学历是硕士及以上的数据
    print("\n【元数据检索：学历=硕士及以上】")
    # 这里假设元数据字段学历为"硕士"或"博士"
    for degree in ["硕士", "博士"]:
        where = {"学历": degree}
        result = query_candidates(query_emb, n_results=5, where=where)
        for i, (id, meta, dist) in enumerate(zip(result['ids'][0], result['metadatas'][0], result['distances'][0]), 1):
            print(f"学历={degree} | Top {i} | id: {id} | 距离: {dist:.4f} | 元数据: {meta}")

# TODO: 实现 FAISS 向量索引的加载、查询、更新等操作 