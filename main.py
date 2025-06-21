import asyncio
from typing import List, Dict, Optional, AsyncGenerator
from pydantic import BaseModel
from datetime import datetime
from custom_agents.query_agent import query_agent
from custom_agents.summarizer_agent import summarizer_agent, SummarizeInput
from tools.search_tool import search_web
from tools.scrapper_tool import smart_scrape_url
from agents import Runner

# Define output schemas
class ArticleData(BaseModel):
    url: str
    title: str
    content: str
    summary: Optional[str] = None
    error: Optional[str] = None

class ResearchOutput(BaseModel):
    query: str
    articles: List[ArticleData]
    status: str
    total_articles: int
    successful_articles: int
    failed_articles: int
    duration_seconds: float
    thought: Optional[str] = None  # <-- Added
    queries: Optional[List[str]] = None  # <-- Added to pass queries to UI

async def scrape_with_retries(url: str, retries: int = 3, delay: float = 1.5) -> Optional[Dict]:
    for attempt in range(1, retries + 1):
        try:
            result = await asyncio.to_thread(smart_scrape_url, url)
            if result and isinstance(result, dict) and "text" in result and len(result["text"]) > 200:
                print(f"✅ Success: {url}")
                return result
            else:
                print(f"⚠️ Attempt {attempt}: Invalid or short content for {url}")
        except Exception as e:
            print(f"❌ Attempt {attempt} failed for {url}: {e}")
            if attempt < retries:
                await asyncio.sleep(delay)
    print(f"⛔ Giving up on: {url}")
    return None

async def summarize_article(title: str, content: str) -> str:
    try:
        input_data = SummarizeInput(title=title, content=content)
        summary_result = await Runner.run(
            summarizer_agent,
            input=[{"role": "user", "content": f"Title: {title}\nContent: {content}"}]
        )
        return summary_result.final_output.summary
    except Exception as e:
        print(f"⚠️ Summarization failed: {e}")
        return None

async def process_article(url: str) -> ArticleData:
    scraped = await scrape_with_retries(url)
    if not scraped:
        return ArticleData(url=url, title="", content="", error="Failed to scrape")

    try:
        summary = await summarize_article(scraped.get('title', ''), scraped['text'])
        return ArticleData(
            url=url,
            title=scraped.get('title', 'No title'),
            content=scraped['text'],
            summary=summary
        )
    except Exception as e:
        return ArticleData(
            url=url,
            title=scraped.get('title', 'No title'),
            content=scraped['text'],
            error=str(e)
        )

async def run_research_pipeline(user_query: str) -> AsyncGenerator[ResearchOutput, None]:
    start_time = datetime.now()

    print("\n🔍 Step 1: Generating search queries...")
    query_response = await Runner.run(query_agent, input=user_query)
    queries = query_response.final_output.queries
    thought = query_response.final_output.thought

    print("\n🧠 Agent Thought:")
    print(thought)

    yield ResearchOutput(
        query=user_query,
        articles=[],
        status="Generated search queries",
        total_articles=0,
        successful_articles=0,
        failed_articles=0,
        duration_seconds=(datetime.now() - start_time).total_seconds(),
        thought=thought,
        queries=queries
    )

    all_urls = []
    print("\n🌐 Step 2: Performing web search...")
    for q in queries:
        print(f"Query: {q}")  # Print queries for logging
        try:
            result = await search_web(q)
            if result and "items" in result:
                urls = [item["link"] for item in result["items"]]
                all_urls.extend(urls)
        except Exception as e:
            print(f"⚠️ Error during search for '{q}': {e}")

    if not all_urls:
        yield ResearchOutput(
            query=user_query,
            articles=[],
            status="Failed: No URLs found",
            total_articles=0,
            successful_articles=0,
            failed_articles=0,
            duration_seconds=(datetime.now() - start_time).total_seconds(),
            thought=thought,
            queries=queries
        )
        return

    print(f"\n📰 Step 3: Processing {min(5, len(all_urls))} URLs...")
    urls_to_process = all_urls[:5]
    processed_articles = []

    for i, url in enumerate(urls_to_process):
        article = await process_article(url)
        processed_articles.append(article)

        yield ResearchOutput(
            query=user_query,
            articles=processed_articles,
            status=f"Processed {i+1}/{len(urls_to_process)}",
            total_articles=len(urls_to_process),
            successful_articles=sum(1 for a in processed_articles if not a.error),
            failed_articles=sum(1 for a in processed_articles if a.error),
            duration_seconds=(datetime.now() - start_time).total_seconds(),
            thought=thought,
            queries=queries
        )

    yield ResearchOutput(
        query=user_query,
        articles=processed_articles,
        status="Completed",
        total_articles=len(urls_to_process),
        successful_articles=sum(1 for a in processed_articles if not a.error),
        failed_articles=sum(1 for a in processed_articles if a.error),
        duration_seconds=(datetime.now() - start_time).total_seconds(),
        thought=thought,
        queries=queries
    )




async def stream_output(output: ResearchOutput):
    """Helper function to stream output in chunks"""
    print("\n📝 Research Results:")
    print(f"🔍 Original Query: {output.query}")
    print(f"📊 Found {len(output.articles)} articles")

    for idx, article in enumerate(output.articles, 1):
        print(f"\n🔹 Article {idx}: {article.title}")
        print(f"🌐 URL: {article.url}")
        if article.error:
            print(f"❌ Error: {article.error}")
        else:
            print("\n📌 Summary:")
            print(article.summary)
            print("\n---")

if __name__ == "__main__":
    user_input = input("\n🔎 Enter your research topic: ")

    async def main():
        async for result in run_research_pipeline(user_input):
            await stream_output(result)

    asyncio.run(main())