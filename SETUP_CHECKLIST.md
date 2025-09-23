# ✅ Setup Checklist

Use this checklist to ensure everything is ready before running the web application.

## Pre-Run Checklist

### 📁 File Structure
- [ ] `app.py` exists
- [ ] `templates/index.html` exists
- [ ] `requirements.txt` exists
- [ ] `openai.txt` exists and has content
- [ ] `Lease Contracts/` folder exists
- [ ] PDF files are in `Lease Contracts/` folder

### 🔑 OpenAI API Key
- [ ] `openai.txt` contains a valid API key
- [ ] API key starts with `sk-`
- [ ] No extra text or quotes in the file
- [ ] OpenAI account has sufficient credits

### 🐍 Python Environment
- [ ] Python 3.8+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Virtual environment activated (recommended)

### 🌐 Network & Access
- [ ] Internet connection available
- [ ] OpenAI API access working
- [ ] Port 5000 is available

## Verification Commands

```bash
# 1. Check file structure
ls -la

# 2. Verify API key
cat openai.txt

# 3. Check PDF files
ls -la "Lease Contracts/"

# 4. Run setup test
python3 test_setup.py

# 5. Test imports
python3 -c "import flask; print('✅ Flask OK')"
python3 -c "import langchain; print('✅ LangChain OK')"
```

## Expected Output from test_setup.py

```
🧪 Testing Lease Document Q&A Setup...
==================================================
📁 Checking required files...
✅ app.py
✅ mainver2.py
✅ requirements.txt
✅ openai.txt
✅ README.md
✅ run.py
✅ templates/index.html

📂 Checking Lease Contracts folder...
✅ Lease Contracts folder exists
✅ Found X PDF files:
   📄 Lease Contracts/your-lease.pdf

🔑 Checking OpenAI API key...
✅ OpenAI API key file has content

==================================================
✅ Setup looks good! Ready to run.
```

## If Something is Missing

### Missing Files
- Copy files from the original directory
- Ensure you're in the `final/` directory

### No API Key
- Get API key from https://platform.openai.com/api-keys
- Add to `openai.txt` (just the key, no quotes)

### No PDFs
- Copy your lease PDFs to `Lease Contracts/` folder
- Ensure PDFs are readable

### Import Errors
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python3 --version`

## Ready to Run? ✅

If all items above are checked:
```bash
python3 run.py
```

Then open: http://localhost:5001
