# LLM API Configuration for Local Development

This guide covers setting up LLM APIs for local development when working outside the BMW corporate network.

## API Provider Options

For local development, you have several LLM API provider options:

### OpenAI API
The most widely supported option across frameworks:

```bash
# Add to your .env file
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
```

### Anthropic Claude API
High-quality reasoning and analysis:

```bash
# Add to your .env file
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Other Providers
Additional commercial and open-source options:

```bash
# Cohere
COHERE_API_KEY=your_cohere_api_key_here

# Google AI
GOOGLE_API_KEY=your_google_api_key_here

# Hugging Face
HF_TOKEN=your_huggingface_token_here
```

## Local LLM Options

For development without API costs:

### Ollama
Run models locally with Ollama:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Start Ollama server (usually runs automatically)
ollama serve
```

Use in your code:
```python
from openai import OpenAI

# Point to local Ollama server
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Required but ignored
)

response = client.chat.completions.create(
    model="llama2",
    messages=[
        {"role": "user", "content": "Explain agentic AI patterns"}
    ]
)
```

### LM Studio
- User-friendly GUI for running local models
- Easy model management and switching
- Compatible with OpenAI API format
- Download from [lmstudio.ai](https://lmstudio.ai/)

### GPT4All
- Open-source local LLM runner
- Multiple model support
- Privacy-focused local inference
- Available at [gpt4all.io](https://gpt4all.io/)

## Environment Setup

Create a `.env` file in your project root:

```bash
# Primary LLM API (choose one)
OPENAI_API_KEY=your_openai_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# OR for local Ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama

# Optional: Additional services
GOOGLE_API_KEY=your_google_api_key_here
HF_TOKEN=your_huggingface_token_here
```

## Testing Your Configuration

### Command Line Testing
Install the `llm` CLI tool for quick testing:

```bash
pip install llm

# Test OpenAI
llm -m gpt-3.5-turbo "How many r's in blueberry?"

# Test with specific API key
llm -m gpt-4 "Explain RAG architecture" --key your_api_key
```

### Python Testing
```python
from openai import OpenAI
import os

# Test your configuration
client = OpenAI()  # Uses OPENAI_API_KEY from environment

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Hello, this is a test!"}
        ],
        max_tokens=50
    )
    print("✅ API connection successful!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"❌ API connection failed: {e}")
```

## Framework Integration

### LangChain
```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# OpenAI
llm = ChatOpenAI(model="gpt-4")

# Anthropic
llm = ChatAnthropic(model="claude-3-sonnet-20240229")

# Local Ollama
llm = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model="llama2"
)
```

### CrewAI
```python
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# Configure your LLM
llm = ChatOpenAI(model="gpt-4")

agent = Agent(
    role='AI Assistant',
    goal='Help with agentic AI development',
    llm=llm
)
```

## Rate Limits and Cost Management

### OpenAI
- Start with GPT-3.5-turbo for development (cheaper)
- Use GPT-4 for production or complex tasks
- Monitor usage at [platform.openai.com](https://platform.openai.com)

### Anthropic
- Claude models have different pricing tiers
- Monitor at [console.anthropic.com](https://console.anthropic.com)

### Cost-Saving Tips
- Use smaller models for development and testing
- Implement request caching for repeated queries
- Set usage limits in provider dashboards
- Consider local models for experimentation

## Troubleshooting

### Common Issues

**Invalid API Key**:
```bash
# Check your environment variables
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

**Rate Limits**:
- Wait between requests
- Implement exponential backoff
- Use smaller models during development

**Network Issues**:
- Check firewall settings
- Verify proxy configuration if needed
- Test with curl:

```bash
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"test"}],"max_tokens":5}' \
     https://api.openai.com/v1/chat/completions
```

### Environment Variables Not Loading
```python
# Explicitly load .env file
from dotenv import load_dotenv
load_dotenv()

import os
print("API Key loaded:", bool(os.getenv("OPENAI_API_KEY")))
```

## Getting API Keys

### OpenAI
1. Visit [platform.openai.com](https://platform.openai.com)
2. Create account and add billing method
3. Generate API key in API settings
4. Start with $5 credit for testing

### Anthropic
1. Visit [console.anthropic.com](https://console.anthropic.com)
2. Sign up and verify email
3. Add payment method
4. Create API key in settings

### Free Alternatives
- **Hugging Face**: Free tier with rate limits
- **Google Colab**: Free GPU access for local models
- **Ollama**: Completely free local models

---

**Ready to develop?** Choose your preferred LLM provider, configure your API keys, and start building agentic AI applications!