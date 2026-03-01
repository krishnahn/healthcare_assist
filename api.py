"""
FastAPI REST API for Google File Search RAG System.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
from pathlib import Path
import tempfile
import os
import time
import hashlib
from cachetools import TTLCache

# Add the current directory to the path for imports
sys.path.append(str(Path(__file__).parent))

from src.search_manager import SearchManager
from src.file_search_client import FileSearchClient
from src.document_processor import DocumentProcessor
from src.response_handler import ResponseHandler

# Initialize FastAPI app
app = FastAPI(
    title="RAG System API",
    description="Google File Search RAG System REST API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
try:
    client = FileSearchClient()
    search_manager = SearchManager(client)
    doc_processor = DocumentProcessor(client)
    print("✅ RAG system initialized successfully!")
except Exception as e:
    print(f"❌ Failed to initialize RAG system: {e}")
    sys.exit(1)

# Initialize cache for search results (100 queries, 1 hour TTL)
search_cache = TTLCache(maxsize=100, ttl=3600)

def get_cache_key(query: str, store_name: str, temperature: float, max_tokens: int) -> str:
    """Generate a unique cache key for the query"""
    key_string = f"{query}:{store_name}:{temperature}:{max_tokens}"
    return hashlib.md5(key_string.encode()).hexdigest()

# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    store_name: str
    temperature: float = 0.0
    max_tokens: int = 512  # Reduced from 1024 for faster responses
    system_prompt: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class StoreRequest(BaseModel):
    store_name: str

class StoreResponse(BaseModel):
    success: bool
    store_id: Optional[str] = None
    message: str

class UploadResponse(BaseModel):
    success: bool
    file_id: Optional[str] = None
    filename: str
    message: str

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "RAG System API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/api/search", response_model=QueryResponse)
async def search(request: QueryRequest):
    """
    Search and generate response from documents
    
    Args:
        request: QueryRequest with query, store_name, and optional parameters
        
    Returns:
        QueryResponse with answer, citations, and metadata
    """
    try:
        start_time = time.time()
        
        # Check cache first (only for queries without custom system prompt)
        cache_key = None
        if request.system_prompt is None:
            cache_key = get_cache_key(
                request.query, 
                request.store_name, 
                request.temperature, 
                request.max_tokens
            )
            if cache_key in search_cache:
                cached_response = search_cache[cache_key]
                processing_time = time.time() - start_time
                cached_response.metadata["processing_time"] = processing_time
                cached_response.metadata["cached"] = True
                print(f"✅ Cache HIT - Query: '{request.query[:50]}...' in {processing_time:.2f}s")
                return cached_response
        
        # Cache miss - perform actual search
        result = search_manager.search_and_generate(
            query=request.query,
            store_name=request.store_name,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt
        )
        
        processing_time = time.time() - start_time
        
        # Convert Citation objects to dictionaries
        citations_list = [
            {
                "file_name": cite.file_name,
                "chunk_text": cite.chunk_text,
                "page_number": cite.page_number,
                "score": cite.score,
                "metadata": cite.metadata
            }
            for cite in result.citations
        ]
        
        # Prepare metadata
        metadata = result.grounding_metadata or {}
        metadata["processing_time"] = processing_time
        metadata["query"] = request.query
        metadata["model"] = result.model_used
        metadata["cached"] = False
        
        response = QueryResponse(
            answer=result.answer,
            citations=citations_list,
            metadata=metadata
        )
        
        # Store in cache (only for queries without custom system prompt)
        if cache_key is not None:
            search_cache[cache_key] = response
            print(f"📝 Cache MISS - Cached query: '{request.query[:50]}...' in {processing_time:.2f}s")
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Ask a direct question (alias for search endpoint)
    """
    return await search(request)

@app.post("/api/summarize")
async def summarize_store(request: StoreRequest):
    """
    Generate a summary of all documents in the store
    """
    try:
        result = search_manager.generate_summary(request.store_name)
        
        # Convert Citation objects to dictionaries
        citations_list = [
            {
                "file_name": cite.file_name,
                "chunk_text": cite.chunk_text,
                "page_number": cite.page_number,
                "score": cite.score,
                "metadata": cite.metadata
            }
            for cite in result.citations
        ]
        
        return {
            "summary": result.answer,
            "citations": citations_list,
            "metadata": result.grounding_metadata or {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    store_name: str = Form(...)
):
    """
    Upload a document to the specified store
    
    Args:
        file: File to upload
        store_name: Name of the store to upload to
        
    Returns:
        UploadResponse with success status and file information
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Upload the file
            file_id = doc_processor.upload_file(tmp_file_path, store_name)
            
            return UploadResponse(
                success=True,
                file_id=file_id,
                filename=file.filename,
                message=f"Successfully uploaded {file.filename}"
            )
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/upload-directory")
async def upload_directory(
    directory_path: str = Form(...),
    store_name: str = Form(...)
):
    """
    Upload all files from a directory to the specified store
    """
    try:
        result = doc_processor.upload_directory(directory_path, store_name)
        return {
            "success": True,
            "files_uploaded": result,
            "message": f"Successfully uploaded {result} files"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Directory upload failed: {str(e)}")

@app.get("/api/stores")
async def list_stores():
    """
    List all available stores
    
    Returns:
        Dictionary with list of stores and their information
    """
    try:
        stores = client.list_stores()
        return {
            "success": True,
            "count": len(stores),
            "stores": stores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list stores: {str(e)}")

@app.post("/api/stores", response_model=StoreResponse)
async def create_store(request: StoreRequest):
    """
    Create a new File Search store
    
    Args:
        request: StoreRequest with store_name
        
    Returns:
        StoreResponse with success status and store_id
    """
    try:
        store_id = client.create_store(request.store_name)
        return StoreResponse(
            success=True,
            store_id=store_id,
            message=f"Successfully created store '{request.store_name}'"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create store: {str(e)}")

@app.delete("/api/stores/{store_name}")
async def delete_store(store_name: str):
    """
    Delete a File Search store
    
    Args:
        store_name: Name of the store to delete
        
    Returns:
        Success status and message
    """
    try:
        client.delete_store(store_name)
        return {
            "success": True,
            "message": f"Successfully deleted store '{store_name}'"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete store: {str(e)}")

@app.get("/api/store-info/{store_name}")
async def get_store_info(store_name: str):
    """
    Get information about a specific store
    """
    try:
        stores = client.list_stores()
        store = next((s for s in stores if s['display_name'] == store_name), None)
        
        if not store:
            raise HTTPException(status_code=404, detail=f"Store '{store_name}' not found")
        
        return {
            "success": True,
            "store": store
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get store info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
