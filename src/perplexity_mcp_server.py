#!/usr/bin/env python3
"""
Perplexity MCP Server
A comprehensive MCP server for Perplexity's Sonar API with full feature support
"""

import asyncio
import sys
import json
import os
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ServerCapabilities
import mcp.server.stdio

# Initialize the MCP server
server = Server("perplexity-sonar")

# Load environment variables
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

class PerplexityClient:
    """Client for interacting with Perplexity API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make an async request to Perplexity API"""
        # Log the request details to stderr for debugging
        print(f"🚀 Sending Perplexity API Request:", file=sys.stderr)
        print(f"   Model: {payload.get('model', 'N/A')}", file=sys.stderr)
        if payload.get('search_mode'):
            print(f"   🎓 Search Mode: {payload.get('search_mode')}", file=sys.stderr)
        if payload.get('web_search_options'):
            print(f"   Web Options: {payload.get('web_search_options')}", file=sys.stderr)
        if payload.get('search_domain_filter'):
            print(f"   Domain Filter: {payload.get('search_domain_filter')}", file=sys.stderr)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(PERPLEXITY_API_URL, json=payload, headers=self.headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ API Response received successfully", file=sys.stderr)
                    return result
                else:
                    error_text = await response.text()
                    print(f"❌ API Error: Status {response.status}", file=sys.stderr)
                    return {"error": f"API request failed with status {response.status}: {error_text}"}
    
    def format_response(self, response: Dict[str, Any], request_info: Dict[str, Any] = None) -> str:
        """Format the API response for display with request details"""
        if "error" in response:
            return f"Error: {response['error']}"
        
        try:
            # Start with request details if provided
            output = ""
            if request_info:
                output += "📋 **Request Details:**\n"
                output += f"• Model: {request_info.get('model', 'N/A')}\n"
                
                # Show search mode if academic
                if request_info.get('search_mode') == 'academic':
                    output += "• 🎓 **ACADEMIC SEARCH MODE ACTIVE**\n"
                
                # Show search context size
                if 'web_search_options' in request_info:
                    context_size = request_info['web_search_options'].get('search_context_size', 'default')
                    output += f"• Search Context Size: {context_size}\n"
                
                # Show domain filter if present
                if request_info.get('search_domain_filter'):
                    output += f"• Domain Filter: {request_info['search_domain_filter']}\n"
                
                # Show date filter if present
                if request_info.get('search_after_date_filter'):
                    output += f"• Date Filter: After {request_info['search_after_date_filter']}\n"
                
                output += "\n---\n\n"
            
            # Add the actual response content
            content = response["choices"][0]["message"]["content"]
            output += content
            
            # Add citations if available
            citations = response.get("citations", [])
            if citations:
                output += "\n\n**Citations:**\n"
                for i, citation in enumerate(citations, 1):
                    output += f"{i}. {citation}\n"
            
            # Add search results summary if available
            search_results = response.get("search_results", [])
            if search_results and len(search_results) > 0:
                output += "\n**Sources consulted:**\n"
                for result in search_results[:5]:  # Show top 5 sources
                    title = result.get("title", "Unknown")
                    url = result.get("url", "")
                    # Check if it's from an academic source
                    if any(domain in url.lower() for domain in ['.edu', 'scholar', 'academic', 'journal', 'pubmed', 'arxiv', 'doi.org']):
                        output += f"- 🎓 {title}: {url}\n"
                    else:
                        output += f"- {title}: {url}\n"
            
            # Add usage/cost information if available
            usage = response.get("usage", {})
            if usage:
                cost = usage.get("cost", {})
                if cost:
                    output += f"\n**Usage Info:**\n"
                    output += f"• Total tokens: {usage.get('total_tokens', 'N/A')}\n"
                    output += f"• Search context: {usage.get('search_context_size', 'N/A')}\n"
                    output += f"• Total cost: ${cost.get('total_cost', 0):.3f}\n"
            
            return output
        except Exception as e:
            return f"Error formatting response: {str(e)}"

# Initialize the client
client = None

def validate_model(model: str) -> bool:
    """Validate if the model is supported"""
    valid_models = ["sonar", "sonar-pro", "sonar-reasoning", "sonar-reasoning-pro", "sonar-deep-research"]
    return model in valid_models

def validate_search_context_size(size: str) -> bool:
    """Validate search context size"""
    return size in ["low", "medium", "high"]

def validate_search_mode(mode: str) -> bool:
    """Validate search mode"""
    return mode in ["", "academic"]

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_web",
            description="""Perform a web search using Perplexity's Sonar models.
            
This is the primary tool for searching the internet and getting real-time information.
The search will automatically include citations and sources.

Available models:
- sonar: Fast, cost-effective search
- sonar-pro: Enhanced search with better comprehension
- sonar-reasoning: Detailed reasoning with search
- sonar-reasoning-pro: Advanced reasoning capabilities

Examples:
- "What are the latest AI developments?"
- "Explain quantum computing"
- "Current stock market trends"
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or question"
                    },
                    "model": {
                        "type": "string",
                        "description": "Model to use: sonar, sonar-pro, sonar-reasoning, sonar-reasoning-pro",
                        "default": "sonar"
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "Optional system prompt to guide the response",
                        "default": ""
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_web_advanced",
            description="""Perform an advanced web search with filtering options.
            
This tool provides fine-grained control over search parameters including:
- Domain filtering (allowlist or denylist)
- Academic search mode
- Search context size control
- Date filtering

Use this for specialized searches requiring specific sources or constraints.

Examples:
- Academic research from specific journals
- News from trusted sources only
- Technical documentation excluding certain sites
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or question"
                    },
                    "model": {
                        "type": "string",
                        "description": "Model to use: sonar, sonar-pro, sonar-reasoning, sonar-reasoning-pro",
                        "default": "sonar"
                    },
                    "search_mode": {
                        "type": "string",
                        "description": "Search mode: 'academic' for scholarly sources, or empty for general",
                        "default": ""
                    },
                    "search_context_size": {
                        "type": "string",
                        "description": "Context size: low, medium, high (affects cost and comprehensiveness)",
                        "default": "medium"
                    },
                    "domain_filter": {
                        "type": "array",
                        "description": "List of domains to include or exclude (prefix with - to exclude)",
                        "items": {"type": "string"},
                        "default": []
                    },
                    "search_after_date": {
                        "type": "string",
                        "description": "Optional date filter (format: MM/DD/YYYY)",
                        "default": ""
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="analyze_image_base64",
            description="""Analyze an image by providing it as base64 encoded data.
            
This tool can analyze images you have locally by encoding them in base64.
Supports PNG, JPEG, WEBP, and GIF formats up to 50MB.

The tool can:
- Describe image contents
- Extract text from images
- Answer questions about visual content
- Interpret diagrams and charts

Note: You need to provide the image already encoded in base64.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Question about the image"
                    },
                    "image_base64": {
                        "type": "string",
                        "description": "Base64 encoded image data (without data URI prefix)"
                    },
                    "image_type": {
                        "type": "string",
                        "description": "Image MIME type: image/png, image/jpeg, image/webp, image/gif",
                        "default": "image/png"
                    },
                    "model": {
                        "type": "string",
                        "description": "Model to use: sonar-pro recommended for images",
                        "default": "sonar-pro"
                    }
                },
                "required": ["question", "image_base64"]
            }
        ),
        Tool(
            name="analyze_image_url",
            description="""Analyze an image from a public URL.
            
This tool can analyze images hosted online by fetching them from a URL.
The URL must be publicly accessible.

The tool can:
- Describe image contents
- Extract text from images
- Answer questions about visual content
- Interpret diagrams and charts

Example URLs:
- https://example.com/image.png
- Public image hosting services
- Wikipedia images
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Question about the image"
                    },
                    "image_url": {
                        "type": "string",
                        "description": "Public URL of the image"
                    },
                    "model": {
                        "type": "string",
                        "description": "Model to use: sonar-pro recommended for images",
                        "default": "sonar-pro"
                    }
                },
                "required": ["question", "image_url"]
            }
        ),
        Tool(
            name="analyze_pdf",
            description="""Analyze a PDF document from a URL.
            
This tool can process PDF documents and answer questions about their content.
The PDF must be accessible via a public URL.

Capabilities:
- Document summarization
- Question answering about content
- Key information extraction
- Multi-language support

Use cases:
- Research paper analysis
- Contract review
- Technical documentation
- Report summarization
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Question about the PDF content"
                    },
                    "pdf_url": {
                        "type": "string",
                        "description": "Public URL of the PDF document"
                    },
                    "model": {
                        "type": "string",
                        "description": "Model to use: sonar-pro recommended for documents",
                        "default": "sonar-pro"
                    },
                    "include_web_search": {
                        "type": "boolean",
                        "description": "Include web search for additional context",
                        "default": False
                    }
                },
                "required": ["question", "pdf_url"]
            }
        ),
        Tool(
            name="search_academic",
            description="""Perform a search specifically targeting academic and scholarly sources.
            
This tool focuses on peer-reviewed papers, journal articles, and research publications.
Ideal for academic research, literature reviews, and evidence-based information.

Benefits:
- Filters out non-academic sources
- Prioritizes peer-reviewed content
- Returns research-grade information
- Includes proper academic citations

Use for:
- Literature reviews
- Scientific research
- Academic writing support
- Evidence-based queries
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Academic search query"
                    },
                    "model": {
                        "type": "string",
                        "description": "Model to use: sonar-pro or sonar-deep-research recommended",
                        "default": "sonar-pro"
                    },
                    "search_context_size": {
                        "type": "string",
                        "description": "Context size: low, medium, high",
                        "default": "high"
                    },
                    "after_date": {
                        "type": "string",
                        "description": "Optional date filter for recent research (MM/DD/YYYY)",
                        "default": ""
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="explain_capabilities",
            description="Get detailed information about this MCP server's capabilities and Perplexity API features",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    global client
    if not client and PERPLEXITY_API_KEY:
        client = PerplexityClient(PERPLEXITY_API_KEY)
    
    if not client:
        return [TextContent(
            type="text",
            text="Error: PERPLEXITY_API_KEY environment variable not set. Please configure your API key."
        )]
    
    try:
        if name == "search_web":
            query = arguments.get("query", "")
            model = arguments.get("model", "sonar")
            system_prompt = arguments.get("system_prompt", "")
            
            if not query:
                return [TextContent(type="text", text="Error: Query is required")]
            
            if not validate_model(model):
                return [TextContent(type="text", text=f"Error: Invalid model '{model}'")]
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": query})
            
            payload = {
                "model": model,
                "messages": messages
            }
            
            response = await client.make_request(payload)
            formatted = client.format_response(response, payload)
            
            return [TextContent(type="text", text=formatted)]
        
        elif name == "search_web_advanced":
            query = arguments.get("query", "")
            model = arguments.get("model", "sonar")
            search_mode = arguments.get("search_mode", "")
            search_context_size = arguments.get("search_context_size", "medium")
            domain_filter = arguments.get("domain_filter", [])
            search_after_date = arguments.get("search_after_date", "")
            
            if not query:
                return [TextContent(type="text", text="Error: Query is required")]
            
            if not validate_model(model):
                return [TextContent(type="text", text=f"Error: Invalid model '{model}'")]
            
            if not validate_search_context_size(search_context_size):
                return [TextContent(type="text", text=f"Error: Invalid search_context_size '{search_context_size}'")]
            
            if not validate_search_mode(search_mode):
                return [TextContent(type="text", text=f"Error: Invalid search_mode '{search_mode}'")]
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": query}],
                "web_search_options": {
                    "search_context_size": search_context_size
                }
            }
            
            if search_mode == "academic":
                payload["search_mode"] = "academic"
            
            if domain_filter and len(domain_filter) > 0:
                payload["search_domain_filter"] = domain_filter[:20]  # Max 20 domains
            
            if search_after_date:
                payload["search_after_date_filter"] = search_after_date
            
            response = await client.make_request(payload)
            formatted = client.format_response(response, payload)
            
            return [TextContent(type="text", text=formatted)]
        
        elif name == "analyze_image_base64":
            question = arguments.get("question", "")
            image_base64 = arguments.get("image_base64", "")
            image_type = arguments.get("image_type", "image/png")
            model = arguments.get("model", "sonar-pro")
            
            if not question:
                return [TextContent(type="text", text="Error: Question is required")]
            
            if not image_base64:
                return [TextContent(type="text", text="Error: Base64 image data is required")]
            
            if not validate_model(model):
                return [TextContent(type="text", text=f"Error: Invalid model '{model}'")]
            
            # Create data URI
            data_uri = f"data:{image_type};base64,{image_base64}"
            
            payload = {
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {"type": "image_url", "image_url": {"url": data_uri}}
                    ]
                }]
            }
            
            response = await client.make_request(payload)
            formatted = client.format_response(response, payload)
            
            return [TextContent(type="text", text=formatted)]
        
        elif name == "analyze_image_url":
            question = arguments.get("question", "")
            image_url = arguments.get("image_url", "")
            model = arguments.get("model", "sonar-pro")
            
            if not question:
                return [TextContent(type="text", text="Error: Question is required")]
            
            if not image_url:
                return [TextContent(type="text", text="Error: Image URL is required")]
            
            if not validate_model(model):
                return [TextContent(type="text", text=f"Error: Invalid model '{model}'")]
            
            payload = {
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }]
            }
            
            response = await client.make_request(payload)
            formatted = client.format_response(response, payload)
            
            return [TextContent(type="text", text=formatted)]
        
        elif name == "analyze_pdf":
            question = arguments.get("question", "")
            pdf_url = arguments.get("pdf_url", "")
            model = arguments.get("model", "sonar-pro")
            include_web_search = arguments.get("include_web_search", False)
            
            if not question:
                return [TextContent(type="text", text="Error: Question is required")]
            
            if not pdf_url:
                return [TextContent(type="text", text="Error: PDF URL is required")]
            
            if not validate_model(model):
                return [TextContent(type="text", text=f"Error: Invalid model '{model}'")]
            
            payload = {
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {"type": "file_url", "file_url": {"url": pdf_url}}
                    ]
                }]
            }
            
            if include_web_search:
                payload["web_search_options"] = {"search_type": "pro"}
            
            response = await client.make_request(payload)
            formatted = client.format_response(response, payload)
            
            return [TextContent(type="text", text=formatted)]
        
        elif name == "search_academic":
            query = arguments.get("query", "")
            model = arguments.get("model", "sonar-pro")
            search_context_size = arguments.get("search_context_size", "high")
            after_date = arguments.get("after_date", "")
            
            if not query:
                return [TextContent(type="text", text="Error: Query is required")]
            
            if not validate_model(model):
                return [TextContent(type="text", text=f"Error: Invalid model '{model}'")]
            
            if not validate_search_context_size(search_context_size):
                return [TextContent(type="text", text=f"Error: Invalid search_context_size '{search_context_size}'")]
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": query}],
                "search_mode": "academic",
                "web_search_options": {
                    "search_context_size": search_context_size
                }
            }
            
            if after_date:
                payload["search_after_date_filter"] = after_date
            
            response = await client.make_request(payload)
            formatted = client.format_response(response, payload)
            
            return [TextContent(type="text", text=formatted)]
        
        elif name == "explain_capabilities":
            explanation = """🚀 **Perplexity MCP Server Capabilities**

This MCP server provides comprehensive access to Perplexity's Sonar API, enabling:

**🔍 Web Search**
- Real-time internet search with citations
- Multiple models: sonar, sonar-pro, sonar-reasoning, sonar-reasoning-pro
- Advanced filtering: domain lists, academic mode, date ranges
- Adjustable search depth (low/medium/high context)

**🖼️ Multimodal Analysis**
- Image analysis from base64 or URLs
- PDF document processing
- Visual question answering
- Text extraction from images

**🎓 Academic Research**
- Dedicated academic search mode
- Peer-reviewed source prioritization
- Scholarly citations and references
- Research paper analysis

**⚙️ Configuration Options**
- Model selection for different use cases
- Search context size control (affects cost/quality)
- Domain filtering (allowlist/denylist up to 20 domains)
- Date filtering for recent information

**💡 Use Cases**
- Real-time information retrieval
- Research and fact-checking
- Document and image analysis
- Academic literature reviews
- Multi-source information synthesis

**🔐 Security**
- API key stored in environment variables
- Input validation on all parameters
- Secure HTTPS communication
- No data persistence

Configure your API key as PERPLEXITY_API_KEY environment variable to get started!
"""
            return [TextContent(type="text", text=explanation)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing tool: {str(e)}")]

async def main():
    """Run the server"""
    # Check for API key
    if not PERPLEXITY_API_KEY:
        print("Warning: PERPLEXITY_API_KEY environment variable not set", file=sys.stderr)
        print("Please set your API key to use this MCP server", file=sys.stderr)
    
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="perplexity-sonar",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    tools={}
                )
            )
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)