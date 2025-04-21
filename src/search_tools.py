from typing import List, Dict, Any
from fastmcp import mcp
from fastmcp.tools import tool
from tavily import TavilyClient
from firecrawl import FirecrawlClient
from exa import ExaClient

class SearchTools:
    def __init__(self):
        self.tavily_client = TavilyClient()
        self.firecrawl_client = FirecrawlClient()
        self.exa_client = ExaClient()

    @mcp.tool
    async def tavily_search(self, query: str) -> Dict[str, Any]:
        """Search the web using Tavily API."""
        try:
            results = await self.tavily_client.search(query)
            return {
                "status": "success",
                "results": results,
                "error": None
            }
        except Exception as e:
            return {
                "status": "error",
                "results": None,
                "error": str(e)
            }

    @mcp.tool
    async def firecrawl_search(self, query: str) -> Dict[str, Any]:
        """Search the web using Firecrawl API for real-time information."""
        try:
            results = await self.firecrawl_client.search(query)
            return {
                "status": "success",
                "results": results,
                "error": None
            }
        except Exception as e:
            return {
                "status": "error",
                "results": None,
                "error": str(e)
            }

    @mcp.tool
    async def exa_search(self, query: str) -> Dict[str, Any]:
        """Search using Exa API for technical and programming information."""
        try:
            results = await self.exa_client.search(query)
            return {
                "status": "success",
                "results": results,
                "error": None
            }
        except Exception as e:
            return {
                "status": "error",
                "results": None,
                "error": str(e)
            }

    def get_tools(self) -> List[Any]:
        """Return all available search tools."""
        return [
            self.tavily_search,
            self.firecrawl_search,
            self.exa_search
        ] 