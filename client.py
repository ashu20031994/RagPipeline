import streamlit as st
from langchain.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings, OpenAIEmbeddings, SentenceTransformerEmbeddings
# from sentence_transformers import SentenceTransformer

from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from app import (create_pdf_loader, create_website_loader, delete_existing_files, create_chunks, retrieve_semantic_answer, retrieve_keyword_answer)
import os
import time

st.title("RaG Application")
st.session_state.clear()
st.write("Upload a PDF file or provide a website URL")
filetype = st.selectbox("Select the file type", ["PDF", "Website"])
if filetype == "PDF":
    uploaded_file = st.file_uploader("Upload the file", type=["pdf"])

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            # processing pdf file
            delete_existing_files()
            st.session_state.documents = create_pdf_loader(uploaded_file)
else:
    website_url = st.text_input("Enter the website url")
    if website_url:
        st.session_state.documents = create_website_loader(website_url)
        st.write(f"File has been uploaded and processed. ")

if "documents" in st.session_state:
    st.session_state.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    # st.session_state.llm = Ollama(model="llama-3.3-70b-versatile")
    st.session_state.final_documents = create_chunks(st.session_state.documents)
    st.write(f"documents are chunked: {len(st.session_state.final_documents)}")
    st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents,
                                                    st.session_state.embeddings)

if "vectors" in st.session_state:
    llm = Ollama(model="llama2")

    prompt = ChatPromptTemplate.from_template(
        """
        Answer the questions based on the provided context only. 
        Please provide the most accurate response based on the question
        <context>
        {context}
        </context>
        Question: {input}"""
    )
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever  = st.session_state.vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    prompt = st.text_input("Enter your question:")
    if prompt:
        semantic_response = retrieve_semantic_answer(prompt, st.session_state.vectors, document_chain)
        st.write("Semantic Search response")
        st.write(semantic_response["answer"])

        # With a streamlit expander
        with st.expander("Document Similarity Search"):
            # Find the relevant chunks
            for i, doc in enumerate(semantic_response["context"]):
                st.write(doc.page_content)
                st.write("--------------------------------")

        keyword_response = retrieve_keyword_answer(prompt, st.session_state.final_documents)
        
        st.write("Keyword Search response")
        for i, doc in enumerate(keyword_response):
            st.write(doc)
            st.write("--------------------------------")

        