"""
Perplexity Sonar MCP Server (Robust FastMCP Implementation)
An MCP server that provides access to Perplexity's Sonar API with enhanced error handling
"""

from mcp.server.fastmcp import FastMCP
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from typing import Optional
import aiohttp
import os
import sys
import json
import asyncio

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
        # Log to stderr, not stdout
        print("ERROR: PERPLEXITY_API_KEY not found", file=sys.stderr)
        raise ValueError("PERPLEXITY_API_KEY environment variable is required")
    
    # Create HTTP session with timeout
    timeout = aiohttp.ClientTimeout(total=30)
    _session = aiohttp.ClientSession(timeout=timeout)
    
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
# Helper Functions
# ============================================
def sanitize_response(text: str) -> str:
    """Sanitize response text to prevent JSON issues"""
    if not text:
        return ""
    # Remove any null bytes or control characters
    text = text.replace('\x00', '')
    # Ensure the text is properly escaped for JSON
    return text

async def make_perplexity_request(payload: dict, timeout: int = 25) -> dict:
    """Make a request to Perplexity API with error handling"""
    try:
        headers = {
            "Authorization": f"Bearer {_api_key}",
            "Content-Type": "application/json"
        }
        
        # Use a specific timeout for this request
        async with _session.post(
            _base_url,
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                return {
                    "error": True,
                    "status": response.status,
                    "message": f"API error {response.status}: {error_text[:200]}"
                }
    except asyncio.TimeoutError:
        return {
            "error": True,
            "message": "Request timed out. Please try again with a simpler query."
        }
    except Exception as e:
        return {
            "error": True,
            "message": f"Connection error: {str(e)[:200]}"
        }

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
        # Validate model
        valid_models = ["sonar", "sonar-pro", "sonar-reasoning", "sonar-reasoning-pro"]
        if model not in valid_models:
            model = "sonar"
        
        # Build request payload
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": query[:4000]  # Limit query length
                }
            ],
            "search_context_size": search_context_size
        }
        
        # Add optional parameters
        if search_recency:
            payload["search_recency_filter"] = search_recency
        
        if search_domain:
            domains = search_domain.split(",")[:10]  # Limit to 10 domains
            payload["search_domain_filter"] = domains
        
        # Make API request
        result = await make_perplexity_request(payload)
        
        if result.get("error"):
            return f"Error: {result.get('message', 'Unknown error')}"
        
        # Format response with citations
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "No response")
        content = sanitize_response(content)
        
        citations = result.get("citations", [])
        
        formatted_response = f"{content}\n\n"
        if citations:
            formatted_response += "Sources:\n"
            for i, citation in enumerate(citations[:10], 1):  # Limit citations
                formatted_response += f"{i}. {sanitize_response(str(citation))}\n"
        
        return formatted_response[:8000]  # Limit total response length
        
    except Exception as e:
        error_msg = f"Error searching web: {str(e)[:200]}"
        print(error_msg, file=sys.stderr)
        return error_msg

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
        # Validate model
        valid_models = ["sonar", "sonar-pro", "sonar-reasoning", "sonar-reasoning-pro"]
        if model not in valid_models:
            model = "sonar"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": query[:4000]  # Limit query length
                }
            ],
            "search_mode": "academic",  # Enable academic filtering
            "search_context_size": search_context_size
        }
        
        if search_recency:
            payload["search_recency_filter"] = search_recency
        
        # Make API request
        result = await make_perplexity_request(payload)
        
        if result.get("error"):
            return f"Error: {result.get('message', 'Unknown error')}"
        
        # Format response
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "No response")
        content = sanitize_response(content)
        
        citations = result.get("citations", [])
        
        formatted_response = f"🎓 **Academic Search Results:**\n\n{content}\n\n"
        if citations:
            formatted_response += "Academic Sources:\n"
            for i, citation in enumerate(citations[:10], 1):
                formatted_response += f"{i}. {sanitize_response(str(citation))}\n"
        
        return formatted_response[:8000]
        
    except Exception as e:
        error_msg = f"Error searching academic sources: {str(e)[:200]}"
        print(error_msg, file=sys.stderr)
        return error_msg

@mcp.tool()
async def quick_search(query: str) -> str:
    """Quick web search with minimal latency using the fastest model.
    
    Args:
        query: The search query (keep it concise for best results)
    
    Returns:
        Quick AI-generated answer
    """
    try:
        payload = {
            "model": "sonar",  # Use fastest model
            "messages": [
                {
                    "role": "user",
                    "content": query[:500]  # Shorter query for speed
                }
            ],
            "search_context_size": "low"  # Minimal context for speed
        }
        
        # Make API request with shorter timeout
        result = await make_perplexity_request(payload, timeout=15)
        
        if result.get("error"):
            return f"Error: {result.get('message', 'Search failed')}"
        
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "No response")
        return sanitize_response(content)[:2000]  # Shorter response
        
    except Exception as e:
        return f"Quick search failed: {str(e)[:100]}"

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
        try:
            mcp.run()
        except Exception as e:
            # Log errors to stderr, not stdout
            print(f"Server error: {e}", file=sys.stderr)
            sys.exit(1)