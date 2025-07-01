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
    if where is not None and len(where) == 0:
        where = None
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

def multi_vector_query(query_embeddings: dict, fields: list, n_results=5, overall_threshold=None, weights=None, where=None):
    """
    多向量字段检索，支持每个字段独立 embedding、权重，最终只对加权总分设置阈值。
    query_embeddings: dict, 维度名->embedding
    fields: list, 需要检索的维度名
    n_results: int, 返回 top N
    overall_threshold: float, 加权总相似度阈值（0~1），可选
    weights: dict, 维度名->权重（float），可选
    where: dict, 元数据筛选条件，可选
    返回: list，每项为 {id, scores: {field: sim}, weighted_score, metadatas}
    """
    if where is not None and len(where) == 0:
        where = None
    # 1. 对每个字段分别检索，取足够多的候选
    field_results = {}
    candidate_ids_set = set()
    for field in fields:
        emb = query_embeddings[field]
        res = collection.query(query_embeddings=[emb], n_results=100, where=where)
        # 记录每个字段的id->(sim, meta)
        field_results[field] = {}
        for i, (cid, meta, dist) in enumerate(zip(res['ids'][0], res['metadatas'][0], res['distances'][0])):
            sim = 1 - dist  # 余弦距离转相似度
            field_results[field][cid] = (sim, meta)
            candidate_ids_set.add(cid)
    # 2. 汇总所有候选id，计算每个id的各字段分数
    # 归一化权重
    norm_weights = {}
    if weights:
        total = sum([weights.get(f, 1.0) for f in fields])
        if total > 0:
            norm_weights = {f: weights.get(f, 1.0) / total for f in fields}
        else:
            norm_weights = {f: 1.0 / len(fields) for f in fields}
    else:
        norm_weights = {f: 1.0 / len(fields) for f in fields}
    results = []
    for cid in candidate_ids_set:
        scores = {}
        metas = {}
        for field in fields:
            sim, meta = field_results[field].get(cid, (0.0, {}))
            scores[field] = sim
            metas[field] = meta
        # 加权融合
        weighted_score = 0.0
        for field in fields:
            w = norm_weights[field]
            weighted_score += scores[field] * w
        # 只保留加权分数大于等于 overall_threshold 的候选
        if overall_threshold is not None and weighted_score < overall_threshold:
            continue
        results.append({
            'id': cid,
            'scores': scores,
            'weighted_score': weighted_score,
            'metadatas': metas
        })
    # 3. 排序并返回 top N
    results.sort(key=lambda x: x['weighted_score'], reverse=True)
    return results[:n_results]

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
    # query_emb = get_embedding_from_llm(query_text)
    # print("\n【向量检索 Top 30】")
    # result = query_candidates(query_emb, n_results=5, similarity_threshold=0.7)
    # for i, (id, meta, dist) in enumerate(zip(result['ids'][0], result['metadatas'][0], result['distances'][0]), 1):
    #     print(f"Top {i} | id: {id} | 距离: {dist:.4f} | 元数据: {meta}")

    # # 2. 元数据搜索：学历是硕士及以上的数据
    # print("\n【元数据检索：学历=硕士及以上】")
    # # 这里假设元数据字段学历为"硕士"或"博士"
    # for degree in ["硕士", "博士"]:
    #     where = {"学历": degree}
    #     result = query_candidates(query_emb, n_results=5, where=where)
    #     for i, (id, meta, dist) in enumerate(zip(result['ids'][0], result['metadatas'][0], result['distances'][0]), 1):
    #         print(f"学历={degree} | Top {i} | id: {id} | 距离: {dist:.4f} | 元数据: {meta}")

    # 3. 多向量加权检索测试
    print("\n【多向量加权检索 Top 10】")
    # 构造每个维度的 embedding
    fields = ["technical_skills", "experience", "projects", "bonus_items"]
    weights = {"technical_skills": 0.5, "experience": 0.4, "projects": 0.3, "bonus_items": 0.05}
    # 这里简单用同一个 query_text 生成所有 embedding，实际可按需分别生成
    query_embeddings = {field: get_embedding_from_llm(query_text) for field in fields}
    overall_threshold = 0.6
    multi_results = multi_vector_query(query_embeddings, fields, n_results=10, overall_threshold=overall_threshold, weights=weights)
    for i, item in enumerate(multi_results, 1):
        print(f"Top {i} | id: {item['id']} | 加权分: {item['weighted_score']:.4f} | 各维度: {item['scores']} | 元数据: {item['metadatas']}")
