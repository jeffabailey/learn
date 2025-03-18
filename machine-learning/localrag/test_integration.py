import os
import tempfile
import pytest
from unittest.mock import MagicMock
from index import extract_text_from_pdf, generate_embeddings, index_documents, search_documents, generate_answer

@pytest.fixture
def mock_opensearch_client():
    client = MagicMock()
    return client

@pytest.fixture
def mock_http_client():
    client = MagicMock()
    return client

def test_extract_text_from_pdf():
    sample_pdf_path = os.path.join(os.path.dirname(__file__), 'sample.pdf')
    with open(sample_pdf_path, 'rb') as temp_file:
        text = extract_text_from_pdf(temp_file)
    assert text is not None

def test_generate_embeddings():
    text = "Sample text for embedding"
    embeddings = generate_embeddings(text)
    assert embeddings is not None

def test_index_documents(mock_opensearch_client):
    text = "Sample text"
    embeddings = generate_embeddings(text)
    index_documents(text, embeddings, mock_opensearch_client)
    mock_opensearch_client.index.assert_called_once()

def test_search_documents(mock_opensearch_client):
    query = "Sample query"
    results = search_documents(query, mock_opensearch_client)
    assert results is not None

def test_generate_answer(mock_http_client):
    question = "Sample question"
    context = "Sample context"
    answer = generate_answer(question, context, mock_http_client)
    assert answer is not None