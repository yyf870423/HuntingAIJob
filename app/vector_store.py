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

def query_candidates(query_embedding, n_results=5, where=None, similarity_threshold=None):
    """
    query_embedding: List[float]
    n_results: int
    where: dict, 可选，元数据筛选条件
    similarity_threshold: float, 可选，相似度阈值（仅余弦距离，0~1，越大越相似）
    """
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where
    )
    if similarity_threshold is not None:
        # 只保留相似度 >= 阈值的结果（余弦距离：sim = 1 - dist）
        filtered = {
            'ids': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        for i, (id, meta, dist) in enumerate(zip(result['ids'][0], result['metadatas'][0], result['distances'][0])):
            sim = 1 - dist
            if sim >= similarity_threshold:
                filtered['ids'][0].append(id)
                filtered['metadatas'][0].append(meta)
                filtered['distances'][0].append(dist)
        return filtered
    return result

if __name__ == "__main__":
    # 1. 向量检索：有没有适合做大模型推理性能优化的候选人？选 top 30
    query_text = '''
大模型推理引擎负责人
工作内容
1.负责大模型推理引擎的开发和优化，特别是针对MOE架构专家分布式的推理性能优化；
2.深入研究和实现MOE模型的底层技术优化，包括CUDA/Kernel算子优化、内存/显存管理策略和计算图优化等；
3.设计和优化MOE模型的专家分布式调度策略，实现高效的专家路由和负载均衡；
4.针对MOE架构大模型进行通信优化，包括通信性能和通信/计算策略流程的优化，减少分布式推理中的通信开销；
5.探索和实现大模型推理引擎的前沿技术，推动团队技术能力的持续提升，同时编写高质量的技术文档，参与团队技术分享和知识沉淀。
任职资格
1.学历要求： 计算机科学、人工智能、软件工程或相关专业，硕士及以上学历；
2.技术背景：
    * 熟悉深度学习框架（如PyTorch、TensorFlow等），具有大模型开发和优化的实际经验；
    * 深入理解MOE（Mixture of Experts）架构，具备相关模型的设计和优化经验；
    * 熟悉GPU/TPU硬件架构，具备CUDA、OpenCL等高性能计算开发经验；
    * 熟悉分布式训练和推理技术，了解NCCL、MPI、RDMA等通信库的优化策略；
    * 具备底层计算优化经验，如算子融合、内存优化、计算图优化等。
3.编程能力： 精通Python、C++，具备高性能代码开发和调试能力；
4.加分项：
    * 在顶级会议（如NeurIPS、ICML、CVPR等）发表过相关论文；
    * 有大规模分布式系统开发经验，熟悉Kubernetes、Docker等容器化技术；
    * 熟悉大模型推理引擎（如DeepSpeed、vllm和sglang等）的源码和优化策略。
'''
    query_emb = get_embedding_from_llm(query_text)
    print("\n【向量检索 Top 30】")
    result = query_candidates(query_emb, n_results=30, similarity_threshold=0.8)
    for i, (id, meta, dist) in enumerate(zip(result['ids'][0], result['metadatas'][0], result['distances'][0]), 1):
        print(f"Top {i} | id: {id} | 距离: {dist:.4f} | 元数据: {meta}")

    # # 2. 元数据搜索：学历是硕士及以上的数据
    # print("\n【元数据检索：学历=硕士及以上】")
    # # 这里假设元数据字段学历为"硕士"或"博士"
    # for degree in ["硕士", "博士"]:
    #     where = {"学历": degree}
    #     result = query_candidates(query_emb, n_results=5, where=where)
    #     for i, (id, meta, dist) in enumerate(zip(result['ids'][0], result['metadatas'][0], result['distances'][0]), 1):
    #         print(f"学历={degree} | Top {i} | id: {id} | 距离: {dist:.4f} | 元数据: {meta}")
