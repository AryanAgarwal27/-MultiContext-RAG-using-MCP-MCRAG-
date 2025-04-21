from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage
from typing import List, Dict, Any
import json
from fastmcp import FastMCP, mcp
from fastmcp.tools import tool

from .config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE
from .search_tools import SearchTools

@mcp.tool
class MCP:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=MODEL_NAME,
            temperature=TEMPERATURE
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.search_tools = SearchTools()
        self.agent = self._setup_agent()

    async def _setup_agent(self) -> AgentExecutor:
        """Set up the agent with tools and prompt."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a helpful AI assistant with access to multiple search tools.
            Your goal is to provide accurate and helpful information by using the most appropriate search tool for each query.
            - Use tavily_search for general web searches
            - Use firecrawl_search for real-time and recent information
            - Use exa_search for technical and programming-related searches
            Always cite your sources and provide URLs when possible."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        tools = self.search_tools.get_tools()
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            prompt=prompt,
            tools=tools
        )

        return AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=True
        )

    @mcp.tool
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query and return the response."""
        try:
            response = await self.agent.ainvoke({"input": query})
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

    @mcp.tool
    async def save_conversation(self, filename: str = "conversation_history.json"):
        """Save the conversation history to a file."""
        history = self.memory.chat_memory.messages
        with open(filename, 'w') as f:
            json.dump([{"role": msg.type, "content": msg.content} for msg in history], f) 