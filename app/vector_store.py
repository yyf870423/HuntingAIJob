import chromadb
from chromadb.config import Settings
import os

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
    collection.add(
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

# TODO: 实现 FAISS 向量索引的加载、查询、更新等操作 