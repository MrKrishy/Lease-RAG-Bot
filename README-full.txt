# 📄 Lease Document Q&A Web Application

A web interface for asking questions about lease documents using AI-powered Retrieval-Augmented Generation (RAG).

## ✨ Features
- **Modern Web UI** – Responsive design served by Flask  
- **Smart Document Search** – Semantic question answering over PDFs  
- **Token Tracking** – Monitor OpenAI API usage  
- **Persistent Embeddings** – Reuse indexed documents without reprocessing  
- **Sensitive Data Protection** – PII detection and masking  
- **Fast Performance** – Optimized chunking and search  

---

## ⚡ Quick Start
```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/Lease-RAG-Bot.git
cd Lease-RAG-Bot

# 2. (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your OpenAI API key
echo "sk-xxxx" > openai.txt

# 5. Place lease documents in:
Lease Contracts/

# 6. Verify setup
python test_setup.py

# 7. Run the app
python run.py
```

Open your browser and go to **http://localhost:5001**.

---

## 📂 Project Structure
```
.
├── app.py                     # Main Flask application
├── run.py                     # Launcher (checks deps, runs app.py)
├── change_port.py              # Utility to modify server port
├── sensitive_data_protection.py# PII masking logic
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Web interface
├── Lease Contracts/            # Your PDF documents
└── test_setup.py               # Setup checks
```

---

## 🔑 Configuration
- **OpenAI API Key**: place in `openai.txt` (one line only).  
- **Documents**: add PDFs to `Lease Contracts/`.  
- **Default Port**: 5001. Change with `change_port.py` or edit `app.py`.  

---


---

## Example Questions
- “What is the lease term for [document]?”  
- “What is the monthly rent amount?”  
- “What are the tenant responsibilities?”  
- “What is the pet policy?”  

Sensitive data requests (SSN, phone, bank details) are blocked.

---

## 🔧 Troubleshooting
- **Missing dependencies** → `pip install -r requirements.txt`  
- **API key errors** → check `openai.txt` contains only your key  
- **No PDFs found** → ensure documents are in `Lease Contracts/`  
- **Port conflict** → update port in `app.py` or with `change_port.py`  

---

## 🔒 Security Notes
- Designed for local use.  
- Do not commit `openai.txt` or sensitive lease files to GitHub.  
- For production: add authentication and HTTPS.  

---

## 📝 License
This project is for educational and personal use. Please respect OpenAI’s usage policies.
