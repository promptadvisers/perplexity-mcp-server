"""
Perplexity Sonar MCP Server (FastMCP Implementation)
An MCP server that provides access to Perplexity's Sonar API for web-grounded AI responses
"""

from mcp.server.fastmcp import FastMCP
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from typing import Optional
import aiohttp
import os

# Load environment variables
load_dotenv()

# Global session to be managed by lifespan
_session: Optional[aiohttp.ClientSession] = None
_api_key: Optional[str] = None
_base_url = "https://api.perplexity.ai/chat/completions"

# ============================================
# Lifespan Management
# ============================================
@asynccontextmanager
async def lifespan(app):
    """Initialize and clean up resources"""
    global _session, _api_key
    
    _api_key = os.getenv("PERPLEXITY_API_KEY")
    if not _api_key:
        raise ValueError("PERPLEXITY_API_KEY environment variable is required")
    
    # Create HTTP session
    _session = aiohttp.ClientSession()
    
    try:
        yield
    finally:
        # Clean up
        await _session.close()

# ============================================
# Initialize MCP Server
# ============================================
mcp = FastMCP("perplexity-sonar", lifespan=lifespan)

# ============================================
# Tools
# ============================================

@mcp.tool()
async def search_web(
    query: str,
    model: str = "sonar",
    search_recency: Optional[str] = None,
    search_domain: Optional[str] = None,
    search_context_size: str = "auto"
) -> str:
    """Search the web using Perplexity Sonar and get AI-powered answers with citations.
    
    Args:
        query: The search query or question to answer
        model: Model to use ('sonar', 'sonar-pro', 'sonar-reasoning', 'sonar-reasoning-pro')
        search_recency: Time filter ('day', 'week', 'month', 'year', None for all time)
        search_domain: Comma-separated domains to search (e.g., 'perplexity.ai,wikipedia.org')
        search_context_size: Amount of context ('low', 'medium', 'high', 'auto')
    
    Returns:
        AI-generated answer with citations
    """
    try:
        headers = {
            "Authorization": f"Bearer {_api_key}",
            "Content-Type": "application/json"
        }
        
        # Build request payload
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "search_context_size": search_context_size
        }
        
        # Add optional parameters
        if search_recency:
            payload["search_recency_filter"] = search_recency
        
        if search_domain:
            payload["search_domain_filter"] = search_domain.split(",")
        
        # Make API request
        async with _session.post(
            _base_url,
            headers=headers,
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                return f"Error: API returned status {response.status}: {error_text}"
            
            result = await response.json()
            
            # Format response with citations
            content = result["choices"][0]["message"]["content"]
            citations = result.get("citations", [])
            
            formatted_response = f"{content}\n\n"
            if citations:
                formatted_response += "Sources:\n"
                for i, citation in enumerate(citations, 1):
                    formatted_response += f"{i}. {citation}\n"
            
            return formatted_response
            
    except Exception as e:
        return f"Error searching web: {str(e)}"

@mcp.tool()
async def search_academic(
    query: str,
    model: str = "sonar",
    search_recency: Optional[str] = None,
    search_context_size: str = "auto"
) -> str:
    """Search academic sources using Perplexity Sonar with academic filtering.
    
    Args:
        query: The academic search query or research question
        model: Model to use ('sonar', 'sonar-pro', 'sonar-reasoning', 'sonar-reasoning-pro')
        search_recency: Time filter ('day', 'week', 'month', 'year', None for all time)
        search_context_size: Amount of context ('low', 'medium', 'high', 'auto')
    
    Returns:
        AI-generated answer based on academic sources with citations
    """
    try:
        headers = {
            "Authorization": f"Bearer {_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "search_domain_filter": ["scholar.google.com", "pubmed.ncbi.nlm.nih.gov", "arxiv.org"],
            "search_context_size": search_context_size
        }
        
        if search_recency:
            payload["search_recency_filter"] = search_recency
        
        async with _session.post(
            _base_url,
            headers=headers,
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                return f"Error: API returned status {response.status}: {error_text}"
            
            result = await response.json()
            
            content = result["choices"][0]["message"]["content"]
            citations = result.get("citations", [])
            
            formatted_response = f"{content}\n\n"
            if citations:
                formatted_response += "Academic Sources:\n"
                for i, citation in enumerate(citations, 1):
                    formatted_response += f"{i}. {citation}\n"
            
            return formatted_response
            
    except Exception as e:
        return f"Error searching academic sources: {str(e)}"

@mcp.tool()
async def search_with_context(
    query: str,
    context: str,
    model: str = "sonar-pro",
    search_context_size: str = "high"
) -> str:
    """Search the web with additional context for more nuanced answers.
    
    Args:
        query: The main search query
        context: Additional context to guide the search (background info, constraints, etc.)
        model: Model to use (defaults to 'sonar-pro' for better context understanding)
        search_context_size: Amount of context (defaults to 'high' for detailed answers)
    
    Returns:
        Contextually-aware AI answer with citations
    """
    try:
        headers = {
            "Authorization": f"Bearer {_api_key}",
            "Content-Type": "application/json"
        }
        
        # Combine query with context
        full_query = f"Context: {context}\n\nQuestion: {query}"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": full_query
                }
            ],
            "search_context_size": search_context_size
        }
        
        async with _session.post(
            _base_url,
            headers=headers,
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                return f"Error: API returned status {response.status}: {error_text}"
            
            result = await response.json()
            
            content = result["choices"][0]["message"]["content"]
            citations = result.get("citations", [])
            search_results = result.get("search_results", [])
            
            formatted_response = f"{content}\n\n"
            
            # Include search results snippets if available
            if search_results:
                formatted_response += "Search Results:\n"
                for sr in search_results[:5]:  # Limit to top 5
                    formatted_response += f"- {sr.get('title', 'No title')}: {sr.get('snippet', 'No snippet')[:150]}...\n"
                formatted_response += "\n"
            
            if citations:
                formatted_response += "Sources:\n"
                for i, citation in enumerate(citations, 1):
                    formatted_response += f"{i}. {citation}\n"
            
            return formatted_response
            
    except Exception as e:
        return f"Error with contextual search: {str(e)}"

@mcp.tool()
async def reasoning_search(
    query: str,
    model: str = "sonar-reasoning",
    search_context_size: str = "high"
) -> str:
    """Use Perplexity's reasoning models for complex, multi-step queries.
    
    Best for:
    - Complex analytical questions
    - Multi-step problem solving
    - Questions requiring logical reasoning
    - Comparative analysis
    
    Args:
        query: Complex query requiring reasoning
        model: 'sonar-reasoning' or 'sonar-reasoning-pro'
        search_context_size: Amount of context (defaults to 'high')
    
    Returns:
        Detailed reasoning-based answer with citations
    """
    try:
        headers = {
            "Authorization": f"Bearer {_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "search_context_size": search_context_size
        }
        
        async with _session.post(
            _base_url,
            headers=headers,
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                return f"Error: API returned status {response.status}: {error_text}"
            
            result = await response.json()
            
            content = result["choices"][0]["message"]["content"]
            citations = result.get("citations", [])
            
            formatted_response = f"Reasoning Analysis:\n{content}\n\n"
            if citations:
                formatted_response += "Sources:\n"
                for i, citation in enumerate(citations, 1):
                    formatted_response += f"{i}. {citation}\n"
            
            # Include token usage for reasoning models
            usage = result.get("usage", {})
            if usage:
                formatted_response += f"\nTokens used: {usage.get('total_tokens', 'N/A')}"
                cost = usage.get("cost", {})
                if cost:
                    formatted_response += f" (Cost: ${cost.get('total_cost', 0):.4f})"
            
            return formatted_response
            
    except Exception as e:
        return f"Error with reasoning search: {str(e)}"

# ============================================
# Resources
# ============================================

@mcp.resource("perplexity://models")
async def list_models() -> str:
    """List available Perplexity models and their capabilities"""
    
    models_info = """Available Perplexity Models:

1. **sonar** - Fast, efficient web search
   - Best for: Quick searches, general questions
   - Context size: auto/low/medium/high
   - Cost: $0.005 per request

2. **sonar-pro** - Advanced web search
   - Best for: Complex queries, detailed research
   - Context size: auto/low/medium/high
   - Cost: Higher than sonar

3. **sonar-reasoning** - Multi-step reasoning
   - Best for: Complex analysis, logical problems
   - Context size: auto/low/medium/high
   - Cost: Higher token-based pricing

4. **sonar-reasoning-pro** - Advanced reasoning
   - Best for: Most complex analytical tasks
   - Context size: auto/low/medium/high
   - Cost: Highest tier pricing

Search Filters:
- search_recency_filter: day, week, month, year
- search_domain_filter: Limit to specific domains
- search_context_size: Control search depth
"""
    return models_info

@mcp.resource("perplexity://prompting-guide")
async def prompting_guide() -> str:
    """Best practices for prompting Perplexity models"""
    
    guide = """Perplexity Prompting Best Practices:

1. **Be Specific**
   - Good: "What are the latest Python 3.12 performance improvements?"
   - Bad: "Tell me about Python"

2. **Use Natural Language**
   - Write queries as you would ask a knowledgeable friend
   - No need for special formatting

3. **Specify Time Frames**
   - Use search_recency for current events
   - Include dates in queries when relevant

4. **Domain Filtering**
   - Use search_domain for authoritative sources
   - Academic filter for research papers

5. **Context Size**
   - 'low': Quick answers (fastest)
   - 'medium': Balanced detail
   - 'high': Comprehensive research
   - 'auto': Let model decide

6. **Reasoning Models**
   - Use for multi-step problems
   - Great for comparisons
   - Best for "why" and "how" questions

Remember: System prompts don't affect search behavior
"""
    return guide

# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    import sys
    
    # Check for transport argument
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        # SSE mode for remote deployment
        import uvicorn
        from mcp.server.sse import SseServerTransport
        
        transport = SseServerTransport()
        app = transport.get_asgi_app(
            mcp,
            lifespan=mcp.lifespan,
            title="Perplexity Sonar MCP Server",
            description="Access Perplexity's web-grounded AI through MCP"
        )
        
        port = int(os.getenv("PORT", 8000))
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Default to stdio for local use
        mcp.run()