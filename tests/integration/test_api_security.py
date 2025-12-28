import pytest
import io
from src.app import create_app

@pytest.fixture
def client():
    """Create test client"""
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client

def test_upload_valid_pdf_structure(client):
    """Test upload with valid PDF structure (magic numbers)"""
    # %PDF-1.4 header
    pdf_content = b'%PDF-1.4\n%...'
    data = {
        'file': (io.BytesIO(pdf_content), 'resume.pdf')
    }
    
    # We expect this to pass security check but might fail parsing if not valid PDF syntax
    # blocking parsing error is fine, blocking security error is bad.
    response = client.post(
        '/api/resumes', 
        data=data,
        content_type='multipart/form-data'
    )
    
    # It should pass security. 
    # If parser fails, it returns 500 or 400 error from parser.
    # Security error is "Invalid file content..."
    assert b'Invalid file content' not in response.data
