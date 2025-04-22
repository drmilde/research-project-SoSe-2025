import os
import PyPDF2
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

from langchain.text_splitter import RecursiveCharacterTextSplitter

import ollama
import json
import requests
import re

import argparse

parser = argparse.ArgumentParser(description='Talk to pdfs')
parser.add_argument('-q','--query', help='The query to be proccesed', type=str, default="What is data science?", required=False)
parser.add_argument('-t','--topic', help='Topic of the query', type=str, default="data science",  required=False)
args = vars(parser.parse_args())
topic = args["topic"]

#### asking question to ollama llama3.2

def ask(question):
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'system',
            'content': f'Your name is Hamish and you are a helpful AI assistant. You are an assistant for question-answering tasks on {topic}. Please always provide answers exclusively in English. So please speak English in your answers, no German. Use the following parts of the retrieved context to answer the question.',
        },
        {
            'role': 'user',
            'content': question,
        },
    ])
    return(response['message']['content'])


## pre processing of data

def extract_text_from_pdfs(folder_path):
    all_text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    all_text += page.extract_text()
    return all_text

pdf_folder = "dataset"
all_text = extract_text_from_pdfs(pdf_folder)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Size of each chunk
    chunk_overlap=50,  # Overlap between chunks to maintain context
    separators=["\n\n", "\n", " ", ""]  # Splitting hierarchy
)

chunks = text_splitter.split_text(all_text)

# Initialize a persistent ChromaDB client
client = chromadb.PersistentClient(path="chroma_db")

# Load the SentenceTransformer model for text embeddings
text_embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Delete existing collection (if needed)
try:
    client.delete_collection(name="knowledge_base")
    print("Deleted existing collection: knowledge_base")
except Exception as e:
    print(f"Collection does not exist or could not be deleted: {e}")

# Create a new collection for text embeddings
collection = client.create_collection(name="knowledge_base")

# Add text chunks to the collection
for i, chunk in enumerate(chunks):
    # Generate embeddings for the chunk
    embedding = text_embedding_model.encode(chunk)

    # Add to the collection with metadata
    collection.add(
        ids=[f"chunk_{i}"],  # Unique ID for each chunk
        embeddings=[embedding.tolist()],  # Embedding vector
        metadatas=[{"source": "pdf", "chunk_id": i}],  # Metadata
        documents=[chunk]  # Original text
    )


def semantic_search(query, top_k=5):
    # Generate embedding for the query
    query_embedding = text_embedding_model.encode(query)

    # Query the collection
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )
    return results



############### TRY RAG on Document Data ############

# Example query
query = "What is data science ?"
query = args["query"]
print (f"{query}\n")

results = semantic_search(query)

# Display results
#for i, result in enumerate(results['documents'][0]):
    #print(f"Result {i+1}: {result}\n")

# Retrieve the top results from semantic search
search_results = semantic_search(query)
context = "\n".join(search_results['documents'][0])

# Generate a response using the retrieved context
#response = generate_response(query, context)
prompt = f"Query: {query}\nContext: {context}\nAnswer:"

#####
response = ask(prompt)
print("Generated Response:\n\n", response)
