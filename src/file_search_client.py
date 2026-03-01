"""
Core Google File Search API client wrapper using the official FileSearchStore API.
"""
from google import genai
from google.genai import types
from typing import List, Optional, Dict, Any
import os
import time
from pathlib import Path

from config.settings import settings

class FileSearchClient:
    """Wrapper class for Google AI File Search operations."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the client with API key."""
        self.api_key = api_key or settings.api_key
        self.client = genai.Client(api_key=self.api_key)
    
    def create_store(self, store_name: str) -> str:
        """
        Create a new File Search store.
        
        Args:
            store_name: Display name for the store
            
        Returns:
            Store name (resource ID) for future operations
        """
        try:
            file_search_store = self.client.file_search_stores.create(
                config={'display_name': store_name}
            )
            print(f"✅ Created File Search store: {store_name}")
            print(f"   Store ID: {file_search_store.name}")
            return file_search_store.name
        except Exception as e:
            print(f"❌ Error creating store '{store_name}': {e}")
            raise
    
    def list_stores(self) -> List[Dict[str, Any]]:
        """
        List all File Search stores.
        
        Returns:
            List of store information dictionaries
        """
        try:
            stores = []
            for store in self.client.file_search_stores.list():
                stores.append({
                    'name': store.name,
                    'display_name': getattr(store, 'display_name', store.name),
                    'create_time': getattr(store, 'create_time', 'N/A')
                })
            return stores
        except Exception as e:
            print(f"❌ Error listing stores: {e}")
            raise
    
    def get_store(self, store_name: str) -> Optional[Any]:
        """
        Get a specific File Search store by name.
        
        Args:
            store_name: Full resource name of the store
            
        Returns:
            Store object or None
        """
        try:
            return self.client.file_search_stores.get(name=store_name)
        except Exception as e:
            print(f"⚠️  Could not get store '{store_name}': {e}")
            return None
    
    def delete_store(self, store_name: str, force: bool = True) -> bool:
        """
        Delete a File Search store.
        
        Args:
            store_name: Full resource name of the store
            force: Whether to force deletion even if store has files
            
        Returns:
            True if successful
        """
        try:
            self.client.file_search_stores.delete(
                name=store_name,
                config={'force': force}
            )
            print(f"✅ Deleted File Search store: {store_name}")
            return True
        except Exception as e:
            print(f"❌ Error deleting store '{store_name}': {e}")
            raise
    
    def upload_document(
        self, 
        file_path: str, 
        store_name: str, 
        display_name: Optional[str] = None,
        chunking_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload a document directly to a File Search store.
        
        Args:
            file_path: Path to the file to upload
            store_name: Full resource name of the target store
            display_name: Optional display name for the file
            chunking_config: Optional chunking configuration
            
        Returns:
            Operation name
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Check file size
            file_size_mb = file_path_obj.stat().st_size / (1024 * 1024)
            if file_size_mb > settings.max_file_size_mb:
                raise ValueError(f"File size ({file_size_mb:.1f}MB) exceeds limit ({settings.max_file_size_mb}MB)")
            
            print(f"🔄 Uploading {file_path_obj.name} ({file_size_mb:.1f}MB)...")
            
            # Prepare config
            upload_config = {
                'display_name': display_name or file_path_obj.name
            }
            
            # Add chunking config if provided
            if chunking_config:
                upload_config['chunking_config'] = chunking_config
            
            # Upload directly to file search store
            operation = self.client.file_search_stores.upload_to_file_search_store(
                file=str(file_path_obj),
                file_search_store_name=store_name,
                config=upload_config
            )
            
            # Wait for operation to complete
            while not operation.done:
                print("⏳ Processing upload...")
                time.sleep(5)
                operation = self.client.operations.get(operation)
            
            print(f"✅ Successfully uploaded: {file_path_obj.name}")
            return operation.name
            
        except Exception as e:
            print(f"❌ Error uploading file '{file_path}': {e}")
            raise
    
    def upload_from_url(
        self,
        url: str,
        store_name: str,
        display_name: Optional[str] = None
    ) -> str:
        """
        Upload a document from URL to File Search store.
        
        Args:
            url: URL of the document to upload
            store_name: Full resource name of the target store
            display_name: Optional display name for the file
            
        Returns:
            Operation name
        """
        try:
            try:
                import httpx
            except ImportError:
                raise ImportError("httpx is required for URL uploads. Install with: pip install httpx")
            
            # Download the file temporarily
            response = httpx.get(url)
            response.raise_for_status()
            
            # Create temporary file
            temp_file = Path(f"temp_{int(time.time())}_{url.split('/')[-1]}")
            temp_file.write_bytes(response.content)
            
            try:
                # Upload the file
                operation_name = self.upload_document(
                    str(temp_file), 
                    store_name, 
                    display_name or url.split('/')[-1]
                )
                return operation_name
            finally:
                # Clean up temporary file
                if temp_file.exists():
                    temp_file.unlink()
                    
        except Exception as e:
            print(f"❌ Error uploading from URL '{url}': {e}")
            raise
    
    def list_files_in_store(self, store_name: str) -> List[Dict[str, Any]]:
        """
        List all files/documents in a File Search store.
        
        Args:
            store_name: Full resource name of the store
            
        Returns:
            List of file information dictionaries
        """
        try:
            # The documents are accessed via the store
            # Using file_search_stores documents list if available
            files = []
            # Note: The API may vary - adjust based on actual SDK capabilities
            try:
                for doc in self.client.file_search_stores.list_documents(name=store_name):
                    files.append({
                        'name': doc.name,
                        'display_name': getattr(doc, 'display_name', doc.name),
                        'size_bytes': getattr(doc, 'size_bytes', 0)
                    })
            except AttributeError:
                # Fallback: the list_documents may not be available in all SDK versions
                print("⚠️  Document listing not available in this SDK version")
            return files
        except Exception as e:
            print(f"❌ Error listing files in store '{store_name}': {e}")
            return []
    
    def get_store_by_name(self, display_name: str) -> Optional[str]:
        """
        Get store resource name by display name.
        
        Args:
            display_name: Display name to search for
            
        Returns:
            Store resource name if found, None otherwise
        """
        try:
            # If it already looks like a resource name, return it
            if display_name.startswith('fileSearchStores/'):
                return display_name
            
            # Search through stores
            for store in self.client.file_search_stores.list():
                store_display = getattr(store, 'display_name', '')
                if store_display == display_name or store.name == display_name:
                    return store.name
            return None
        except Exception as e:
            print(f"❌ Error searching for store '{display_name}': {e}")
            return None
    
    def get_client(self) -> genai.Client:
        """
        Get the underlying genai Client for advanced operations.
        
        Returns:
            genai.Client instance
        """
        return self.client
