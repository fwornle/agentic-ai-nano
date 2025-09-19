# Development Environment Setup

<script>
// Corporate network redirect
if (window.location.hostname.includes('fwornle.github.io') && 
    window.CorporateContentLoader && 
    window.networkDetection && 
    window.networkDetection.isCorporateNetwork) {
    // Redirect to corporate version
    window.location.href = '../corporate-only/00_intro/coder-detailed/';
}
</script>

This guide helps you set up your development environment for the Agentic AI Nano-Degree course modules. Corporate users have access to pre-configured cloud environments, while public users can set up their own local development environment.

## Local Development Environment Setup

For public access, you'll need to set up your local development environment. While this requires more initial setup than a cloud environment, it provides full control over your development setup.

### Requirements

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

### IDE Setup

**VS Code (Recommended)**:
1. Install the Python extension
2. Install the Jupyter extension for notebook support
3. Open the project folder
4. Select your virtual environment as the Python interpreter

### Testing Your Setup

```python
# Test your API configuration
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello! Test message."}]
)
print(response.choices[0].message.content)
```

### Local LLM Options

For development without API costs:

- **Ollama**: Run models locally (`ollama pull llama2`)  
- **LM Studio**: User-friendly local LLM interface  
- **GPT4All**: Open-source local models  

### Course Module Structure

Each module includes:

- **Jupyter notebooks** for interactive learning  
- **Python scripts** for standalone examples  
- **Requirements files** for module-specific dependencies  
- **README files** with module-specific setup instructions  

---

**Ready to start?** With your local environment configured, you can begin working through the course modules and exercises!