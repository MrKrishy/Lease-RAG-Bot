# 📄 Lease Document Q&A

Flask web app powered by Retrieval-Augmented Generation (RAG) for answering questions about lease contracts.

---

## ⚡ Quick Start
```bash
# Clone repo
git clone https://github.com/MrKrishy/Lease-RAG-Bot.git
cd Lease-RAG-Bot

# Install deps
pip install -r requirements.txt

# Add your OpenAI key
echo "sk-xxxx" > openai.txt

# Place your PDFs
mkdir -p "Lease Contracts"
cp /path/to/lease.pdf "Lease Contracts/"

# Run setup test
python test_setup.py

# Start app
python run.py
```

Open [http://localhost:5001](http://localhost:5001) in your browser.

---

## 📂 Structure
```
app.py                     # Main Flask app
run.py                     # Launcher
change_port.py             # Utility to change server port
sensitive_data_protection.py# PII masking
requirements.txt
templates/index.html
Lease Contracts/           # Your PDFs
test_setup.py
test_document_functions.py
test_sensitive_integration.py  #Test if sensitive information
test_document_listing.py       #List out the documents the bot has access to
```

---

## 🔑 Notes
- Requires Python **3.8+**  
- `openai.txt` must contain your API key (not committed to GitHub)  
- Place lease PDFs inside `Lease Contracts/`  
- Default port: **5001** (change with `change_port.py`)  

---

## 🧪 Testing
```bash
pytest tests/
```

---

## 📝 License
Educational and personal use. Respect OpenAI usage policies.  
