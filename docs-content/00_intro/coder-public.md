# Local Development Environment Setup

## Overview: Setting Up Your Local Environment

For public access to the Agentic AI Nano-Degree, you'll need to set up your local development environment. While this requires more initial setup than a pre-configured cloud environment, it provides full control over your development setup and works with any LLM API provider.

## Local Setup Requirements

Before beginning the course modules, ensure you have:

1. **Python 3.11+** installed with pip and virtual environment support
2. **Git** for version control and cloning repositories  
3. **Code editor** (VS Code recommended with Python extension)
4. **LLM API access** (OpenAI, Anthropic Claude, or local models like Ollama)

## Local Environment Setup Guide

### 1. Python Environment

We recommend using Python 3.11 or higher with a virtual environment:

```bash
# Create virtual environment
python -m venv agentic-ai
source agentic-ai/bin/activate  # On Windows: agentic-ai\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Clone Repository

```bash
git clone https://github.com/fwornle/agentic-ai-nano.git
cd agentic-ai-nano
```

### 3. Install Dependencies

```bash
# Install core requirements (if available)
pip install -r requirements.txt

# For specific modules, install additional dependencies:
# Agent Frameworks
pip install -r docs-content/01_frameworks/src/session1/requirements.txt

# RAG Architecture  
pip install -r docs-content/02_rag/src/session1/requirements.txt

# MCP & Agent Protocols
pip install -r docs-content/03_mcp-acp-a2a/src/session1/requirements.txt
```

### 4. API Keys Setup

Create a `.env` file in the project root:

```bash
# OpenAI (required for most examples)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Other LLM providers
ANTHROPIC_API_KEY=your_anthropic_key_here
COHERE_API_KEY=your_cohere_key_here

# Vector Database APIs (choose based on your preference)
PINECONE_API_KEY=your_pinecone_key_here
WEAVIATE_URL=your_weaviate_instance_url
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Other services
GOOGLE_API_KEY=your_google_key_here
HF_TOKEN=your_huggingface_token_here
```

### 5. Verify Installation

```bash
# Test basic Python setup
python --version
pip --version

# Test a simple import (if dependencies are installed)
python -c "print('Setup looks good!')"

# Navigate to your chosen module to begin
cd docs-content/01_frameworks  # or 02_rag or 03_mcp-acp-a2a
```

## Development Tools

### Recommended IDEs
- **VS Code**: Excellent Python support, extensions
- **PyCharm**: Professional Python IDE
- **Jupyter**: Great for experimentation and learning

### Useful Extensions/Plugins
- Python syntax highlighting and linting
- Git integration
- Docker support
- Markdown preview
- Code formatting (Black, autopep8)

### Command Line Tools
```bash
# Code formatting
pip install black isort

# Linting
pip install flake8 pylint

# Testing
pip install pytest pytest-cov

# Documentation
pip install mkdocs mkdocs-material
```

## Local LLM Options

For development without API costs, consider:

### Ollama
Run models locally with Ollama:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Use in your Python code
import requests
response = requests.post('http://localhost:11434/api/generate',
    json={'model': 'llama2', 'prompt': 'Hello!'})
```

### LM Studio
- User-friendly GUI for running local models
- Easy model management and switching
- Compatible with OpenAI API format

### GPT4All
- Open-source local LLM runner
- Multiple model support
- Privacy-focused local inference

## Getting Help

### Documentation Resources
- Check session materials and API documentation first
- Review the Getting Started guide for common issues
- Consult framework-specific documentation

### Community Support
- GitHub Issues for bugs or unclear instructions
- Community discussions for questions and sharing
- Stack Overflow with tags: `agentic-ai`, `langchain`, `rag`

### Troubleshooting Common Issues

**API Rate Limits**: Use smaller examples, implement delays between requests

**Memory Issues**: Close other applications, consider using smaller models locally

**Import Errors**: Check virtual environment activation and package installation

**Network Issues**: Verify API keys and internet connection

---

**Ready to start?** Begin with the [Getting Started Guide](../getting-started.md) and choose your first module!