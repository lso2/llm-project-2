import streamlit as st
from pdfminer.high_level import extract_text
from docx2python import docx2python
from bs4 import BeautifulSoup
import google.generativeai as genai

st.title("LLM Document Q&A System")

st.link_button("View the Deployed Web App", "https://llm-project-2.streamlit.app/")

# Question 1
# Open-source LLM setup (Ollama) with fallback
llm = None
try:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.2:latest", temperature=0)
except:
    pass

# Read documents
def read_document(file_input):
    if not file_input:
        return ""
    
    if hasattr(file_input, 'name'):
        filename = file_input.name
        if filename.endswith('.pdf'):
            text = extract_text(file_input)
            return text
        elif filename.endswith('.docx'):
            doc = docx2python(file_input)
            return doc.text
        elif filename.endswith('.html'):
            soup = BeautifulSoup(file_input, 'html.parser')
            return soup.text
        elif filename.endswith('.txt'):
            text = file_input.read()
            if isinstance(text, bytes):
                text = text.decode('utf-8')
            return text
    return ""

# Answer questions with Ollama
def answer_question_ollama(question, document_file=None):
    if document_file:
        context = read_document(document_file)
        prompt = f"{context}\n\nAnswer this question only: {question}\n\nAnswer:"
    else:
        prompt = question
    
    ai_msg = llm.invoke(prompt)
    return ai_msg.content

# Question 2
# Extract abbreviations with Ollama
def generate_abbreviation_index_ollama(document_file):
    context = read_document(document_file)
    prompt = f"Extract abbreviations, in a bulleted list, format 'ABBR: full term':\n\n{context}"
    ai_msg = llm.invoke(prompt)
    return ai_msg.content

# Question 4
# Answer questions with Gemini
def answer_question_gemini(question, document_file=None, api_key=""):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    if document_file:
        context = read_document(document_file)
        prompt = f"Based on this document, answer: {question}\n\nDocument: {context}"
    else:
        prompt = question
    
    response = model.generate_content(prompt)
    return response.text

# Extract abbreviations with Gemini
def generate_abbreviation_index_gemini(document_file, api_key=""):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    context = read_document(document_file)
    prompt = f"Extract abbreviations, in a bulleted list, format 'ABBR: full term':\n\n{context}"
    response = model.generate_content(prompt)
    return response.text

llm_choice = st.radio("Choose an LLM", ["Ollama 2.3 (Open Source)", "Google Gemini 2.5 Flash (Closed Source)"])

# API key for Gemini
gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")

uploaded_file = st.file_uploader("Upload Document", type=["pdf", "docx", "txt", "html"])

question = st.text_input("Enter Question")

if st.button("Get Answer"):
    if question:
        if llm_choice == "Ollama 2.3 (Open Source)" and llm is not None:
            try:
                answer = answer_question_ollama(question, uploaded_file)
            except:
                st.warning("Ollama not available, using Gemini instead")
                answer = answer_question_gemini(question, uploaded_file, gemini_api_key)
        elif llm_choice == "Ollama 2.3 (Open Source)" and llm is None:
            st.warning("Ollama not available, using Gemini instead")
            answer = answer_question_gemini(question, uploaded_file, gemini_api_key)
        else:
            answer = answer_question_gemini(question, uploaded_file, gemini_api_key)
        st.write(answer)

# Abbreviation button
if st.button("Extract Abbreviations"):
    if uploaded_file:
        if llm_choice == "Ollama 2.3 (Open Source)" and llm is not None:
            try:
                abbreviations = generate_abbreviation_index_ollama(uploaded_file)
            except:
                st.warning("Ollama not available, using Gemini instead")
                abbreviations = generate_abbreviation_index_gemini(uploaded_file, gemini_api_key)
        elif llm_choice == "Ollama 2.3 (Open Source)" and llm is None:
            st.warning("Ollama not available, using Gemini instead")
            abbreviations = generate_abbreviation_index_gemini(uploaded_file, gemini_api_key)
        else:
            abbreviations = generate_abbreviation_index_gemini(uploaded_file, gemini_api_key)
        st.write(abbreviations)
		
st.divider()
st.write("&nbsp; &nbsp; &nbsp; &nbsp; LLM App Final Project by James &nbsp; &nbsp; &bull; &nbsp; &nbsp; MS Business Analytics & Data Science &nbsp; &nbsp; &bull; &nbsp; &nbsp; December 7, 2025")