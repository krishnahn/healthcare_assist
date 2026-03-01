"""
System prompts and templates for the RAG system.
OPTIMIZED for speed - shorter prompts = faster processing.
"""

class PromptTemplates:
    """Collection of prompt templates for different use cases."""
    
    # OPTIMIZED: Reduced from 300+ tokens to ~80 tokens
    RAG_SYSTEM_PROMPT = """You are a precise assistant answering from provided documents only.

RULES:
1. Use ONLY document information - no external knowledge
2. If not found, say "Not available in documents"
3. Be concise and direct
4. Match response language to question language
5. No source citations"""

    SEARCH_PROMPT_TEMPLATE = """Answer using ONLY the provided documents.

Question: {query}

Direct, concise answer in question's language. No sources."""

    SUMMARIZATION_PROMPT = """Summarize key information from the documents. Be concise. No sources."""

    QUESTION_ANSWERING_PROMPT = """Question: {query}

Answer directly from documents only. Match question language. No sources.
For greetings, respond politely mentioning you help with document queries."""

    @classmethod
    def format_search_prompt(cls, query: str) -> str:
        """Format the search prompt with the user query."""
        return cls.SEARCH_PROMPT_TEMPLATE.format(query=query)
    
    @classmethod
    def format_qa_prompt(cls, query: str) -> str:
        """Format the question-answering prompt with the user query."""
        return cls.QUESTION_ANSWERING_PROMPT.format(query=query)
