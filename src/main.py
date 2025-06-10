from agent.agent_controller import HuntingAgent

if __name__ == "__main__":
    agent = HuntingAgent()
    # 这里示例传入 JD 文本文件路径或直接文本
    agent.run_from_jd("path/to/jd.txt")
