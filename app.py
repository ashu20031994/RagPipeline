import os
from langchain_community.document_loaders import PyPDFDirectoryLoader, WebBaseLoader
import bs4  
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def delete_existing_files():
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        

def create_pdf_loader(uploaded_file):
    # check if file is pdf
    if uploaded_file.type == "application/pdf":
        # Save the uploaded file to the server
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        # Load the PDF file
        loader = PyPDFDirectoryLoader(UPLOAD_FOLDER)
        documents = loader.load() 
        return documents
        
def create_website_loader(website_url):
        loader = WebBaseLoader(website_url)
        documents = loader.load()
        return documents

def create_chunks(documents):
    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(documents)
    return final_documents

def retrieve_semantic_answer(prompt, vectorstore, document_chain):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    result = retrieval_chain.invoke({"input": prompt})
    return result

def remove_stopwords(text):
    stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", 
                  "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 
                  'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 
                  'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 
                  'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 
                  'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at',
                  'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 
                  'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 
                  'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 
                  'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 
                  'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 
                  'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', 
                  "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't",
                    'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 
                    'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

    word_tokens = (text).split(" ")
    filtered_text = [word for word in word_tokens if word.lower() not in stop_words]
    return filtered_text

def match_all_keywords(chunk, keywords):
    
    chunk = (chunk.page_content.lower()).split(" ")
    for keyword in keywords:
        if keyword.lower() not in chunk:
            return False
    return True
def retrieve_keyword_answer(prompt, final_documents):
    prompt = remove_stopwords(prompt)
    matched_docs = []
    for docs in final_documents:
        if match_all_keywords(docs, prompt):
            print("Matched Document: ", docs.page_content)
            matched_docs.append(docs.page_content)
    return matched_docs