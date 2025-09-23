import os
import glob
import hashlib
from typing import List
import json

from flask import Flask, render_template, request, jsonify
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
import chromadb
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.callbacks import get_openai_callback
import tiktoken
from sensitive_data_protection import SensitiveDataProtector

app = Flask(__name__)

# ======== Configuration ========
folder_path = "Lease Contracts"
recursive = True
chunk_size = 1500
chunk_overlap = 100
persist_root = ".chroma"
# ===============================

# Global variables for the RAG system
rag_chain = None
vector_store = None
initialization_status = "Not initialized"
sensitive_data_protector = SensitiveDataProtector()
_comparison_keywords = [
    "compare",
    "difference",
    "differences",
    "across documents",
    "between documents",
    "all documents",
    "each document",
    "contrast",
]

# OpenAI API key from file if not present in env
if os.path.exists("openai.txt"):
    with open("openai.txt", "r") as f:
        key = f.read().strip()
    if key and "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = key

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def list_pdfs(root: str, recurse: bool) -> List[str]:
    root = os.path.abspath(root)
    if not recurse:
        return sorted(glob.glob(os.path.join(root, "*.pdf")))
    matches: List[str] = []
    for dirpath, _, _ in os.walk(root):
        matches.extend(sorted(glob.glob(os.path.join(dirpath, "*.pdf"))))
    return matches

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def format_docs(docs) -> str:
    return "\n".join(doc.page_content for doc in docs)

def mask_document_content(docs):
    """Mask sensitive information in documents before processing"""
    masked_docs = []
    for doc in docs:
        masked_content, _ = sensitive_data_protector.mask_sensitive_data(doc.page_content)
        # Create a new document with masked content
        from langchain.schema import Document
        masked_doc = Document(
            page_content=masked_content,
            metadata=doc.metadata
        )
        masked_docs.append(masked_doc)
    return masked_docs

def get_available_documents():
    """Get list of available documents in the system"""
    try:
        # Get documents from the Lease Contracts folder
        abs_folder = os.path.abspath(folder_path)
        pdfs = list_pdfs(abs_folder, recursive)
        
        # Get document information
        documents_info = []
        for pdf_path in pdfs:
            filename = os.path.basename(pdf_path)
            file_size = os.path.getsize(pdf_path)
            file_size_mb = round(file_size / (1024 * 1024), 2)
            
            # Check if document is indexed (has embeddings)
            is_indexed = vector_store is not None and vector_store._collection.count() > 0
            
            documents_info.append({
                'filename': filename,
                'path': pdf_path,
                'size_mb': file_size_mb,
                'indexed': is_indexed
            })
        
        return documents_info
    except Exception as e:
        print(f"Error getting document list: {e}")
        return []

def is_document_listing_question(question):
    """Check if the question is asking about available documents"""
    document_keywords = [
        'documents', 'files', 'leases', 'contracts', 'available', 'access',
        'what do you have', 'what files', 'which documents', 'list documents',
        'show me documents', 'what leases', 'what contracts'
    ]
    
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in document_keywords)

def create_document_listing_response():
    """Create a formatted response listing available documents"""
    documents = get_available_documents()
    
    if not documents:
        return (
            "<p>I don't currently have access to any documents. "
            "Please ensure PDF files are placed in the '<strong>Lease Contracts</strong>' folder.</p>"
        )
    
    items = []
    for i, doc in enumerate(documents, 1):
        status_icon = "✅" if doc['indexed'] else "⏳"
        status_text = "Indexed" if doc['indexed'] else "Processing"
        items.append(
            f"<li><strong>{i}. {doc['filename']}</strong> {status_icon} — "
            f"Size: {doc['size_mb']} MB • Status: {status_text}</li>"
        )

    html = [
        "<div>",
        "<p><strong>I have access to the following documents:</strong></p>",
        "<ul>",
        *items,
        "</ul>",
        "<p>You can ask questions such as:</p>",
        "<ul>",
        "<li><strong>What is the lease term in [filename]?</strong></li>",
        "<li><strong>What is the monthly rent in [filename]?</strong></li>",
        "<li><strong>What are the tenant responsibilities in [filename]?</strong></li>",
        "</ul>",
        "<p><em>Note:</em> Documents marked with ⏳ are still being processed and may not be fully searchable yet.</p>",
        "</div>",
    ]

    return "".join(html)

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens in text using tiktoken"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # Fallback to approximate counting if model not found
        return len(text.split()) * 1.3  # Rough approximation

