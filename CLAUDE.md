# CLAUDE.md

This file provides context and guidance for AI assistants (particularly Claude) when working with this repository.

## Repository Purpose

This is a Model Context Protocol (MCP) server implementation that bridges Perplexity's Sonar API with Claude Code, enabling real-time web search, academic research, and document analysis capabilities within AI sessions.

## Key Components

### Core Server Implementation
- **src/perplexity_mcp_server.py**: Main MCP server using FastMCP framework
  - Implements stdio transport for local communication
  - Provides 7 tools: search_web, search_web_advanced, search_academic, analyze_image_base64, analyze_image_url, analyze_pdf, explain_capabilities
  - Enhanced feedback system showing request details and active modes

### Configuration
- **config/.env.example**: Template for API key configuration
- **requirements.txt**: Python dependencies (fastmcp, httpx, python-dotenv)

### Scripts
- **scripts/run_perplexity_mcp.sh**: Unix wrapper for virtual environment activation
- **scripts/run_perplexity_mcp.bat**: Windows wrapper script

## Important Implementation Details

### Virtual Environment Management
The server requires a Python virtual environment named `mcp_venv` to isolate dependencies. The wrapper scripts handle activation automatically.

### Enhanced Feedback System
The server provides detailed feedback for each request:
```python
def format_response(self, response: Dict[str, Any], request_info: Dict[str, Any] = None) -> str:
    # Shows request parameters, active modes (e.g., "🎓 ACADEMIC SEARCH MODE ACTIVE")
    # Displays token usage and cost information
    # Includes citations with sources
```

### Academic Search Mode
When using search_academic or setting academic filter, the server:
1. Adds "search_mode": "academic" to request info
2. Displays prominent "🎓 ACADEMIC SEARCH MODE ACTIVE" banner
3. Focuses on scholarly sources and peer-reviewed content

### Error Handling
- Validates API key presence
- Handles rate limiting gracefully
- Provides clear error messages for debugging
- Logs detailed information for troubleshooting

## Common Tasks and Solutions

### Setting Up the Server
1. Create virtual environment: `python3 -m venv mcp_venv`
2. Install dependencies: `pip install -r requirements.txt`
3. Configure API key in `.env` file
4. Make scripts executable: `chmod +x scripts/*.sh`
5. Test with: `python src/perplexity_mcp_server.py`

### Integrating with Claude Code
1. Copy MCP configuration to `~/.claude/mcp_config.json`
2. Update paths in configuration to match local installation
3. Add shell aliases for convenience
4. Launch with: `claude --mcp-config ~/.claude/mcp_config.json`

### Debugging Issues
- Check virtual environment activation
- Verify API key configuration
- Ensure script permissions (executable)
- Review server logs for detailed errors
- Test server independently before Claude integration

## API Integration Notes

### Perplexity Sonar API
- Endpoint: `https://api.perplexity.ai/chat/completions`
- Authentication: Bearer token in Authorization header
- Models: sonar, sonar-pro, sonar-reasoning, sonar-reasoning-pro
- Supports: streaming, search filters, context control, multimodal inputs

### Search Context Sizes
- `low`: ~5 web sources
- `medium`: ~10 web sources
- `high`: ~20 web sources
- `auto`: Dynamically determined

### Cost Tracking
Each response includes token usage and estimated cost based on model pricing.

## Best Practices

### When Modifying the Server
1. Maintain backward compatibility with existing tools
2. Preserve the enhanced feedback system
3. Keep error messages user-friendly
4. Document any new environment variables
5. Update wrapper scripts for both platforms

### When Adding New Tools
1. Follow the existing tool pattern using @server.tool() decorator
2. Provide clear, LLM-friendly descriptions
3. Include request info in responses for transparency
4. Handle errors gracefully with informative messages
5. Update the explain_capabilities tool

### Security Considerations
- Never commit API keys to the repository
- Use .env files for sensitive configuration
- Validate and sanitize user inputs
- Be cautious with file system operations
- Respect rate limits and API quotas

## Platform-Specific Notes

### macOS
- Uses zsh by default, aliases go in ~/.zshrc
- Virtual environment activation: `source mcp_venv/bin/activate`
- File paths use forward slashes

### Windows
- Uses PowerShell or Command Prompt
- Virtual environment activation: `.\mcp_venv\Scripts\Activate`
- Requires batch file wrappers
- File paths may need conversion

### Linux
- Shell varies (bash, zsh, etc.)
- Similar to macOS setup
- May require additional Python packages via apt/yum

## Testing Recommendations

1. Test server standalone before Claude integration
2. Verify each tool works independently
3. Check academic mode feedback is visible
4. Confirm cost tracking is accurate
5. Validate error handling for missing API keys
6. Test with different Sonar models
7. Verify citations are properly formatted

## Support Resources

- Perplexity API Documentation: https://docs.perplexity.ai
- MCP Specification: https://modelcontextprotocol.io
- FastMCP Documentation: https://github.com/jlowin/fastmcp
- Claude Code Documentation: https://claude.ai/code

## Version Information

- Python: 3.8+
- FastMCP: Latest stable
- MCP Protocol: 1.0
- Perplexity API: v1

This repository is designed to be a comprehensive reference implementation for building production-ready MCP servers that integrate external APIs with Claude Code.