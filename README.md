# 📚 ScholarAssistant

An intelligent, comprehensive academic research assistant platform that combines semantic search, PDF document parsing, interactive chat, summarization, and citation recommendation. ScholarAssistant helps researchers discover, analyze, and cite relevant literature from **arXiv** and **Semantic Scholar** in one unified workflow.

---

## 🌟 Features

### 🔍 Unified Semantic Search
* **Cross-Source Search:** Simutaneously queries arXiv and Semantic Scholar using a single query.
* **Semantic Similarity Ranking:** Embeds and ranks results by relevance using vector cosine similarity.
* **Deduplication:** Automatically matches and deduplicates papers returning from multiple sources.

### 📄 PDF & Document Processing
* **Multi-Format Upload:** Upload and parse both **PDF** and **DOCX** files.
* **Formula Extraction:** Heuristically detects and extracts mathematical equations and formulas.
* **Clean Text Normalization:** Filters out page numbers, headers, footers, and redundant line breaks.
* **Interactive PDF Chat:** Chat directly with your documents while maintaining conversational history context.
* **Automatic Summarization:** Instantly generates structured executive summaries of uploaded documents.

### 📖 Citation Recommender
* **Query Generation:** Automatically refines abstracts or paragraphs into search keywords.
* **Ranked Citations:** Finds matching bibliography entries based on semantic closeness to your text.
* **BibTeX Export:** Generates and exports citations directly in BibTeX format.

### 🔄 End-to-End Pipeline
* **Search → Summarize → Cite:** Runs the entire discovery pipeline in a single API call (`/semantic/pipeline`).
* **Configurable Workflow:** Enables toggling individual pipeline stages as needed.

### 📊 Evaluation Module
* **Retrieval Evaluation:** Benchmarks Precision@k and Recall@k.
* **Summarization Metrics:** Measures ROUGE-1, ROUGE-L, and BLEU scores against ground-truth references.
* **Citation Auditing:** Verifies citation correctness, checking title matching and author overlap.
* **Batch Testing:** Run full evaluations using JSON/JSONL test suites and export results as CSV.

---

## 🛠️ Tech Stack & Tools

