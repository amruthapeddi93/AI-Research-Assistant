import streamlit as st
from google import genai
from google.genai import types

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

st.title("🤖 AI Research Assistant")
st.caption("Real-time web search powered by Google Grounding & Gemini.")

query = st.text_input("Enter your research topic:", placeholder="e.g., Impact of Quantum Computing on Cryptography")

if st.button("Start Research", type="primary"):
    if not api_key:
        st.error("Please enter a valid Gemini API Key in the sidebar or Secrets.")
    elif not query.strip():
        st.warning("Please enter a research topic first.")
    else:
        with st.spinner("Searching Google in real-time and generating research report..."):
            try:
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
                You are an expert AI Research Assistant. Research the following topic using real-time Google search: "{query}".

                Structure your report in clean Markdown format with the following sections:
                1. **Executive Summary**: A concise, high-level overview.
                2. **Key Insights & Breakthroughs**: Bullet points detailing critical takeaways.
                3. **Source Analysis & Comparison**: Direct comparison of perspectives and viewpoints.
                4. **Detailed Report**: In-depth analytical breakdown.
                5. **Citations & References**: Direct Markdown links to authoritative sources found.
                """

                # Call Gemini with Google Search tool enabled using the current stable model
                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    ),
                )
                
                report = response.text
                
                # Extract grounding web sources if available
                sources = []
                if response.candidates and response.candidates[0].grounding_metadata:
                    metadata = response.candidates[0].grounding_metadata
                    if hasattr(metadata, "grounding_chunks") and metadata.grounding_chunks:
                        for chunk in metadata.grounding_chunks:
                            if hasattr(chunk, "web") and chunk.web:
                                sources.append({
                                    "title": chunk.web.title or "Web Reference",
                                    "url": chunk.web.uri
                                })

                # UI Display
                tab1, tab2, tab3 = st.tabs(["📊 Research Report", "🔗 Sources Retrieved", "📥 Export"])
                
                with tab1:
                    st.markdown(report)
                    
                with tab2:
                    if sources:
                        st.write(f"**Found {len(sources)} Grounded Web Sources:**")
                        for idx, src in enumerate(sources, 1):
                            st.markdown(f"{idx}. [{src['title']}]({src['url']})")
                    else:
                        st.info("Direct citation links are embedded within the Research Report.")
                            
                with tab3:
                    st.download_button(
                        label="Download Report (.md)",
                        data=report,
                        file_name=f"research_{query[:20].replace(' ', '_')}.md",
                        mime="text/markdown"
                    )

            except Exception as e:
                st.error(f"Error generating research report: {e}")
