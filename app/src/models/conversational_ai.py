# src/models/conversational_ai.py

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os

from src.processing.document_parser import extract_sections

def create_retriever_for_document(file_path: str):
    # ... (This function is the same as before, so it's omitted for brevity) ...
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            document_text = f.read()
    except FileNotFoundError:
        return None
    sections = extract_sections(document_text)
    chunks = [Document(page_content=content, metadata={"section": header}) for header, content in sections.items()]
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embedding_function)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    return retriever

# --- Main block for running the full RAG pipeline ---
if __name__ == '__main__':
    test_doc_path = 'data/raw/proposals/content/MOC_01.txt'
    
    # Step 1: Create the retriever
    retriever = create_retriever_for_document(test_doc_path)
    
    if retriever:
        # Step 2: Define the LLM and the Prompt Template
        llm = ChatOllama(model="tinyllama")
        
        prompt_template = """
        You are an expert assistant for reviewing research proposals.
        Answer the user's question based ONLY on the following context.
        If the information is not in the context, say "I cannot find that information in the document."

        Context:
        {context}

        Question:
        {question}
        """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)

        # Step 3: Create the RAG Chain
        # This chains together the retriever, prompt, LLM, and output parser.
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        # Step 4: Ask a question
        query = "In a few bullet points, what is the proposed methodology?"
        print(f"\n--- Running RAG chain with query: '{query}' ---")
        
        # The .invoke() method now runs the entire pipeline
        answer = rag_chain.invoke(query)
        
        print("\n--- Generated Answer ---")
        print(answer)