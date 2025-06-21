# import os
# import aiohttp
# from dotenv import load_dotenv
# from agents import function_tool

# load_dotenv()

# API_KEY = os.getenv("WEBSEARCH_API_KEY")
# CX_ID = os.getenv("CX_ID")

# @function_tool
# async def search_web(query: str) -> dict:
#     params = {
#         "key": API_KEY,
#         "cx": CX_ID,
#         "q": query,
#         "num": 5
#     }

#     async with aiohttp.ClientSession() as session:
#         async with session.get("https://www.googleapis.com/customsearch/v1", params=params) as response:
#             if response.status != 200:
#                 return {"items": [], "error": await response.text()}
#             return await response.json()

# if __name__ == "__main__":
#     import asyncio

#     async def test_search():
#         query = input("🔍 Enter search query: ")
#         print(f"\n🌐 Searching for: {query}...\n")

#         try:
#             result = await search_web(query)

#             if "items" in result and result["items"]:
#                 for i, item in enumerate(result["items"], 1):
#                     print(f"{i}. {item.get('title')}")
#                     print(f"   {item.get('link')}\n")
#             else:
#                 print("⚠️ No results found or malformed response.")

#         except Exception as e:
#             print("❌ Error during search:", e)

#     asyncio.run(test_search())

# tools/search_tool.py
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEBSEARCH_API_KEY_2")
CX_ID = os.getenv("CX_ID_2")

async def search_web(query: str) -> dict:
    params = {
        "key": API_KEY,
        "cx": CX_ID,
        "q": query,
        "num": 5
    }

    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.googleapis.com/customsearch/v1", params=params) as response:
            if response.status != 200:
                return {"items": [], "error": await response.text()}
            return await response.json()
