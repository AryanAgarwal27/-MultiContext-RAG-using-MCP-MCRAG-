from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import format_tool_to_openai_function
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import json

# Load environment variables
load_dotenv()

class MCPImplementation:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.tools = self._setup_tools()
        self.agent = self._setup_agent()

    def _setup_tools(self) -> List[Tool]:
        # Define your tools here
        tools = [
            Tool(
                name="search",
                func=lambda x: "Search results for: " + x,
                description="Useful for searching information"
            ),
            # Add more tools as needed
        ]
        return tools

    def _setup_agent(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are a helpful AI assistant."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        functions = [format_tool_to_openai_function(t) for t in self.tools]
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            prompt=prompt,
            tools=self.tools
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )

    def process_query(self, query: str) -> Dict[str, Any]:
        try:
            response = self.agent.invoke({"input": query})
            return {
                "status": "success",
                "response": response["output"],
                "error": None
            }
        except Exception as e:
            return {
                "status": "error",
                "response": None,
                "error": str(e)
            }

    def save_conversation(self, filename: str = "conversation_history.json"):
        history = self.memory.chat_memory.messages
        with open(filename, 'w') as f:
            json.dump([{"role": msg.type, "content": msg.content} for msg in history], f) 