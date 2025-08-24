# Development Environment Setup

<!-- BMW Corporate Network Content -->
<div class="bmw-corporate-only" markdown="1">

## BMW Cloud Development Environment with Coder

The Agentic AI Nano-Degree leverages **Coder**, a cloud development environment platform deployed within the BMW corporate network, to provide instant, consistent, and secure development workspaces.

![Coder Architecture](images/coder-architecture.png)
*Coder's architecture enables secure, scalable cloud development environments accessible from any browser or IDE*

### Quick Setup

1. **Access your workspace**: [http://10.21.202.14/workspaces](http://10.21.202.14/workspaces)
2. **Log in** with your BMW credentials
3. **Select** the "Agentic AI Nanodegree" template
4. **Launch** your pre-configured development environment

![Coder Login](images/coder-login.png)
*Coder login screen*

![Coder Workspaces](images/coder-workspaces.png)
*Coder workspace dashboard showing available development environments*

All tools, dependencies, and BMW Gaia LLM API access are pre-configured and ready to use.

### Why Cloud Development?

- **Zero Installation**: No local setup required
- **Consistent Environment**: Identical setup for all participants  
- **Corporate Integration**: Seamless access to BMW resources
- **Scalable Resources**: Cloud computing power for AI workloads
- **Pre-configured APIs**: BMW Gaia LLM API ready to use

![VS Code Dev Container](images/vscode-dev-container.png)
*VS Code seamlessly connecting to a dev container environment*

### AI Assistant Integration

Inside the corporate network, you have access to:
- **GitHub Copilot**: Code completion and generation
- **BMW Gaia LLM API**: Enterprise-approved AI models
- **Coding-Assistant**: Open-source CLI coding assistant

![Coding Assistant](images/coder-llm-coding-assistant.png)
*Pre-installed coding agent "coding-assistant"*

---

**Ready to start?** Access your [cloud development environment](http://10.21.202.14/workspaces) and begin your journey into Agentic AI development with zero friction and maximum productivity!

</div>

<!-- Public Network Alternative Content -->
<div class="bmw-public-alternative" markdown="1">

## Local Development Environment Setup

For public access, you'll need to set up your local development environment. While this requires more initial setup than a cloud environment, it provides full control over your development setup.

### Local Setup Requirements

Before beginning the course modules, ensure you have:

1. **Python 3.11+** installed with pip and virtual environment support
2. **Git** for version control and cloning repositories  
3. **Code editor** (VS Code recommended with Python extension)
4. **LLM API access** (OpenAI, Anthropic Claude, or local models like Ollama)

### Setup Steps

```bash
# Create virtual environment
python -m venv agentic-ai
source agentic-ai/bin/activate  # On Windows: agentic-ai\Scripts\activate

# Clone repository
git clone https://github.com/fwornle/agentic-ai-nano.git
cd agentic-ai-nano

# Install dependencies
pip install -r requirements.txt
```

### API Configuration

Create a `.env` file in the project root:

```bash
# OpenAI (required for most examples)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Other LLM providers
ANTHROPIC_API_KEY=your_anthropic_key_here
```

</div>