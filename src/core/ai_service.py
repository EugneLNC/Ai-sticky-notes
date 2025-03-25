# src/core/ai_service.py

"""
ai_service.py
-------------
基于 DeepSeek 的 OpenAI SDK 接口实现任务规划功能，
使用官方示例中可成功运行的方式调用 API。
请确保已安装 openai 库，例如：
    pip install openai
"""

from openai import OpenAI

class AIService:
    def __init__(self, api_key: str = "your api key", 
                 base_url: str = "https://api.deepseek.com", 
                 model: str = "deepseek-chat"):
        # 直接使用官方示例的方式初始化客户端
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def generate_plan(self, tasks: list) -> str:
        """
        根据任务列表调用 DeepSeek API 生成整体规划。
        :param tasks: 任务列表，每个任务为 dict，例如：
                      [{"title": "任务1", "goal_type": "short-term", "task_type": "daily"}, ...]
        :return: AI 生成的规划文本
        """
        # 将任务列表转换为简洁的描述字符串，使用分号分隔
        tasks_str = "; ".join(
            f"{t.get('title', '(无标题)')} ({t.get('goal_type', '')}, {t.get('task_type', '')})"
            for t in tasks
        )
        # 构造对话消息
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": f"请根据以下任务生成一个整体规划，并给出详细建议： {tasks_str}"}
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False
        )
        return response.choices[0].message.content.strip()