* **Frontend:** [Streamlit](https://streamlit.io/) (Interactive web interface with customized HTML components)
* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (High-performance web API framework)
* **LLM Engine:** [Groq Cloud API](https://groq.com/) (Powering `llama-3.1-8b-instant` for ultra-fast summarization & QA)
* **NLP & Embeddings:** [scikit-learn](https://scikit-learn.org/) (Using `HashingVectorizer` for lightweight, dependency-free local vector representation and cosine similarity)
* **Document Parsing:** [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) & [python-docx](https://python-docx.readthedocs.io/)
* **External APIs:** [arXiv API](https://arxiv.org/help/api/index) & [Semantic Scholar API](https://www.semanticscholar.org/product/api)

---

## 📁 Project Structure

```text
ScholarAssistant/
├── Backend/                    # FastAPI Backend Application
│   ├── app/                    # Application Source Code
│   │   ├── api/                # API Router Endpoints
│   │   │   ├── auth_routes.py        # Authentication & status
│   │   │   ├── citation_routes.py    # Citation recommendation router
│   │   │   ├── evaluation_routes.py  # Batch & single query evaluation
│   │   │   ├── pdf_routes.py         # PDF parsing, summary, & QA router
│   │   │   ├── query_routes.py       # Prompt enhancement & text summarization
│   │   │   └── semantic_routes.py    # Unified semantic search & pipelines
│   │   ├── auth/               # JWT & Password Verification Handlers (Placeholders)
│   │   ├── services/           # Backend Business Logic
│   │   │   ├── arxiv_service.py              # arXiv integration
│   │   │   ├── embedding_service.py          # Vector embeddings generation
│   │   │   ├── evaluation_service.py         # Metrics calculations (ROUGE/BLEU)
│   │   │   ├── pdf_service.py                # File text extraction
│   │   │   ├── semantic_retrieval_service.py # Unified search coordinator
│   │   │   ├── semantic_scholar_service.py   # Semantic Scholar integration
│   │   │   └── summarizer_service.py         # Groq LLM integration
│   │   └── utils/              # Utilities & Cleaners
│   │       ├── pdf_parser.py                 # Mathematical formula & layout extraction
│   │       └── text_cleanup.py               # Text cleaning heuristics
│   ├── cache/                  # Pickled Vector Embeddings Cache
│   ├── main.py                 # FastAPI Application Entrypoint
│   └── requirements.txt        # Full project dependencies (Backend + Frontend)
├── Frontend/                   # Streamlit Frontend Web App
│   └── app.py                  # Main Streamlit interface code
├── requirements.txt            # Root database/web requirements (pgvector, SQLAlchemy)
└── .gitignore                  # Git Ignore specifications
```

---

## ⚙️ Environment Configuration

Create a `.env` file in the `Backend/` directory:

```env
# Required for LLM summarization and chat
GROQ_API_KEY=gsk_your_groq_api_key_here

# Optional (highly recommended to avoid Semantic Scholar API rate limits)
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_api_key_here

# Optional (for future OpenAI expansions)
# OPENAI_API_KEY=sk-your_openai_key_here
```

---

## 🚀 Installation & Local Setup

### Prerequisites
* Python 3.8 or higher installed.
* A valid Groq Cloud API Key.

### Step-by-Step Setup

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd ScholarAssistant
   ```

2. **Create and Activate a Virtual Environment:**
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate on Windows:
   venv\Scripts\activate

   # Activate on macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   Install all necessary packages for the frontend web application and backend server:
   ```bash
   pip install -r Backend/requirements.txt
   ```

4. **Set Up the Environment File:**
   Create a `.env` file inside the `Backend/` folder with your credentials as described in the [Environment Configuration](#️-environment-configuration) section.

5. **Run the Backend API Server:**
   ```bash
   cd Backend
   uvicorn main:app --reload
   ```
   * The server runs on `http://localhost:8000`.
   * Interactive API documentation is available at `http://localhost:8000/docs` (Swagger UI).

6. **Run the Streamlit Frontend Web Interface:**
   Open a separate terminal window, activate the virtual environment, and run:
   ```bash
   cd Frontend
   streamlit run app.py
   ```
   * The web application will launch in your browser at `http://localhost:8501`.

---

## 📡 API Endpoints

The backend exposes the following primary REST endpoints:

### PDF Operations (`/pdf`)
* **`POST /pdf/upload`** (Multipart/Form-Data): Uploads files (`.pdf` or `.docx`), extracts clean text/formulas, and returns summaries and extracted text.
* **`POST /pdf/question`** (JSON): Answers questions regarding the uploaded text with conversation history context.

### Citation Operations (`/citation_router`)
* **`POST /citation_router/recommend`** (JSON): Recommends relevant citations from arXiv and Semantic Scholar based on input text, and returns generated queries, citation lists, and scores.

### Semantic Search Operations (`/semantic`)
* **`POST /semantic/search`** (JSON): Performs joint queries to arXiv and Semantic Scholar and ranks results by vector similarity.
* **`POST /semantic/pipeline`** (JSON): Runs an end-to-end flow. Searches relevant papers, summarizes them, and compiles recommended citations in a single payload.

### General Queries (`/queries`)
* **`GET /queries/summarize`** (Query Params): Summarizes a raw text string.
* **`POST /queries/enhance_prompt`** (Query Params): Expands a user prompt to improve performance in downstream LLM requests.

### Performance Evaluation (`/evaluation`)
* **`POST /evaluation/evaluate`** (JSON): Evaluates a single system query's metrics (Precision@K, Recall@K, ROUGE, BLEU, and citation coverage).
* **`POST /evaluation/evaluate-batch`** (Multipart/Form-Data): Benchmarks a test file (JSON/JSONL) and exports results to a CSV report under `Backend/evaluation_results/`.

---

## 📸 Screenshots

*(Place screenshots and GIFs demonstrating application features here)*

| Feature 1: PDF Chat | Feature 2: Citation Recommendation |
| :---: | :---: |
| ![PDF Chat Placeholder](https://via.placeholder.com/400x250?text=Chat+With+PDF+UI) | ![Citation Recommender Placeholder](https://via.placeholder.com/400x250?text=Citation+Recommender+UI) |

---

## ⚠️ Known Limitations & Future Roadmap

* **Hashing-Based Embeddings:** To maintain speed and run locally without specialized GPU/PyTorch setups, the active search module utilizes scikit-learn's `HashingVectorizer` (1024-dimensional sparse hashing representations) for matching. Integrating dense neural embeddings (e.g. `sentence-transformers` or OpenAI's `text-embedding-3-large`) would improve retrieval precision for complex semantic abstractions.
* **Vector Databases:** The system currently ranks papers in-memory for each query. In-production environments can scale queries by storing pre-computed paper embeddings in a vector database like **pgvector** or **FAISS** (which are currently listed in dependencies but not integrated into the active query path).
* **OCR support:** Document text extraction is limited to selectable text. PDFs containing images or scanned pages require OCR integrations (e.g., Tesseract).
* **API Rate Limits:** Free searches depend heavily on Semantic Scholar and arXiv public API rates. A distributed caching layer or dedicated enterprise keys is recommended for large-scale operations.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
