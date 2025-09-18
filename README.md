# Perplexity MCP Server for Claude Code

A complete Model Context Protocol (MCP) server that integrates Perplexity's Sonar API with Claude Code, enabling powerful web search, academic research, and document analysis capabilities directly within your AI sessions.

## 🎯 What This Does

This MCP server allows Claude Code to:
- 🔍 Search the web in real-time using Perplexity's Sonar models
- 📚 Search academic papers and scholarly sources
- 🖼️ Analyze images from URLs or base64 encoded data
- 📄 Analyze PDF documents from URLs
- 🎯 Filter searches by domain (include/exclude specific sites)
- 📊 Control search context size for efficiency

## 📋 Prerequisites

Before you begin, you'll need:
1. **Claude Code** installed on your computer (get it from [claude.ai/code](https://claude.ai/code))
2. **Python 3.8 or higher** installed
3. **A Perplexity API key** (get one from [perplexity.ai/settings/api](https://perplexity.ai/settings/api))
4. **A terminal/command line** application

## 🚀 Step-by-Step Installation Guide

### For Mac Users

#### Step 1: Download the Repository
```bash
# Open Terminal (press Cmd+Space, type "Terminal", press Enter)
# Navigate to your Desktop
cd ~/Desktop

# Clone this repository
git clone https://github.com/YOUR_USERNAME/perplexity-mcp-server.git

# Enter the directory
cd perplexity-mcp-server
```

#### Step 2: Set Up Python Environment
```bash
# Create a virtual environment (this keeps everything contained)
python3 -m venv mcp_venv

# Activate the virtual environment
source mcp_venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

#### Step 3: Configure Your API Key
```bash
# Copy the example configuration
cp config/.env.example .env

# Open the .env file in a text editor
nano .env
# (or use any text editor you prefer)

# Add your Perplexity API key:
# PERPLEXITY_API_KEY=your-actual-api-key-here
# Save and exit (in nano: Ctrl+X, then Y, then Enter)
```

#### Step 4: Make Scripts Executable
```bash
# Make the wrapper script executable
chmod +x scripts/run_perplexity_mcp.sh

# Make the server executable
chmod +x src/perplexity_mcp_server.py
```

#### Step 5: Set Up Claude Code Integration
```bash
# Create Claude configuration directory
mkdir -p ~/.claude

# Create MCP configuration file
cat > ~/.claude/mcp_config.json << EOF
{
  "mcpServers": {
    "perplexity": {
      "command": "$(pwd)/scripts/run_perplexity_mcp.sh",
      "args": [],
      "env": {}
    }
  }
}
EOF
```

#### Step 6: Add Convenient Aliases
```bash
# Add aliases to your shell configuration
echo '# Claude MCP aliases' >> ~/.zshrc
echo 'alias claude-mcp="claude --mcp-config ~/.claude/mcp_config.json"' >> ~/.zshrc
echo 'alias cmcp="claude --mcp-config ~/.claude/mcp_config.json"  # Short version' >> ~/.zshrc

# Reload your shell configuration
source ~/.zshrc
```

#### Step 7: Test Your Setup
```bash
# Test the MCP server directly
python src/perplexity_mcp_server.py

# You should see:
# Starting Perplexity MCP Server...
# Press Ctrl+C to see if it stops cleanly

# Now test with Claude Code
cmcp
# In Claude Code, type: "Use the perplexity search_web tool to find the latest AI news"
```

### For Windows Users

#### Step 1: Download the Repository
```powershell
# Open PowerShell (press Win+X, select "Windows PowerShell")
# Navigate to your Desktop
cd ~/Desktop

# Clone this repository
git clone https://github.com/YOUR_USERNAME/perplexity-mcp-server.git

# Enter the directory
cd perplexity-mcp-server
```

#### Step 2: Set Up Python Environment
```powershell
# Create a virtual environment
python -m venv mcp_venv

# Activate the virtual environment
.\mcp_venv\Scripts\Activate

# Install required packages
pip install -r requirements.txt
```

#### Step 3: Configure Your API Key
```powershell
# Copy the example configuration
copy config\.env.example .env

# Open the .env file in Notepad
notepad .env

# Add your Perplexity API key:
# PERPLEXITY_API_KEY=your-actual-api-key-here
# Save and close Notepad
```

#### Step 4: Create Windows Wrapper Script
```powershell
# Create a batch file for Windows
@"
@echo off
call "$(Get-Location)\mcp_venv\Scripts\activate"
python "$(Get-Location)\src\perplexity_mcp_server.py"
"@ | Out-File -FilePath scripts\run_perplexity_mcp.bat -Encoding ASCII
```

#### Step 5: Set Up Claude Code Integration
```powershell
# Create Claude configuration directory
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude"

# Create MCP configuration
$currentPath = (Get-Location).Path.Replace('\', '/')
$config = @"
{
  "mcpServers": {
    "perplexity": {
      "command": "$currentPath/scripts/run_perplexity_mcp.bat",
      "args": [],
      "env": {}
    }
  }
}
"@
$config | Out-File -FilePath "$env:USERPROFILE\.claude\mcp_config.json" -Encoding UTF8
```

#### Step 6: Test Your Setup
```powershell
# Test the MCP server directly
python src\perplexity_mcp_server.py

# You should see:
# Starting Perplexity MCP Server...
# Press Ctrl+C to stop

# Now test with Claude Code
claude --mcp-config "$env:USERPROFILE\.claude\mcp_config.json"
# In Claude Code, type: "Use the perplexity search_web tool to find the latest AI news"
```

### For Linux Users

#### Step 1: Download the Repository
```bash
# Open Terminal
# Navigate to your home directory
cd ~

# Clone this repository
git clone https://github.com/YOUR_USERNAME/perplexity-mcp-server.git

# Enter the directory
cd perplexity-mcp-server
```

#### Step 2: Set Up Python Environment
```bash
# Ensure Python 3 and pip are installed
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Create a virtual environment
python3 -m venv mcp_venv

# Activate the virtual environment
source mcp_venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

#### Step 3: Configure Your API Key
```bash
# Copy the example configuration
cp config/.env.example .env

# Open the .env file in your preferred editor
nano .env
# or: vim .env
# or: gedit .env

# Add your Perplexity API key:
# PERPLEXITY_API_KEY=your-actual-api-key-here
# Save and exit
```

#### Step 4: Make Scripts Executable
```bash
# Make the wrapper script executable
chmod +x scripts/run_perplexity_mcp.sh

# Make the server executable
chmod +x src/perplexity_mcp_server.py
```

#### Step 5: Set Up Claude Code Integration
```bash
# Create Claude configuration directory
mkdir -p ~/.claude

# Create MCP configuration file
cat > ~/.claude/mcp_config.json << EOF
{
  "mcpServers": {
    "perplexity": {
      "command": "$(pwd)/scripts/run_perplexity_mcp.sh",
      "args": [],
      "env": {}
    }
  }
}
EOF
```

#### Step 6: Add Convenient Aliases
```bash
# Determine which shell you're using
echo $SHELL

# For bash users:
echo '# Claude MCP aliases' >> ~/.bashrc
echo 'alias claude-mcp="claude --mcp-config ~/.claude/mcp_config.json"' >> ~/.bashrc
echo 'alias cmcp="claude --mcp-config ~/.claude/mcp_config.json"' >> ~/.bashrc
source ~/.bashrc

# For zsh users:
echo '# Claude MCP aliases' >> ~/.zshrc
echo 'alias claude-mcp="claude --mcp-config ~/.claude/mcp_config.json"' >> ~/.zshrc
echo 'alias cmcp="claude --mcp-config ~/.claude/mcp_config.json"' >> ~/.zshrc
source ~/.zshrc
```

#### Step 7: Test Your Setup
```bash
# Test the MCP server directly
python3 src/perplexity_mcp_server.py

# You should see:
# Starting Perplexity MCP Server...
# Press Ctrl+C to stop

# Now test with Claude Code
cmcp
# In Claude Code, type: "Use the perplexity search_web tool to find the latest AI news"
```

## 📖 Usage Guide

### Starting Claude Code with MCP

Once installed, you have three ways to start Claude Code with the Perplexity MCP server:

1. **Using the short alias** (recommended):
   ```bash
   cmcp
   ```

2. **Using the full alias**:
   ```bash
   claude-mcp
   ```

3. **Using the direct command**:
   ```bash
   claude --mcp-config ~/.claude/mcp_config.json
   ```

### Available Commands in Claude Code

Once you're in a Claude Code session with MCP enabled, you can use these commands:

#### Basic Web Search
```
Use the perplexity search_web tool to find information about [your topic]
```

#### Academic Search
```
Use perplexity search_academic to find research papers about [your topic]
```

#### Advanced Search with Filters
```
Use perplexity search_web_advanced to search for [topic] excluding reddit.com and including only results from the last week
```

#### Analyze an Image
```
Use perplexity analyze_image_url to analyze this image: [URL]
```

#### Analyze a PDF
```
Use perplexity analyze_pdf to summarize this document: [PDF URL]
```

#### Get Help
```
Use perplexity explain_capabilities to show all available features
```

### Examples

#### Example 1: Research Latest Technology
```
cmcp
> Use perplexity to find the latest developments in quantum computing from the past month
```

#### Example 2: Academic Research
```
cmcp
> Use perplexity search_academic to find peer-reviewed papers about machine learning in healthcare
```

#### Example 3: Analyze Documentation
```
cmcp
> Use perplexity analyze_pdf to summarize the key points from https://example.com/whitepaper.pdf
```

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### "Command not found: claude"
- **Solution**: Make sure Claude Code is installed from [claude.ai/code](https://claude.ai/code)

#### "No module named 'fastmcp'"
- **Solution**: Activate your virtual environment and reinstall requirements:
  ```bash
  source mcp_venv/bin/activate  # Mac/Linux
  # or
  .\mcp_venv\Scripts\Activate  # Windows
  pip install -r requirements.txt
  ```

#### "401 Unauthorized" error
- **Solution**: Check your API key in the `.env` file is correct and has no extra spaces

#### "Permission denied" error
- **Solution**: Make the scripts executable:
  ```bash
  chmod +x scripts/run_perplexity_mcp.sh
  chmod +x src/perplexity_mcp_server.py
  ```

#### MCP server not connecting
- **Solution**: Test the server directly:
  ```bash
  cd ~/Desktop/perplexity-mcp-server
  source mcp_venv/bin/activate
  python src/perplexity_mcp_server.py
  ```

### Getting More Help

1. Check the [examples](examples/) directory for more usage examples
2. Open an issue on GitHub if you encounter problems

## 📊 Available Sonar Models

The MCP server supports all Perplexity Sonar models:

| Model | Description | Best For |
|-------|-------------|----------|
| `sonar` | Fast, cost-effective search | Quick queries, general information |
| `sonar-pro` | Enhanced comprehension | Complex topics, detailed research |
| `sonar-reasoning` | Step-by-step reasoning | Problem-solving, analysis |
| `sonar-reasoning-pro` | Advanced reasoning | Complex analysis, research |

## 🔧 Advanced Configuration

### Customizing Search Behavior

Edit `src/perplexity_mcp_server.py` to modify default settings:

```python
# Default model (line ~50)
DEFAULT_MODEL = "sonar"  # Change to "sonar-pro" for better quality

# Default search context (line ~51)
DEFAULT_SEARCH_CONTEXT = "auto"  # Options: "low", "medium", "high", "auto"

# Temperature for responses (line ~52)
DEFAULT_TEMPERATURE = 0.7  # Lower = more focused, Higher = more creative
```

### Adding Custom Tools

To add your own tools, edit `src/perplexity_mcp_server.py` and add a new method:

```python
@server.tool()
async def your_custom_tool(query: str) -> str:
    """Description of what your tool does"""
    # Your implementation here
    return result
```

## 📄 Project Structure

```
perplexity-mcp-server/
├── src/
│   └── perplexity_mcp_server.py    # Main MCP server implementation
├── scripts/
│   ├── run_perplexity_mcp.sh       # Mac/Linux wrapper script
│   └── run_perplexity_mcp.bat      # Windows wrapper script
├── config/
│   └── .env.example                 # Example environment configuration
├── examples/
│   └── test_server.py               # Test script for the server
├── setup/
│   └── install.sh                   # Automated installation script
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
└── CLAUDE.md                       # AI context file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Perplexity AI](https://perplexity.ai) for the Sonar API
- [Anthropic](https://anthropic.com) for Claude and the MCP protocol
- The FastMCP library for simplifying MCP server development

## 📞 Support

If you need help:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Look at the [examples](examples/) directory
3. Open an issue on GitHub

---

**Remember**: This tool gives Claude Code the ability to search the web and analyze documents in real-time. Use it responsibly and in accordance with Perplexity's terms of service.