def is_comparison_question(question: str) -> bool:
    q = question.lower()
    return any(k in q for k in _comparison_keywords)

def compare_across_documents(question: str) -> dict:
    """
    Structured multi-document comparison:
      - Retrieve chunks per file with metadata filter
      - Summarize per document
      - Compare summaries and list differences
    """
    global vector_store

    abs_folder = os.path.abspath(folder_path)
    pdfs = list_pdfs(abs_folder, recursive)
    if not pdfs:
        return {
            'answer': "I couldn't find any documents to compare.",
            'tokens': {
                'question_tokens': count_tokens(question),
                'context_tokens': 0,
                'total_input_tokens': count_tokens(question),
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': count_tokens(question)
            }
        }

    per_doc_summaries = []
    llm = ChatOpenAI(temperature=0)
    total_prompt = 0
    total_completion = 0

    sources_set = set()

    for pdf in pdfs:
        try:
            retriever = vector_store.as_retriever(
                search_kwargs={"k": 15, "filter": {"source": pdf}}
            )
            rel_docs = retriever.get_relevant_documents(question)
            if not rel_docs:
                retriever_alt = vector_store.as_retriever(
                    search_kwargs={"k": 15, "filter": {"file_path": pdf}}
                )
                rel_docs = retriever_alt.get_relevant_documents(question)

            doc_name = os.path.basename(pdf)
            if not rel_docs:
                per_doc_summaries.append({
                    "document": doc_name,
                    "summary": "No explicit details found.",
                })
                continue

            snippets = []
            for d in rel_docs:
                page = d.metadata.get("page")
                page_num = None
                try:
                    if isinstance(page, int):
                        page_num = page + 1
                    elif isinstance(page, str) and page.isdigit():
                        page_num = int(page) + 1
                except Exception:
                    page_num = None
                header = f"[Page {page_num}]" if page_num else ""
                snippets.append(f"{header} {d.page_content}".strip())
                # Track sources for final citation list
                if page_num is not None:
                    sources_set.add((doc_name, page_num))
            context = "\n\n".join(snippets)

            summarize_prompt = (
                "You are analyzing a single lease document. Based ONLY on the CONTEXT, "
                "summarize the parts relevant to the user's request as short bullets. "
                "If the information is not clearly present, say 'No explicit details found.'\n\n"
                f"DOCUMENT: {doc_name}\n"
                f"USER REQUEST: {question}\n"
                "CONTEXT:\n"
                f"{context}\n\n"
                "Output as short bullet points."
            )

            with get_openai_callback() as cb:
                _res = llm.invoke(summarize_prompt)
                summary = _res.content if hasattr(_res, 'content') else str(_res)
                total_prompt += cb.prompt_tokens
                total_completion += cb.completion_tokens

            per_doc_summaries.append({
                "document": doc_name,
                "summary": summary.strip(),
            })
        except Exception as e:
            print(f"Per-document summarize failed for {pdf}: {e}")
            continue

    if not per_doc_summaries:
        return {
            'answer': "I couldn't retrieve enough information from the documents to compare.",
            'tokens': {
                'question_tokens': count_tokens(question),
                'context_tokens': 0,
                'total_input_tokens': count_tokens(question),
                'prompt_tokens': total_prompt,
                'completion_tokens': total_completion,
                'total_tokens': total_prompt + total_completion
            }
        }

    comparisons_text = "\n\n".join(
        f"{item['document']}:\n{item['summary']}" for item in per_doc_summaries
    )
    compare_prompt = (
        "Compare the tenant-related terms across these documents. "
        "Answer ONLY the subject(s) explicitly asked by the user and strictly use the provided CONTEXT. "
        "If the question is about a specific topic (e.g., parking), DO NOT include other topics (e.g., responsibilities, remedies, notice periods). "
        "If the answer is not clearly stated in the context, reply exactly: Not specified in the provided documents. "
        "Do not add extra commentary or unrelated details. "
             
        "If a question is asked about identifying key differences policy-by-policy (e.g., rights, responsibilities, notice periods, remedies). "
        "Be specific and attribute differences to document names. "
        f"INPUT SUMMARIES:\n{comparisons_text}\n\n"
        "Return a clear, structured list of differences, grouped by topic."
    )

    with get_openai_callback() as cb:
        _cres = llm.invoke(compare_prompt)
        comparison_answer = _cres.content if hasattr(_cres, 'content') else str(_cres)
        total_prompt += cb.prompt_tokens
        total_completion += cb.completion_tokens

    # Append simple sources section
    sources_lines = []
    if sources_set:
        sources_lines.append("\nSources:\n")
        for (doc, pg) in sorted(sources_set):
            sources_lines.append(f"- [{doc} Page {pg}]")

    final_answer = comparison_answer.strip()
    if sources_lines:
        final_answer = final_answer + "\n\n" + "\n".join(sources_lines)

    return {
        'answer': final_answer,
        'tokens': {
            'question_tokens': count_tokens(question),
            'context_tokens': 0,
            'total_input_tokens': count_tokens(question),
            'prompt_tokens': total_prompt,
            'completion_tokens': total_completion,
            'total_tokens': total_prompt + total_completion
        }
    }

