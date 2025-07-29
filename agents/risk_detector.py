# agents/risk_detector.py

from langchain.memory import ConversationBufferMemory
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class RiskDetectorAgent:
    def __init__(self, llm: BaseChatModel, memory: ConversationBufferMemory):
        self.llm = llm
        self.memory = memory

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Risk Detection Agent."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        self.chain = self.prompt | self.llm

    def run(self, prompt: str) -> str:
        inputs = {"input": prompt, "chat_history": self.memory.chat_memory.messages}
        response = self.chain.invoke(inputs)
        return response.content if hasattr(response, "content") else str(response)
