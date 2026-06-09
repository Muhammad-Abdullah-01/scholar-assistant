import streamlit as st
import requests

# -----------------------
# 🎨 Page Config
# -----------------------
st.set_page_config(page_title="📄 ScholarAssistant", layout="wide")
st.title("📄 ScholarAssistant")

# -----------------------
# 🧭 Sidebar Navigation
# -----------------------
app_mode = st.sidebar.radio("Choose Feature:", ["Chat with PDF", "Citation Recommender", "Semantic Search"])

# -----------------------
# 1️⃣ Chat with PDF
# -----------------------
if app_mode == "Chat with PDF":
    # --- Session States ---
    for key in ["pdf_text", "pdf_summary", "conversation_history", "uploaded_filename"]:
        if key not in st.session_state:
            st.session_state[key] = "" if "text" in key or key == "uploaded_filename" else []

    # --- Upload PDF ---
    st.sidebar.header("📤 Upload PDF")
    uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type="pdf")

    if uploaded_file:
        if uploaded_file.name != st.session_state.uploaded_filename:
            st.session_state.pdf_text = ""
            st.session_state.pdf_summary = ""
            st.session_state.conversation_history = []
            st.session_state.uploaded_filename = uploaded_file.name

            files = {"files": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            with st.spinner("📚 Extracting and summarizing your PDF..."):
                response = requests.post("http://127.0.0.1:8000/pdf/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.pdf_text = data["pdf_texts"][0]
                st.session_state.pdf_summary = data["summaries"][0]
                st.sidebar.success(f"✅ '{uploaded_file.name}' uploaded successfully!")
            else:
                st.sidebar.error("❌ Error uploading the PDF.")

    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.conversation_history = []
        st.sidebar.info("Chat history cleared.")

    # --- PDF Summary ---
    if st.session_state.pdf_summary:
        st.subheader("📝 PDF Summary")
        st.info(st.session_state.pdf_summary)

    # --- Chat Interface ---
    st.subheader("💬 Chat with Your PDF")
    for chat in st.session_state.conversation_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    question = st.chat_input("Ask a question about the uploaded PDF...")
    if question:
        if not st.session_state.pdf_text:
            st.warning("Please upload a PDF first.")
        else:
            st.chat_message("user").markdown(question)
            st.session_state.conversation_history.append({"role": "user", "content": question})

            payload = {
                "pdf_texts": [st.session_state.pdf_text],
                "question": question,
                "conversation_history": "\n".join(
                    [f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.conversation_history]
                ),
            }
            with st.spinner("🤔 Thinking..."):
                response = requests.post("http://127.0.0.1:8000/pdf/question", json=payload)
            if response.status_code == 200:
                answer = response.json()["answer"]
                with st.chat_message("assistant"):
                    st.markdown(answer)
                st.session_state.conversation_history.append({"role": "assistant", "content": answer})
            else:
                st.error(f"❌ Error generating answer: {response.text}")

# -----------------------
# 2️⃣ Citation Recommender
# -----------------------
elif app_mode == "Citation Recommender":
    # --- Session States ---
    for key in ["citation_results", "search_query", "text_input", "sources_used"]:
        if key not in st.session_state:
            st.session_state[key] = [] if key in ["citation_results", "sources_used"] else ""

    st.subheader("📚 Citation Recommender")
    st.markdown("Find relevant citations from **arXiv** and **Semantic Scholar** based on semantic similarity.")

    # --- Input Form ---
    with st.form("citation_form", clear_on_submit=False):
        st.session_state.text_input = st.text_area(
            "Paste your paragraph or abstract here:", 
            height=200, 
            value=st.session_state.text_input
        )
        
        # Source selection options
        col1, col2, col3 = st.columns(3)
        with col1:
            use_arxiv = st.checkbox("Search arXiv", value=True)
        with col2:
            use_semantic_scholar = st.checkbox("Search Semantic Scholar", value=True)
        with col3:
            use_sbert = st.checkbox("Use Sentence-BERT (faster)", value=True)
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            max_results = st.number_input("Max results per source", min_value=3, max_value=20, value=5)
            top_k = st.number_input("Top K results", min_value=5, max_value=30, value=10)
        
        submitted = st.form_submit_button("🔍 Find Relevant Citations")

    # --- API Call ---
    if submitted:
        if not st.session_state.text_input.strip():
            st.warning("Please enter some text!")
        elif not use_arxiv and not use_semantic_scholar:
            st.warning("Please select at least one source (arXiv or Semantic Scholar)!")
        else:
            with st.spinner("🔍 Generating queries and searching arXiv & Semantic Scholar..."):
                try:
                    API_URL = "http://localhost:8000/citation_router/recommend"
                    payload = {
                        "text": st.session_state.text_input,
                        "use_arxiv": use_arxiv,
                        "use_semantic_scholar": use_semantic_scholar,
                        "max_results_per_source": max_results,
                        "top_k": top_k,
                        "use_sbert": use_sbert
                    }
                    response = requests.post(API_URL, json=payload)
                    response.raise_for_status()
                    data = response.json()

                    st.session_state.search_query = data.get("query", "")
                    st.session_state.citation_results = data.get("results", [])
                    st.session_state.sources_used = data.get("sources_used", [])

                except Exception as e:
                    st.error(f"❌ Error: {e}")

        # --- Display Results ---
    if st.session_state.citation_results:
        # Show sources used
        if hasattr(st.session_state, 'sources_used') and st.session_state.sources_used:
            sources_badges = " | ".join([f"**{source}**" for source in st.session_state.sources_used])
            st.markdown(f"### 📊 Sources: {sources_badges}")
        
        st.markdown("### 🔍 Generated Search Query")
        st.info(st.session_state.search_query)

        st.markdown(f"### 📄 Top {len(st.session_state.citation_results)} Papers")
        for idx, paper in enumerate(st.session_state.citation_results, 1):
            with st.container():
                # Determine source badge
                source = paper.get('source', 'unknown')
                if source == 'arxiv':
                    source_badge = "📚 arXiv"
                elif source == 'semantic_scholar':
                    source_badge = "🎓 Semantic Scholar"
                else:
                    source_badge = "📄 Unknown Source"
                
                # Get venue if available
                venue = paper.get('venue', '')
                venue_text = f" | <strong>Venue:</strong> {venue}" if venue else ""
                
                st.markdown(
                    f"""
                    <div style="border:1px solid #e0e0e0; padding:15px; border-radius:10px; margin-bottom:10px; background-color:#f9f9f9">
                        <h4 style="margin:0; color:#2B7A78;">{idx}. {paper['title']}</h4>
                        <p style="margin:0; font-size:14px; color:#555;"><strong>Authors:</strong> {', '.join(paper['authors']) if paper['authors'] else 'Unknown'}</p>
                        <p style="margin:0; font-size:14px; color:#555;"><strong>Published:</strong> {paper['published']}{venue_text}</p>
                        <p style="margin:0; font-size:14px; color:#555;"><strong>Source:</strong> {source_badge} | <strong>Semantic Score:</strong> {paper['score']:.4f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                # Collapsible Abstract using Streamlit expander
                with st.expander("📖 Abstract"):
                    st.write(paper['summary'])

                # Paper link
                link_text = "🔗 View Paper" if source == 'arxiv' else "🔗 View on Semantic Scholar"
                st.markdown(f"[{link_text}]({paper['link']})")

                # BibTeX download
                # Determine journal based on source
                journal = "arXiv" if source == 'arxiv' else (venue if venue else "Semantic Scholar")
                bibtex = f"""@article{{{paper.get('paperId', 'paper').replace('-', '') if paper.get('paperId') else 'paper'}{idx},
    title={{ {paper['title']} }},
    author={{ {', '.join(paper['authors']) if paper['authors'] else 'Unknown'} }},
    journal={{ {journal} }},
    year={{ {paper['published'][:4] if len(paper['published']) >= 4 else 'Unknown'} }},
    url={{ {paper['link']} }}
}}"""
                st.download_button(
                    label="📥 Download BibTeX",
                    data=bibtex,
                    file_name=f"{paper['title'][:50].replace(' ', '_')}.bib",
                    mime="text/plain",
                    key=f"bib_{paper.get('paperId', idx)}_{hash(paper['title'])}"
                )
                st.markdown("---")

# -----------------------
# 3️⃣ Semantic Search
# -----------------------
elif app_mode == "Semantic Search":
    # --- Session States ---
    for key in ["semantic_results", "pipeline_results", "search_query", "semantic_input"]:
        if key not in st.session_state:
            st.session_state[key] = [] if "results" in key else ""
    
    st.subheader("🔍 Semantic Search")
    st.markdown("Search across arXiv and Semantic Scholar using semantic similarity.")
    
    # --- Tabs for Search vs Pipeline ---
    search_tab, pipeline_tab = st.tabs(["🔎 Search Only", "🔄 Full Pipeline"])
    
    # --- Search Only Tab ---
    with search_tab:
        with st.form("semantic_search_form", clear_on_submit=False):
            st.session_state.semantic_input = st.text_input(
                "Enter your search query:",
                value=st.session_state.semantic_input,
                placeholder="e.g., transformer architectures in natural language processing"
            )
            col1, col2 = st.columns(2)
            with col1:
                max_results = st.number_input("Max results per source", min_value=5, max_value=50, value=10)
            with col2:
                top_k = st.number_input("Top K results", min_value=5, max_value=50, value=20)
            
            submitted_search = st.form_submit_button("🔍 Search")
        
        if submitted_search:
            if not st.session_state.semantic_input.strip():
                st.warning("Please enter a search query!")
            else:
                with st.spinner("🔍 Searching arXiv and Semantic Scholar..."):
                    try:
                        API_URL = "http://localhost:8000/semantic/search"
                        payload = {
                            "query": st.session_state.semantic_input,
                            "max_results_per_source": max_results,
                            "top_k": top_k,
                            "use_sbert": True
                        }
                        response = requests.post(API_URL, json=payload)
                        response.raise_for_status()
                        data = response.json()
                        
                        st.session_state.search_query = data["query"]
                        st.session_state.semantic_results = data["results"]
                        
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        
        # Display search results
        if st.session_state.semantic_results:
            st.markdown(f"### 📊 Found {len(st.session_state.semantic_results)} papers")
            
            for idx, paper in enumerate(st.session_state.semantic_results, 1):
                with st.container():
                    source_badge = "📚 arXiv" if paper.get("source") == "arxiv" else "🎓 Semantic Scholar"
                    st.markdown(
                        f"""
                        <div style="border:1px solid #e0e0e0; padding:15px; border-radius:10px; margin-bottom:10px; background-color:#f9f9f9">
                            <h4 style="margin:0; color:#2B7A78;">{idx}. {paper['title']}</h4>
                            <p style="margin:0; font-size:14px; color:#555;"><strong>Authors:</strong> {', '.join(paper['authors'])}</p>
                            <p style="margin:0; font-size:14px; color:#555;"><strong>Published:</strong> {paper['published']} | <strong>Source:</strong> {source_badge}</p>
                            <p style="margin:0; font-size:14px; color:#555;"><strong>Semantic Score:</strong> {paper['score']:.4f}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    with st.expander("📖 Abstract"):
                        st.write(paper['summary'])
                    st.markdown(f"[🔗 View Paper]({paper['link']})")
                    st.markdown("---")
    
    # --- Full Pipeline Tab ---
    with pipeline_tab:
        st.markdown("**Full Pipeline:** Search → Summarize → Generate Citations")
        
        with st.form("pipeline_form", clear_on_submit=False):
            pipeline_query = st.text_input(
                "Enter your query:",
                placeholder="e.g., recent advances in large language models"
            )
            col1, col2 = st.columns(2)
            with col1:
                pipeline_max_results = st.number_input("Max results per source", min_value=5, max_value=50, value=10, key="pipeline_max")
            with col2:
                pipeline_top_k = st.number_input("Top K results", min_value=5, max_value=20, value=10, key="pipeline_top")
            
            generate_summary = st.checkbox("Generate summary from retrieved papers", value=True)
            generate_citations = st.checkbox("Generate citation recommendations", value=True)
            
            submitted_pipeline = st.form_submit_button("🚀 Run Full Pipeline")
        
        if submitted_pipeline:
            if not pipeline_query.strip():
                st.warning("Please enter a query!")
            else:
                with st.spinner("🔄 Running full pipeline (this may take a moment)..."):
                    try:
                        API_URL = "http://localhost:8000/semantic/pipeline"
                        payload = {
                            "query": pipeline_query,
                            "max_results_per_source": pipeline_max_results,
                            "top_k": pipeline_top_k,
                            "use_sbert": True,
                            "generate_summary": generate_summary,
                            "generate_citations": generate_citations
                        }
                        response = requests.post(API_URL, json=payload)
                        response.raise_for_status()
                        data = response.json()
                        
                        st.session_state.pipeline_results = data
                        
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        
        # Display pipeline results
        if st.session_state.pipeline_results:
            pipeline_data = st.session_state.pipeline_results
            
            # Display summary
            if pipeline_data.get("summary"):
                st.markdown("### 📝 Generated Summary")
                st.info(pipeline_data["summary"])
                st.markdown("---")
            
            # Display retrieved papers
            if pipeline_data.get("retrieved_papers"):
                st.markdown(f"### 📚 Retrieved Papers ({len(pipeline_data['retrieved_papers'])})")
                for idx, paper in enumerate(pipeline_data["retrieved_papers"][:5], 1):  # Show top 5
                    with st.expander(f"{idx}. {paper['title']}"):
                        st.write(f"**Authors:** {', '.join(paper['authors'])}")
                        st.write(f"**Published:** {paper['published']}")
                        st.write(f"**Score:** {paper['score']:.4f}")
                        st.write(f"**Abstract:** {paper['summary'][:300]}...")
                        st.markdown(f"[🔗 View Paper]({paper['link']})")
            
            # Display citations
            if pipeline_data.get("citations"):
                st.markdown("### 📖 Recommended Citations")
                for idx, citation in enumerate(pipeline_data["citations"][:5], 1):  # Show top 5
                    st.markdown(
                        f"""
                        <div style="border-left:4px solid #2B7A78; padding-left:10px; margin-bottom:10px;">
                            <strong>{idx}. {citation['title']}</strong><br>
                            <small>{', '.join(citation['authors'])} ({citation['published']})</small><br>
                            <small>Relevance Score: {citation['score']:.4f}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.markdown(f"[🔗 View]({citation['link']})")
                    st.markdown("---")
