"""
Search manager for semantic search, query processing, and result retrieval using File Search tool.
"""
from google import genai
from google.genai import types
from typing import List, Optional, Dict, Any

from src.file_search_client import FileSearchClient
from src.response_handler import ResponseHandler, SearchResponse
from config.settings import settings
from config.prompts import PromptTemplates

class SearchManager:
    """Manages search operations using Google AI File Search tool."""

    def __init__(self, client: FileSearchClient, model_name: Optional[str] = None):
        """
        Initialize SearchManager.

        Args:
            client: FileSearchClient instance
            model_name: Model to use for generation (defaults to settings)
        """
        self.client = client
        self.model_name = model_name or settings.default_model
        self.response_handler = ResponseHandler()

    def search_and_generate(
        self,
        query: str,
        store_name: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = 1024
    ) -> SearchResponse:
        """
        Perform semantic search and generate response using File Search tool.

        Args:
            query: User query
            store_name: File Search store name (resource ID)
            system_prompt: Optional system prompt override
            temperature: Generation temperature (0.0-1.0)
            max_tokens: Maximum tokens in response

        Returns:
            SearchResponse with answer and citations
        """
        try:
            # Resolve store name if needed
            resolved_store = self.client.get_store_by_name(store_name)
            if not resolved_store:
                return SearchResponse(
                    answer=f"Store '{store_name}' not found. Please create one first using 'create-store' command.",
                    citations=[],
                    model_used=self.model_name,
                    query=query
                )
            
            # Prepare the prompt
            formatted_query = PromptTemplates.format_search_prompt(query)
            
            print(f"🔍 Searching in store '{store_name}' for: {query[:100]}...")
            
            # Build the generation config with File Search tool
            gen_config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                system_instruction=system_prompt or PromptTemplates.RAG_SYSTEM_PROMPT,
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[resolved_store]
                        )
                    )
                ]
            )
            
            # Generate response with File Search grounding
            response = self.client.get_client().models.generate_content(
                model=self.model_name,
                contents=formatted_query,
                config=gen_config
            )
            
            # Process the response
            search_response = self.response_handler.process_response(
                response=response,
                query=query,
                model_name=self.model_name
            )
            
            print(f"✅ Generated response with File Search grounding")
            return search_response
            
        except Exception as e:
            print(f"❌ Error during search and generation: {e}")
            # Return error response
            return SearchResponse(
                answer=f"Error processing query: {e}",
                citations=[],
                model_used=self.model_name,
                query=query
            )
    
    def search_multiple_stores(
        self,
        query: str,
        store_names: List[str],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1
    ) -> SearchResponse:
        """
        Search across multiple File Search stores.
        
        Args:
            query: User query
            store_names: List of store names to search
            system_prompt: Optional system prompt override
            temperature: Generation temperature
            
        Returns:
            SearchResponse combining results from all stores
        """
        try:
            # Resolve all store names
            resolved_stores = []
            for store_name in store_names:
                resolved = self.client.get_store_by_name(store_name)
                if resolved:
                    resolved_stores.append(resolved)
                else:
                    print(f"⚠️  Store '{store_name}' not found, skipping")
            
            if not resolved_stores:
                return SearchResponse(
                    answer=f"No valid stores found in: {', '.join(store_names)}",
                    citations=[],
                    model_used=self.model_name,
                    query=query
                )
            
            formatted_query = PromptTemplates.format_search_prompt(query)
            
            print(f"🔍 Searching across {len(resolved_stores)} stores for: {query[:100]}...")
            
            # Build config with multiple stores
            gen_config = types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_prompt or PromptTemplates.RAG_SYSTEM_PROMPT,
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=resolved_stores
                        )
                    )
                ]
            )
            
            response = self.client.get_client().models.generate_content(
                model=self.model_name,
                contents=formatted_query,
                config=gen_config
            )
            
            search_response = self.response_handler.process_response(
                response=response,
                query=query,
                model_name=self.model_name
            )
            
            print(f"✅ Found response from {len(resolved_stores)} stores")
            return search_response
            
        except Exception as e:
            print(f"❌ Error during multi-store search: {e}")
            return SearchResponse(
                answer=f"Error processing multi-store query: {e}",
                citations=[],
                model_used=self.model_name,
                query=query
            )
    
    def ask_question(
        self,
        question: str,
        store_name: str,
        context: Optional[str] = None
    ) -> SearchResponse:
        """
        Ask a specific question with optional additional context.
        
        Args:
            question: Direct question to ask
            store_name: File Search store to search
            context: Optional additional context
            
        Returns:
            SearchResponse with direct answer
        """
        try:
            # Format as Q&A prompt
            formatted_prompt = PromptTemplates.format_qa_prompt(question)
            
            if context:
                formatted_prompt = f"Additional context: {context}\n\n{formatted_prompt}"
            
            return self.search_and_generate(
                query=formatted_prompt,
                store_name=store_name,
                temperature=0.0,  # More deterministic for Q&A
                max_tokens=1024
            )
            
        except Exception as e:
            print(f"❌ Error during question answering: {e}")
            return SearchResponse(
                answer=f"Error processing question: {e}",
                citations=[],
                model_used=self.model_name,
                query=question
            )
    
    def summarize_documents(
        self,
        store_name: str,
        focus_topic: Optional[str] = None
    ) -> SearchResponse:
        """
        Generate a summary of documents in a store.
        
        Args:
            store_name: File Search store to summarize
            focus_topic: Optional topic to focus the summary on
            
        Returns:
            SearchResponse with document summary
        """
        try:
            if focus_topic:
                query = f"{PromptTemplates.SUMMARIZATION_PROMPT}\n\nFocus particularly on information related to: {focus_topic}"
            else:
                query = PromptTemplates.SUMMARIZATION_PROMPT
            
            return self.search_and_generate(
                query=query,
                store_name=store_name,
                temperature=0.3,  # Slightly more creative for summaries
                max_tokens=3072
            )
            
        except Exception as e:
            print(f"❌ Error during document summarization: {e}")
            return SearchResponse(
                answer=f"Error generating summary: {e}",
                citations=[],
                model_used=self.model_name,
                query="Document summarization"
            )
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        try:
            model = self.client.get_client().models.get(name=f"models/{self.model_name}")
            return {
                'name': model.name,
                'display_name': getattr(model, 'display_name', model.name),
                'description': getattr(model, 'description', 'N/A'),
                'input_token_limit': getattr(model, 'input_token_limit', 'N/A'),
                'output_token_limit': getattr(model, 'output_token_limit', 'N/A')
            }
        except Exception as e:
            return {
                'name': self.model_name,
                'error': f"Could not retrieve model info: {e}"
            }
    
    def set_model(self, model_name: str) -> bool:
        """
        Change the model used for generation.
        
        Args:
            model_name: Name of the new model
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Test if model exists and is accessible
            self.client.get_client().models.get(name=f"models/{model_name}")
            self.model_name = model_name
            print(f"✅ Switched to model: {model_name}")
            return True
        except Exception as e:
            print(f"❌ Error switching to model '{model_name}': {e}")
            return False
    
    def batch_search(
        self,
        queries: List[str],
        store_name: str,
        delay_seconds: float = 1.0
    ) -> List[SearchResponse]:
        """
        Process multiple queries with rate limiting.
        
        Args:
            queries: List of queries to process
            store_name: File Search store to search
            delay_seconds: Delay between requests
            
        Returns:
            List of SearchResponse objects
        """
        import time
        
        results = []
        
        for i, query in enumerate(queries, 1):
            print(f"🔄 Processing query {i}/{len(queries)}: {query[:50]}...")
            
            try:
                response = self.search_and_generate(query, store_name)
                results.append(response)
                
                # Rate limiting
                if i < len(queries):  # Don't delay after last query
                    time.sleep(delay_seconds)
                    
            except Exception as e:
                print(f"❌ Error processing query {i}: {e}")
                results.append(SearchResponse(
                    answer=f"Error processing query: {e}",
                    citations=[],
                    model_used=self.model_name,
                    query=query
                ))
        
        print(f"✅ Completed batch processing of {len(queries)} queries")
        return results
