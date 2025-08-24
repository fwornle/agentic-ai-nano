# LLM API Configuration

<!-- BMW Corporate Network Content -->
<div class="bmw-corporate-only" markdown="1">

## BMW Gaia LLM API Configuration

The [BMW Gaia LLM API](https://pages.atc-github.azure.cloud.bmw/Data-Transformation-AI/llm-api/getting_started/introduction/) is available automatically from the Coder AI nanodegree instances.

## Automatic Configuration

The following environment variables are automatically configured in your Coder workspace:

```bash
$ env | grep OPENAI
OPENAI_BASE_URL=...
OPENAI_API_KEY=...
```

OpenAI-compatible tools and libraries work out of the box in this environment.

## Testing Your Connection

To try it out you can run the [`llm`](https://llm.datasette.io/en/stable/index.html) command that is preinstalled:

```bash
llm -m "claude-sonnet-4" "How many r's in blueberry?"
There are 2 r's in "blueberry".
```

## Available Models

The BMW Gaia API provides access to multiple LLM models:
- **Claude Sonnet 4**: High-quality reasoning and analysis
- **GPT-4 variants**: OpenAI's latest models
- **Other enterprise-approved models**: Additional models as they become available

## Using in Your Code

Since the environment variables are set, you can use OpenAI-compatible libraries directly:

```python
from openai import OpenAI

# Uses the pre-configured OPENAI_BASE_URL and OPENAI_API_KEY
client = OpenAI()

response = client.chat.completions.create(
    model="claude-sonnet-4",
    messages=[
        {"role": "user", "content": "Explain agentic AI patterns"}
    ]
)

print(response.choices[0].message.content)
```

## Preinstalled Tools

Your Coder workspace includes several pre-configured AI coding assistants:

### [`coding_assistant`](https://github.com/msc94/coding_assistant)

A CLI-based open-source coding assistant developed by Marcel Schneider, available through our corporate network:

```bash
coding-assistant "Help me implement a basic agent"
```

### [`llm` CLI Tool](https://llm.datasette.io/)

Direct access to LLM models from the command line:

```bash
# Quick queries
llm "What are the key principles of RAG?"

# Specific model selection
llm -m "claude-sonnet-4" "Design a multi-agent system"

# File processing
llm "Summarize this code" < my_script.py
```

## Integration with Frameworks

The pre-configured API works seamlessly with all course frameworks:

### LangChain
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()  # Uses environment variables automatically
response = llm.invoke("Hello, how are you?")
```

### CrewAI
```python
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()  # Pre-configured BMW Gaia API

agent = Agent(
    role='AI Assistant',
    goal='Help with agentic AI development',
    llm=llm
)
```

## Rate Limits and Usage

The BMW Gaia API is configured for educational use within the nanodegree:

- **Reasonable usage**: Designed to support all course activities
- **Rate limiting**: Built-in protections to ensure fair access
- **Monitoring**: Usage is monitored for optimization

## Troubleshooting

### Check Environment Variables
```bash
echo $OPENAI_BASE_URL
echo $OPENAI_API_KEY
```

### Test Connectivity
```bash
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "Content-Type: application/json" \
     "$OPENAI_BASE_URL/v1/models"
```

### Common Issues
- **Missing variables**: Restart your Coder workspace
- **Permission denied**: Contact course administrators
- **Rate limits**: Wait a moment and retry

---

**Ready to develop?** Your BMW Gaia LLM API is ready to use in all course modules and exercises!

</div>

<!-- Public Network Alternative Content -->
<div class="bmw-public-alternative" markdown="1">

## Public LLM API Configuration

For public access, you'll need to configure your own LLM API keys.

### OpenAI Setup

1. Sign up at [OpenAI](https://platform.openai.com/)
2. Create an API key in your dashboard
3. Add to your `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Anthropic Claude Setup

1. Sign up at [Anthropic](https://console.anthropic.com/)
2. Create an API key in your console
3. Add to your `.env` file:

```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### Testing Your Setup

```python
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### Local LLM Options

For development without API costs:

- **Ollama**: Run models locally (`ollama pull llama2`)
- **LM Studio**: User-friendly local LLM interface  
- **GPT4All**: Open-source local models

</div>