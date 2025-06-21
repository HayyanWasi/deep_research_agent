import os
import asyncio
from agents import Agent, Runner, OpenAIChatCompletionsModel, RunConfig
from openai import AsyncOpenAI
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Load Gemini API Key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Configure Gemini
genai.configure(api_key=gemini_api_key)
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client,
)
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True,
)

# Agent instructions
QUERY_AGENT_PROMPT = """
You are a helpful assistant that can generate search queries for research...
"""

class QueryResponse(BaseModel):
    queries: list[str]
    thought: str

query_agent = Agent(
    name="Query Generator Agent",
    instructions=QUERY_AGENT_PROMPT,
    output_type=QueryResponse,
    model=model,
)

# ✅ Clean test function
async def generate_query_test(query: str):
    print("🔍 Input Query:", query)
    result = await Runner.run(query_agent, input=query)
    output: QueryResponse = result.final_output
    print("\n🧠 Thought Process:\n", output.thought)
    print("\n🔎 Generated Queries:")
    for i, q in enumerate(output.queries, 1):
        print(f"{i}. {q}")

# ✅ Entry point
if __name__ == "__main__":
    user_query = input("Enter your query: ")
    asyncio.run(generate_query_test(user_query))
