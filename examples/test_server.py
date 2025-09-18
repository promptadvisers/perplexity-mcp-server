#!/usr/bin/env python3
"""
Test script for Perplexity MCP Server
Run this to verify the server is working correctly
"""

import json
import subprocess
import sys
import os

def test_server():
    """Test the MCP server with various commands"""
    
    print("🧪 Perplexity MCP Server Test Suite\n")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("⚠️  Warning: PERPLEXITY_API_KEY not set in environment")
        print("   The server will start but tools won't work without an API key")
        print("   Set it in .env file or export PERPLEXITY_API_KEY=your_key")
        print()
    else:
        print("✅ API key found in environment")
        print()
    
    # Test cases
    test_cases = [
        {
            "name": "Server Initialization",
            "request": {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"}
                },
                "id": 1
            }
        },
        {
            "name": "List Available Tools",
            "request": {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2
            }
        }
    ]
    
    # Add tool test only if API key is available
    if api_key:
        test_cases.append({
            "name": "Test Basic Search (requires API key)",
            "request": {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "search_web",
                    "arguments": {
                        "query": "What is MCP (Model Context Protocol)?",
                        "model": "sonar"
                    }
                },
                "id": 3
            }
        })
    
    # Path to the server script
    server_script = os.path.join(os.path.dirname(__file__), "perplexity_mcp_server.py")
    
    # Check if server script exists
    if not os.path.exists(server_script):
        print(f"❌ Error: Server script not found at {server_script}")
        return
    
    # Check if we're in virtual environment (recommended)
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not running in virtual environment")
        print("   It's recommended to activate the virtual environment first:")
        print("   source mcp_venv/bin/activate")
        print()
    
    # Run tests
    for i, test in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {test['name']}")
        print("-" * 40)
        
        try:
            # Start the server process
            cmd = [sys.executable, server_script]
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ}  # Include environment variables
            )
            
            # Send request
            request_str = json.dumps(test["request"]) + "\n"
            stdout, stderr = process.communicate(input=request_str, timeout=10)
            
            # Parse response
            if stdout:
                try:
                    # The server might output multiple JSON objects, try to parse the first valid one
                    for line in stdout.strip().split('\n'):
                        if line.strip():
                            response = json.loads(line)
                            
                            # Check for successful response
                            if "result" in response or "error" not in response:
                                print("✅ Success!")
                                
                                # Show summary of response
                                if test["name"] == "List Available Tools":
                                    if "result" in response:
                                        tools = response["result"]
                                        print(f"   Found {len(tools)} tools:")
                                        for tool in tools[:3]:  # Show first 3 tools
                                            print(f"   - {tool['name']}")
                                        if len(tools) > 3:
                                            print(f"   ... and {len(tools) - 3} more")
                                elif test["name"] == "Server Initialization":
                                    print(f"   Server: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
                                    print(f"   Version: {response.get('result', {}).get('serverInfo', {}).get('version', 'Unknown')}")
                            else:
                                print(f"⚠️  Response contains error: {response.get('error', 'Unknown error')}")
                            break
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse response: {e}")
                    print(f"   Raw output: {stdout[:200]}...")
            
            # Show any errors
            if stderr and stderr.strip():
                if "Warning:" in stderr:
                    print(f"⚠️  Warning: {stderr.strip()}")
                else:
                    print(f"❌ Error output: {stderr.strip()}")
            
        except subprocess.TimeoutExpired:
            print("❌ Test timed out")
            process.kill()
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Testing complete!")
    
    if not api_key:
        print("\n📝 Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your Perplexity API key")
        print("3. Run tests again to verify API connectivity")
    else:
        print("\n🎉 Server is ready to use with Claude Desktop!")
        print("Add the configuration from README.md to your Claude Desktop config.")

def main():
    """Main entry point"""
    # Try to load .env file if it exists
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        print("Loading environment from .env file...")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print()
    
    test_server()

if __name__ == "__main__":
    main()