# (comparison helpers removed to restore original behavior)

def initialize_rag_system():
    """Initialize the RAG system - this will be called once at startup"""
    global rag_chain, vector_store, initialization_status
    
    try:
        print("🚀 Initializing RAG system...")
        initialization_status = "Initializing..."
        
        abs_folder = os.path.abspath(folder_path)
        folder_base = os.path.basename(abs_folder) or "pdfs"
        folder_hash = sha256_text(abs_folder)[:10]
        persist_dir = os.path.join(persist_root, f"{folder_base}-{folder_hash}")
        ensure_dir(persist_dir)

        embeddings = OpenAIEmbeddings()
        client = chromadb.PersistentClient(path=persist_dir)
        collection_name = "docs"
        vector_store = Chroma(client=client, collection_name=collection_name, embedding_function=embeddings)

        marker_dir = os.path.join(persist_dir, ".ingested")
        ensure_dir(marker_dir)

        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        pdfs = list_pdfs(abs_folder, recursive)
        if not pdfs:
            initialization_status = "Error: No PDFs found"
            return False

        # Ingest new/changed PDFs only
        ingested_count = 0
        for pdf in pdfs:
            try:
                fhash = sha256_file(pdf)[:10]
                marker = os.path.join(marker_dir, f"{os.path.basename(pdf)}-{fhash}.done")
                if os.path.exists(marker):
                    print(f"Skipping (already embedded): {os.path.basename(pdf)}")
                    continue

                print(f"Indexing: {os.path.basename(pdf)}")
                docs = PyMuPDFLoader(pdf).load()
                # Mask sensitive information before chunking
                masked_docs = mask_document_content(docs)
                chunks = splitter.split_documents(masked_docs)
                if chunks:
                    vector_store.add_documents(chunks)
                    ingested_count += 1
                    with open(marker, "w") as m:
                        m.write("ok")
            except Exception as e:
                print(f"Failed to index {pdf}: {e}")

        # Focused retriever to reduce unrelated context
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 6,
                "fetch_k": 30,
                "lambda_mult": 0.3,
            },
        )
        # Concise default prompt; only compare when explicitly asked
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a concise assistant for lease documents. "
             "Answer ONLY the subject(s) explicitly asked by the user and strictly use the provided CONTEXT. "
             "If the question is about a specific topic (e.g., parking), DO NOT include other topics (e.g., responsibilities, remedies, notice periods). "
             "If the answer is not clearly stated in the context, reply exactly: Not specified in the provided documents. "
             "Do not add extra commentary or unrelated details. "
             "Unless the user explicitly asks to compare across documents, do not synthesize multi-document comparisons. "
             "Respond with either a short paragraph (<= 3 sentences) or up to 3 concise bullet points."),
            ("human", "Question: {question}\n\nCONTEXT:\n{context}\n\nAnswer:")
        ])
        llm = ChatOpenAI(temperature=0, max_tokens=300)
        parser = StrOutputParser()

        # Build the RAG chain
        rag_chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
            | parser
        )

        doc_count = vector_store._collection.count()
        initialization_status = f"Ready - {doc_count} documents indexed"
        print(f"✅ RAG system initialized with {doc_count} documents")
        return True
        
    except Exception as e:
        initialization_status = f"Error: {str(e)}"
        print(f"❌ Failed to initialize RAG system: {e}")
        return False

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/status')
def status():
    """Get the current status of the RAG system"""
    return jsonify({
        'status': initialization_status,
        'ready': rag_chain is not None
    })

