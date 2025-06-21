import os
import asyncio
from pydantic import BaseModel
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool
from openai import AsyncOpenAI
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=gemini_api_key)

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta"
)

model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",
    openai_client=external_client
)

class SummarizeInput(BaseModel):
    title: str
    content: str

class SummarizeOutput(BaseModel):
    summary: str

async def summarize_web_core(data: SummarizeInput) -> SummarizeOutput:
    prompt = f"""
You are a highly skilled research summarization agent.

Your task is to generate a clear, accurate, and professional summary of the article based on the title and full content provided. Follow these strict guidelines:

1. **Content Selection**
   - Focus on the most important, relevant, and informative points.
   - Exclude filler, repetition, and off-topic sections.
   - Maintain alignment with the title and overall purpose of the article.

2. **Structure & Format**
   - Use bullet points if the content lists facts, arguments, or steps.
   - Use a short paragraph (max 3–5 sentences) if the content is narrative or conceptual.
   - Do not include introductory or concluding phrases like "In summary" or "This article talks about".

3. **Language & Tone**
   - Make it understandable for a non-expert audience (no jargon or technical complexity).
   - Keep the tone neutral, formal, and objective.
   - Avoid speculation or hallucination — only summarize what is present in the content.

4. **Length**
   - Target ~10–20% of the original content’s length.
   - Be concise without losing essential information.

Input:
Title: {data.title}

Content:
\"\"\"
{data.content}
\"\"\"

Respond with only the final summary. Do not include any explanations or extra text.

Summary:
    """
    input_message = [{"role": "user", "content": prompt}]
    
    response = await Runner.run(
        instructions="",  
        model=model,
        input=input_message,
        output_type=SummarizeOutput
    )
    return response.final_output

@function_tool
async def summarize_web(data: SummarizeInput) -> SummarizeOutput:
    return await summarize_web_core(data)

summarizer_agent = Agent(
    name="summarizer-agent",
    instructions="Summarize articles using the summarize_web tool",
    tools=[summarize_web],
    model=model,
    output_type=SummarizeOutput
)

# Test execution
async def main():
    test_input = SummarizeInput(
        title="How AI Agents Transform Research",
        content="""
        AI agents automate repetitive research tasks such as searching, scraping, and summarizing.
        They can break down complex queries, gather data, and organize information efficiently.
        Using agent SDKs, developers can build tools that reduce human effort in knowledge work.
        AI agents can be trained to generate insights, detect patterns, and summarize long documents.
        These capabilities are helping researchers, students, and businesses accelerate their workflows.
        """
    )
    
    input_message = [
        {"role": "user", "content": f"Title: {test_input.title}\nContent: {test_input.content}"}
    ]
    
    result = await Runner.run(
        summarizer_agent,
        input=input_message
    )
    
    print("✅ Summary:\n", result.final_output.summary)

if __name__ == "__main__":
    asyncio.run(main())