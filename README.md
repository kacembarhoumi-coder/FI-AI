# FI-AI: Finance Education Chatbot

FI-AI is a robust, hallucination-free educational platform designed to teach financial concepts securely and accurately. At its core, the project leverages a **Retrieval-Augmented Generation (RAG)** architecture to provide users with reliable, cited explanations of complex financial topics without offering unauthorized financial advice.

##  Key Features
* **Strictly Educational, Zero Hallucination Focus:** Utilizes advanced prompting techniques (including few-shot examples) and strict system rules. The LLM is constrained to answer *only* using the provided context. If the system doesn't know the answer based on the loaded documents, it will safely admit it.
* **Intelligent Document Retrieval:** Ingests textual financial data via custom scrapers and PDF parsers, converting it into dense vector representations.
* **Fast and Efficient Vector Storage:** Uses FAISS (Facebook AI Similarity Search) to store document embeddings, allowing instant retrieval of the most relevant chunks.
* **Locally Hosted LLM:** Integrates with Ollama (utilizing the `qwen2:7b-instruct` model) via LangChain, ensuring data privacy and offline capability.
* **Beginner-Friendly Design:** Tuned to break down financial jargon into simple terms that a beginner can easily digest, automatically citing source documents.

## 🛠️ Technology Stack
* **Language:** Python
* **Framework:** LangChain (Orchestration, Prompting, Retrieval)
* **Vector Database:** FAISS
* **Embeddings:** HuggingFace `sentence-transformers/all-MiniLM-L6-v2`
* **LLM:** Ollama (`qwen2:7b-instruct`)
* **Document Processing:** PyMuPDF (`fitz`) for PDFs, BeautifulSoup4 for web scraping

## 📁 Project Structure
```
finance/
├── scripts/
│   ├── faiss_embedding.py      # Main script to build vectorstore and run the chatbot
│   ├── faiss_persist.py        # Handles loading and saving the FAISS index
│   ├── ingest_faiss.py         # Utilities to find, load, and chunk text documents
│   ├── prompting.py            # Chat templates, system rules, and few-shot examples
│   ├── scraper.py              # General web scraping utilities
│   ├── investopia_scraper.py   # Specialized scraper for financial terms
│   └── pdf_parser.py           # Extracts and cleans text from PDF documents
├── data/                       # Directory for raw and cleaned datasets
├── db/faiss/                   # Local storage for the persisted FAISS vector database
└── requirements.txt            # Python dependencies
```

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kacembarhoumi-coder/FI-AI.git
   cd FI-AI
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install and run Ollama:**
   - Download and install [Ollama](https://ollama.com/).
   - Pull the required model:
     ```bash
     ollama run qwen2:7b-instruct
     ```

## 💻 Usage

1. **Populate your data directory:** Add financial `.txt` or `.pdf` files into the `data/` directory. Alternatively, use the included scrapers to gather data.
2. **Run the chatbot:**
   ```bash
   python scripts/faiss_embedding.py
   ```
3. The system will ingest the documents, build (or load) the FAISS index, and open an interactive chat prompt. Type your finance-related questions!

## ⚠️ Disclaimer
FI-AI is an educational tool. It is intentionally designed and prompted to avoid giving financial advice. Always consult a certified financial advisor before making any investment decisions.
