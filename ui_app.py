import streamlit as st
import asyncio
from datetime import datetime
from typing import AsyncGenerator
from main import run_research_pipeline, ResearchOutput, ArticleData
import pandas as pd

# Configure page settings
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
    <style>
    /* Main card styles */
    .summary-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border-left: 4px solid #4f46e5;
        background-color: #0E1117;
    }

    /* Thought process bubble */
    /* Thought process bubble */
    .thought-bubble {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #1f2937; /* Darker background for dark mode */
    border-left: 4px solid #38bdf8;
    margin-bottom: 1.5rem;
    font-style: italic;
    color: #e0f2fe; /* Light blue readable text */
    }


    /* Article elements */
    .article-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #819A91;
        margin-bottom: 0.5rem;
    }
    .source-url {
        font-size: 0.875rem;
        color: #4f46e5;
        margin-bottom: 1rem;
        word-break: break-all;
    }
    .summary-content {
        font-size: 1rem;
        line-height: 1.6;
        color: #EEEFE0;
    }
    .error-message {
        color: #EEEFE0;
        font-weight: 500;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #0E1117;
    }

    /* Stats container */
    .stats-container {
        background-color: #0E1117;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

def display_generated_queries(queries: list[str]):
    if queries:
        st.markdown(f"""
        <div style="padding: 1rem; background-color: #111827; border-left: 4px solid #4f46e5; border-radius: 0.5rem; margin-bottom: 1.5rem;">
            <div style="font-weight:600; color:#4f46e5; margin-bottom:0.5rem;">🔎 Generated Search Queries:</div>
            <ul style="margin:0; padding-left:1.25rem; color:#EEEFE0;">
                {''.join(f'<li>{q}</li>' for q in queries)}
            </ul>
        </div>
        """, unsafe_allow_html=True)


def display_thought_process(thought: str):
    """Display the agent's thought process in a styled bubble"""
    if thought:
        st.markdown(f"""
        <div class="thought-bubble">
            <div style="font-weight:500;color:#0369a1;margin-bottom:0.5rem;">🤖 Agent's Thought Process:</div>
            <div>{thought}</div>
        </div>
        """, unsafe_allow_html=True)

def display_article_card(article: ArticleData, index: int):
    """Display individual article card with summary and metadata"""
    with st.container():
        card = st.markdown(f"""
        <div class="summary-card">
            <div class="article-title">📄 Article {index}: {article.title}</div>
            <div class="source-url">🌐 Source: <a href="{article.url}" target="_blank">{article.url}</a></div>
            {f'<div class="summary-content">{article.summary}</div>' if article.summary else f'<div class="error-message">❌ {article.error}</div>'}
        </div>
        """, unsafe_allow_html=True)
    return card

async def display_results_stream(generator: AsyncGenerator[ResearchOutput, None]):
    """Display streaming results from the research pipeline"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    thought_container = st.empty()
    results_container = st.empty()
    stats_container = st.empty()

    all_articles = []
    current_thought = ""
    shown_thought_and_queries = False  
    start_time = datetime.now()

    async for update in generator:
        
        progress = (
            (update.successful_articles + update.failed_articles) / update.total_articles * 100
            if update.total_articles > 0 else 0
        )
        progress_bar.progress(int(progress))

        
        if not shown_thought_and_queries and update.thought:
            with thought_container.container():
                display_thought_process(update.thought)
                if update.queries:
                    st.markdown("#### 🧠 Generated Search Queries")
                    for i, q in enumerate(update.queries, 1):
                        st.markdown(f" {i}-{q}")
            shown_thought_and_queries = True  

        
        status_text.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <div style="font-size: 1rem; color: #6b7280;">Status</div>
            <div style="font-size: 1.25rem; font-weight: 600; color: #111827;">{update.status}</div>
        </div>
        """, unsafe_allow_html=True)

        
        with results_container.container():
            if update.articles:
                st.subheader("📄 Research Findings", anchor=False)
                for idx, article in enumerate(update.articles, 1):
                    display_article_card(article, idx)

        
        duration = (datetime.now() - start_time).total_seconds()
        with stats_container.container():
            st.markdown(f"""
            <div class="stats-container">
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                    <div>
                        <div style="font-size: 0.875rem; color: #6b7280;">Total Articles</div>
                        <div style="font-size: 1.25rem; font-weight: 600;">{update.total_articles}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.875rem; color: #6b7280;">Successful</div>
                        <div style="font-size: 1.25rem; font-weight: 600; color: #10b981;">{update.successful_articles}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.875rem; color: #6b7280;">Failed</div>
                        <div style="font-size: 1.25rem; font-weight: 600; color: #ef4444;">{update.failed_articles}</div>
                    </div>
                </div>
                <div style="margin-top: 1rem; font-size: 0.875rem; color: #6b7280;">
                    Processing time: {duration:.1f} seconds
                </div>
            </div>
            """, unsafe_allow_html=True)

        all_articles = update.articles

    return all_articles

def main():
    """Main Streamlit application"""
    st.title("🔍 AI Research Agent")
    st.markdown("Automatically research any topic and get summarized results from multiple web sources.")

    # Sidebar controls
    with st.sidebar:
        st.header("Research Settings")
        max_articles = st.slider("Maximum articles to process", 3, 10, 5)
        st.markdown("---")
        st.markdown("**How it works:**")
        st.markdown("1. Enter your research question")
        st.markdown("2. The AI generates search queries")
        st.markdown("3. Web pages are scraped and summarized")
        st.markdown("4. Results appear in real-time")

    # Main input form
    with st.form("research_form"):
        query = st.text_input(
            "Research topic",
            placeholder="e.g., 'Latest advancements in quantum computing'",
            help="Be specific for better results"
        )
        submitted = st.form_submit_button("Start Research")

    if submitted and query:
        st.session_state.research_started = True
        with st.spinner("Initializing research agent..."):
            try:
                # Run the research pipeline
                generator = run_research_pipeline(query)

                # Display streaming results
                final_results = asyncio.run(display_results_stream(generator))

                # Show completion message
                st.success("Research completed successfully!")

                # Add export options
                st.download_button(
                    label="📥 Export as CSV",
                    data=pd.DataFrame([r.dict() for r in final_results]).to_csv(index=False),
                    file_name=f"research_results_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    elif submitted and not query:
        st.warning("Please enter a research topic")

if __name__ == "__main__":
    main()
