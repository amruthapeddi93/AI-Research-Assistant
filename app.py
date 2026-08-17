import streamlit as st
from google import genai

# Page Setup
st.set_page_config(page_title="AI Research Assistant", layout="wide", page_icon="🤖")

# API Key handling
api_key = st.secrets.get("GEMINI_API_KEY", None)

with st.sidebar:
    st.header("⚙️ Configuration")
    if not api_key:
        api_key = st.text_input("Gemini API Key", type="password", help="Enter your free Gemini key")
        st.caption("Get a free key at [Google AI Studio](https://aistudio.google.com).")
    else:
        st.success("API Key loaded securely from Secrets.")

st.title("🤖 AI Research Assistant")
st.caption("AI-powered research and structured report generator.")

query = st.text_input("Enter your research topic:", placeholder="e.g., Quantum Computing breakthroughs")

if st.button("Start Research", type="primary"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar or Secrets.")
    elif not query.strip():
        st.warning("Please enter a research topic.")
    else:
        with st.spinner("Compiling research brief..."):
            client = genai.Client(api_key=api_key)
            
            prompt = f"""
            You are an expert AI Research Assistant. Conduct a detailed research review on: "{query}".

            Structure the response in clean Markdown with these sections:
            1. **Executive Summary**: High-level overview.
            2. **Key Insights & Findings**: Critical breakthroughs and data points.
            3. **Comparative Analysis**: Competing methodologies, frameworks, or models.
            4. **Detailed Technical Breakdown**: In-depth analysis of architectures and use cases.
            5. **Authoritative Literature & References**: Key papers, organizations, or standards.
            """

            # Fallback list of free-tier models in order of quota size
            models_to_try = [
                "gemini-3.1-flash-lite",
                "gemini-3.5-flash-lite",
                "gemini-3.7-flash"
            ]
            
            report = None
            last_error = None
            
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    report = response.text
                    break  # Success, exit loop
                except Exception as e:
                    last_error = e
                    continue

            if report:
                tab1, tab2 = st.tabs(["📊 Research Report", "📥 Export"])
                with tab1:
                    st.markdown(report)
                with tab2:
                    st.download_button(
                        label="Download Report (.md)",
                        data=report,
                        file_name=f"research_{query[:20].replace(' ', '_')}.md",
                        mime="text/markdown"
                    )
            else:
                st.error(f"Generation failed across all model endpoints: {last_error}")
