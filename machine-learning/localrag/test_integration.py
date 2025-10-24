import os
import tempfile
import pytest
import numpy as np
from unittest.mock import MagicMock, patch, Mock
from index import (
    extract_text_from_pdf,
    generate_embeddings,
    index_documents,
    search_documents,
    generate_answer,
    chunk_text
)


@pytest.fixture
def mock_opensearch_client():
    """Mock OpenSearch client for testing"""
    client = MagicMock()
    client.index.return_value = {'result': 'created'}
    client.search.return_value = {
        'hits': {
            'hits': [
                {'_source': {'text': 'Sample result text'}}
            ]
        }
    }
    return client


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing"""
    client = MagicMock()
    response = MagicMock()
    response.json.return_value = {'response': 'Sample answer'}
    client.post.return_value = response
    return client


@pytest.fixture
def mock_file_upload():
    """Mock Streamlit file upload"""
    mock_file = MagicMock()
    mock_file.name = 'test.pdf'
    mock_file.read.return_value = b'PDF content'
    return mock_file


class TestChunkText:
    """Test the chunk_text utility function"""

    def test_chunk_text_default_size(self):
        """Test chunking text with default size"""
        text = "a" * 1000
        chunks = chunk_text(text)
        assert len(chunks) == 2
        assert len(chunks[0]) == 500

    def test_chunk_text_custom_size(self):
        """Test chunking text with custom size"""
        text = "a" * 1000
        chunks = chunk_text(text, chunk_size=250)
        assert len(chunks) == 4
        assert len(chunks[0]) == 250

    def test_chunk_text_small_text(self):
        """Test chunking small text"""
        text = "small text"
        chunks = chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0] == text


class TestExtractTextFromPDF:
    """Test PDF text extraction"""

    @patch('index.convert_from_path')
    @patch('index.pytesseract.image_to_string')
    def test_extract_text_from_pdf(self, mock_ocr, mock_convert, mock_file_upload):
        """Test extracting text from PDF"""
        mock_convert.return_value = [MagicMock()]
        mock_ocr.return_value = "Extracted text"

        text = extract_text_from_pdf(mock_file_upload)

        assert text == "Extracted text"
        mock_convert.assert_called_once()
        mock_ocr.assert_called_once()


class TestGenerateEmbeddings:
    """Test embedding generation"""

    def test_generate_embeddings(self):
        """Test that embeddings are generated"""
        text = "Sample text for embedding"
        embeddings = generate_embeddings(text)

        assert embeddings is not None
        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) > 0

    def test_generate_embeddings_multiple_chunks(self):
        """Test embeddings for multiple chunks"""
        text = "a" * 1000  # Will create 2 chunks
        embeddings = generate_embeddings(text)

        assert embeddings is not None
        assert len(embeddings) == 2  # Two chunks


class TestIndexDocuments:
    """Test document indexing"""

    def test_index_documents(self, mock_opensearch_client):
        """Test indexing documents in OpenSearch"""
        text = "Sample text"
        embeddings = generate_embeddings(text)

        index_documents(text, embeddings, mock_opensearch_client)

        mock_opensearch_client.index.assert_called_once()
        call_args = mock_opensearch_client.index.call_args
        assert call_args[1]['index'] == 'documents'
        assert 'text' in call_args[1]['body']
        assert 'embedding' in call_args[1]['body']

    def test_index_documents_handles_errors(self, mock_opensearch_client):
        """Test that indexing handles errors gracefully"""
        mock_opensearch_client.index.side_effect = Exception("Connection error")
        text = "Sample text"
        embeddings = generate_embeddings(text)

        # Should not raise exception
        try:
            index_documents(text, embeddings, mock_opensearch_client)
        except Exception:
            pytest.fail("index_documents should handle exceptions")


class TestSearchDocuments:
    """Test document search"""

    def test_search_documents(self, mock_opensearch_client):
        """Test searching documents"""
        query = "Sample query"

        results = search_documents(query, mock_opensearch_client)

        assert results is not None
        assert isinstance(results, list)
        mock_opensearch_client.search.assert_called_once()

    def test_search_documents_empty_results(self, mock_opensearch_client):
        """Test search with no results"""
        mock_opensearch_client.search.return_value = {'hits': {'hits': []}}
        query = "Sample query"

        results = search_documents(query, mock_opensearch_client)

        assert results == []

    def test_search_documents_handles_errors(self, mock_opensearch_client):
        """Test that search handles errors gracefully"""
        mock_opensearch_client.search.side_effect = Exception("Search error")
        query = "Sample query"

        results = search_documents(query, mock_opensearch_client)

        assert results == []


class TestGenerateAnswer:
    """Test answer generation"""

    def test_generate_answer(self, mock_http_client):
        """Test generating answer from context"""
        question = "Sample question"
        context = ["Sample context"]

        answer = generate_answer(question, context, mock_http_client)

        assert answer is not None
        mock_http_client.post.assert_called_once()

    def test_generate_answer_with_list_context(self, mock_http_client):
        """Test generating answer with multiple context items"""
        question = "Sample question"
        context = ["Context 1", "Context 2"]

        answer = generate_answer(question, context, mock_http_client)

        assert answer is not None