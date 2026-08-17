import streamlit as st
from duckduckgo_search import DDGS
from google import genai

# Page Setup
st.set_page_config(page_title="AI Research Assistant", layout="wide", page_icon="🤖")

# API Key handling via Streamlit Secrets or manual fallback
api_key = st.secrets.get("GEMINI_API_KEY", None)

with st.sidebar:
    st.header("⚙️ Configuration")
    if not api_key:
        api_key = st.text_input("Gemini API Key", type="password", help="Enter your Gemini API key")
        st.caption("Get a free key from [Google AI Studio](https://aistudio.google.com).")
    else:
        st.success("API Key loaded securely from Secrets.")
    
    st.markdown("---")
    max_sources = st.slider("Max Sources to Search", min_value=3, max_value=8, value=5)

st.title("🤖 AI Research Assistant")
st.caption("Search live sources, synthesize insights, and build structured research reports.")

query = st.text_input("Enter your research topic:", placeholder="e.g., Impact of Quantum Computing on Cryptography")

if st.button("Start Research", type="primary"):
    if not api_key:
        st.error("Please enter a valid Gemini API Key in the sidebar.")
    elif not query.strip():
        st.warning("Please enter a research topic first.")
    else:
        # 1. DuckDuckGo Free Search
        with st.spinner("Searching the web for current sources..."):
            sources = []
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=max_sources))
                    for r in results:
                        sources.append({
                            "title": r.get("title", "No Title"),
                            "url": r.get("href", ""),
                            "content": r.get("body", "")
                        })
            except Exception as e:
                st.error(f"Search retrieval error: {e}")

        if not sources:
            st.warning("No search results found. Try modifying your search keywords.")
        else:
            # 2. Gemini Synthesis
            with st.spinner("Analyzing and drafting research brief..."):
                context_text = "\n\n".join(
                    [f"Source {i+1}: {s['title']} ({s['url']})\nSnippet: {s['content']}" 
                     for i, s in enumerate(sources)]
                )
                
                prompt = f"""
                You are an expert AI Research Assistant. Based on the provided search context, write a comprehensive, well-structured research report on: "{query}".

                SOURCES:
                {context_text}

                Provide your output in clean Markdown with these sections:
                1. **Executive Summary**: A concise high-level overview.
                2. **Key Insights & Findings**: Bullet points detailing critical takeaways.
                3. **Source Analysis & Comparison**: Direct comparison of perspectives from the findings.
                4. **Detailed Report**: In-depth breakdown.
                5. **Citations & References**: Markdown links pointing directly to the source URLs.
                """

                try:
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    report = response.text
                except Exception as e:
                    st.error(f"AI Generation failed: {e}")
                    report = None

            # 3. UI Display
            if report:
                tab1, tab2, tab3 = st.tabs(["📊 Research Report", "🔗 Sources Retrieved", "📥 Export"])
                
                with tab1:
                    st.markdown(report)
                    
                with tab2:
                    st.write(f"**Retrieved {len(sources)} Sources:**")
                    for idx, src in enumerate(sources, 1):
                        with st.expander(f"{idx}. {src.get('title')}"):
                            st.write(f"**Link:** {src.get('url')}")
                            st.write(src.get("content"))
                            
                with tab3:
                    st.download_button(
                        label="Download Report (.md)",
                        data=report,
                        file_name=f"research_{query[:20].replace(' ', '_')}.md",
                        mime="text/markdown"
                    )