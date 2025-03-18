import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import streamlit as st
import pytesseract
from pdf2image import convert_from_path
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch, RequestsHttpConnection, ConnectionError
from requests.auth import HTTPBasicAuth
import tempfile
import httpx

# Step 1: Set up Streamlit UI
def main():
    st.title("Local RAG System")
    uploaded_files = st.file_uploader("Upload PDFs", accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            text = extract_text_from_pdf(uploaded_file)
            embeddings = generate_embeddings(text)
            index_documents(text, embeddings, get_opensearch_client())
            st.write(f"Processed and indexed: {uploaded_file.name}")

    # Step 2: Ask a question
    question = st.text_input("Ask a question:")
    if question:
        results = search_documents(question, get_opensearch_client())
        answer = generate_answer(question, results, get_http_client())
        st.write(f"Answer: {answer}")

# Step 3: Extract text from PDF using OCR (PyTesseract)
def extract_text_from_pdf(uploaded_pdf):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_pdf.read())
        temp_file_path = temp_file.name

    images = convert_from_path(temp_file_path)
    text = ''.join([pytesseract.image_to_string(image) for image in images])
    return text

# Step 4: Generate embeddings using SentenceTransformers
def generate_embeddings(text):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    chunks = chunk_text(text)
    embeddings = model.encode(chunks)
    return embeddings

# Utility function to chunk text
def chunk_text(text, chunk_size=500):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Step 5: Set up and index documents in OpenSearch
def index_documents(text, embeddings, client):
    try:
        doc = {"text": text, "embedding": embeddings.tolist()}
        client.index(index="documents", body=doc)
    except ConnectionError:
        st.error("Failed to connect to OpenSearch. Please ensure the OpenSearch server is running.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Step 6: Search documents using hybrid search (text + embeddings)
def search_documents(query, client):
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode([query])[0].tolist()
        search_body = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"text": query}},
                        {"script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "cosineSimilarity(params.query_embedding, doc['embedding']) + 1.0",
                                "params": {"query_embedding": query_embedding}
                            }
                        }}
                    ]
                }
            }
        }
        st.write(f"Search body: {search_body}")  # Debugging information
        response = client.search(index="documents", body=search_body)
        st.write(f"OpenSearch response status: {response.status_code}")
        st.write(f"OpenSearch response body: {response.text}")
        return [hit["_source"]["text"] for hit in response['hits']['hits']]
    except ConnectionError:
        st.error("Failed to connect to OpenSearch. Please ensure the OpenSearch server is running.")
        return []
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

# Step 7: Generate an answer using Ollama
def generate_answer(question, context, http_client):
    prompt = f"Answer the following based on context: {context}. Question: {question}"
    try:
        payload = {
            "model": "llama3.2",
            "prompt": prompt
        }
        st.write(f"Request payload: {payload}")  # Debugging information
        response = httpx.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        st.write(f"Response content: {response.content.decode('utf-8')}")  # Debugging information
        response.raise_for_status()
        answer = response.json().get("answer", "No answer generated.")
        return answer
    except httpx.ConnectError:
        st.error("Failed to connect to Ollama. Please ensure the Ollama service is running.")
        return "Connection to Ollama failed."
    except httpx.HTTPStatusError as e:
        st.error(f"Error from Ollama service: {e.response.text}")
        return "Error from Ollama service."
    except httpx.RequestError as e:
        st.error(f"An error occurred while requesting: {e}")
        return "Request error."

def get_opensearch_client():
    admin_password = os.getenv('OPENSEARCH_INITIAL_ADMIN_PASSWORD')
    if not admin_password:
        st.error("OpenSearch admin password is not set. Please set the OPENSEARCH_INITIAL_ADMIN_PASSWORD environment variable.")
        return None

    return OpenSearch(
        hosts=[{'host': 'localhost', 'port': 9200}],
        http_auth=HTTPBasicAuth('admin', admin_password),
        use_ssl=False,
        verify_certs=False,
        connection_class=RequestsHttpConnection
    )

def get_http_client():
    return httpx.Client()

if __name__ == "__main__":
    main()