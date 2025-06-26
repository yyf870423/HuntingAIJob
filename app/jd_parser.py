from app.llm import call_gpt
import os

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompt", "jd_parser_prompt.txt")

def parse_jd(jd_text):
    """调用 LLM 对 JD 进行结构化解析，返回结构化字段。"""
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        system_prompt = f.read()
    full_prompt = f"{system_prompt}\n\nJD:\n{jd_text.strip()}"
    result = call_gpt(full_prompt)
    return result

if __name__ == "__main__":
    jd_text = '''
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
    result = parse_jd(jd_text)
    print(result) 