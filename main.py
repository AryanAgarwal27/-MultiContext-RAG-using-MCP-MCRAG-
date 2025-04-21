import os
import sys
import asyncio
import traceback
from typing import List, Tuple
import logging
import requests
from langchain.schema import Document
from langchain.vectorstores import FAISS
from langchain.embeddings import MistralAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from firecrawl import FireCrawlLoader  # Assuming this comes from the Firecrawl SDK
from exa import Exa  # Assuming this is the Exa API SDK

# ENV setup (ensure these are set in .env or your shell)
EXA_API_KEY = os.getenv("EXA_API_KEY", "")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
os.environ["FIRECRAWL_API_KEY"] = FIRECRAWL_API_KEY

# Exa Client
exa = Exa(EXA_API_KEY)

# Constants
MAX_RETRIES = 3
FIRECRAWL_TIMEOUT = 15.0

# Web search config
websearch_config = {
    "parameters": {
        "default_num_results": 5,
        "include_domains": []
    }
}

# ===================
# 🔍 SEARCH
# ===================

def format_search_results(search_results):
    if not search_results.results:
        return "No results found"

    markdown_results = "### Search Results:\n\n"
    for idx, result in enumerate(search_results.results, 1):
        title = result.title if hasattr(result, 'title') and result.title else "No title"
        url = result.url
        published_date = f" (Published: {result.published_date})" if hasattr(result, 'published_date') and result.published_date else ""
        markdown_results += f"**{idx}.** [{title}]({url}){published_date}\n"

        if hasattr(result, 'summary') and result.summary:
            markdown_results += f"> **Summary:** {result.summary}\n\n"
        else:
            markdown_results += "\n"

    return markdown_results

async def search_web(query: str, num_results: int = None) -> Tuple[str, list]:
    try:
        search_args = {
            "num_results": num_results or websearch_config["parameters"]["default_num_results"]
        }

        search_results = exa.search_and_contents(
            query,
            summary={"query": "Main points and key takeaways"},
            **search_args
        )
        formatted_results = format_search_results(search_results)
        return formatted_results, search_results.results

    except Exception as e:
        return f"An error occurred while searching with Exa: {e}", []

# ===================
# 🔥 FIRECRAWL
# ===================

async def get_web_content(url: str) -> List[Document]:
    for attempt in range(MAX_RETRIES):
        try:
            loader = FireCrawlLoader(
                url=url,
                mode="scrape"
            )
            document = await asyncio.wait_for(loader.aload(), timeout=FIRECRAWL_TIMEOUT)
            if document and len(document) > 0:
                return document

            print(f"No documents retrieved from {url} (attempt {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(1)
                continue

        except requests.exceptions.HTTPError as e:
            if "Website Not Supported" in str(e):
                print(f"Website not supported by FireCrawl: {url}")
                content = f"Content from {url} could not be retrieved: Website not supported by FireCrawl."
                return [Document(page_content=content, metadata={"source": url, "error": "Website not supported"})]
            else:
                print(f"HTTP error retrieving content from {url}: {str(e)} (attempt {attempt + 1}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(1)
                    continue
                raise

        except Exception as e:
            print(f"Error retrieving content from {url}: {str(e)} (attempt {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(1)
                continue
            raise

    return []

# ===================
# 🧠 RAG
# ===================

async def create_rag(links: List[str]) -> FAISS:
    try:
        model_name = os.getenv("MODEL", "your name model")

        embeddings = MistralAIEmbeddings(
            model=model_name,
            chunk_size=64
        )

        documents = []
        tasks = [get_web_content(url) for url in links]
        results = await asyncio.gather(*tasks)
        for result in results:
            documents.extend(result)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=500,
            length_function=len,
            is_separator_regex=False
        )

        split_documents = text_splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)

        return vectorstore

    except Exception as e:
        print(f"Error in create_rag: {str(e)}")
        raise

async def search_rag(query: str, vectorstore: FAISS):
    try:
        return vectorstore.similarity_search(query)
    except Exception as e:
        print(f"Error in search_rag: {str(e)}")
        raise

# ===================
# 🚀 MAIN
# ===================

async def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter search query: ")

    print(f"\n🔍 Searching for: {query}")

    try:
        formatted_results, raw_results = await search_web(query)

        if not raw_results:
            print("❌ No search results found.")
            return

        print(f"✅ Found {len(raw_results)} search results.")

        urls = [result.url for result in raw_results if hasattr(result, 'url')]
        if not urls:
            print("❌ No valid URLs found in search results.")
            return

        print(f"🌐 Processing {len(urls)} URLs...")

        vectorstore = await create_rag(urls)
        rag_results = await search_rag(query, vectorstore)

        print("\n=== 🔎 Search Results ===\n")
        print(formatted_results)

        print("\n=== 🧠 RAG Results ===\n")
        for doc in rag_results:
            print("\n---\n" + doc.page_content)

    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