@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle question asking with token tracking"""
    global rag_chain
    
    if not rag_chain:
        return jsonify({
            'error': 'RAG system not initialized. Please wait and try again.'
        }), 500
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Check if question is asking about available documents
        if is_document_listing_question(question):
            document_listing_response = create_document_listing_response()
            question_tokens = count_tokens(question)
            
            return jsonify({
                'answer': document_listing_response,
                'tokens': {
                    'question_tokens': question_tokens,
                    'context_tokens': 0,
                    'total_input_tokens': question_tokens,
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_tokens': question_tokens
                },
                'document_listing': True
            })
        
        # Check if question is asking about sensitive information
        if sensitive_data_protector.is_question_about_sensitive_data(question):
            # Get detected sensitive data types from the question
            detected_types = list(sensitive_data_protector.detect_sensitive_data(question).keys())
            warning_message = sensitive_data_protector.create_sensitive_data_warning(question, detected_types)
            
            return jsonify({
                'answer': warning_message,
                'tokens': {
                    'question_tokens': count_tokens(question),
                    'context_tokens': 0,
                    'total_input_tokens': count_tokens(question),
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_tokens': count_tokens(question)
                },
                'sensitive_data_blocked': True
            })
        
        # Comparison questions need a different flow to ensure multi-document coverage
        compare_flag = bool(data.get('compare', False))
        if compare_flag or is_comparison_question(question):
            print("🔎 Comparison mode activated for question:", question)
            result = compare_across_documents(question)
            return jsonify(result)

        # Count input tokens (standard single-question flow)
        question_tokens = count_tokens(question)
        
        # Get retrieved context for token counting
        retriever = vector_store.as_retriever()
        retrieved_docs = retriever.get_relevant_documents(question)
        context = format_docs(retrieved_docs)
        context_tokens = count_tokens(context)
        
        # Run the RAG chain with token tracking
        with get_openai_callback() as cb:
            answer = rag_chain.invoke(question)
        
        # Prepare response with token information
        response = {
            'answer': answer,
            'tokens': {
                'question_tokens': question_tokens,
                'context_tokens': context_tokens,
                'total_input_tokens': question_tokens + context_tokens,
                'prompt_tokens': cb.prompt_tokens,
                'completion_tokens': cb.completion_tokens,
                'total_tokens': cb.total_tokens
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error processing question: {e}")
        return jsonify({
            'error': f'Error processing question: {str(e)}'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'rag_initialized': rag_chain is not None,
        'initialization_status': initialization_status
    })

if __name__ == '__main__':
    print("🌐 Starting Lease Document Q&A Web Application...")
    
    # Initialize the RAG system
    success = initialize_rag_system()
    
    if success:
        print("✅ Starting web server...")
        print("📱 Open your browser and go to: http://localhost:5001")
        print("🔍 You can now ask questions about your lease documents!")
    else:
        print("❌ Failed to initialize RAG system. Starting server anyway for debugging...")
    
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5001)
