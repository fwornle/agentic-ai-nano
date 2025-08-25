# LLM API Configuration

<!-- BMW Corporate Network Content -->
<div class="bmw-corporate-only" markdown="1">

The [BMW Gaia LLM API](https://pages.atc-github.azure.cloud.bmw/Data-Transformation-AI/llm-api/getting_started/introduction/) is available automatically from your Coder workspace.

### Quick Setup

Environment variables are pre-configured:

```bash
$ env | grep OPENAI
OPENAI_BASE_URL=...
OPENAI_API_KEY=...
```

### Testing Your Connection

Test with the pre-installed `llm` command:

```bash
llm -m "claude-sonnet-4" "How many r's in blueberry?"
# Output: There are 2 r's in "blueberry".
```

### Available Models

- **Claude Sonnet 4**: High-quality reasoning and analysis
- **GPT-4 variants**: OpenAI's latest models  
- **Other enterprise-approved models**: Additional models as available

### Using in Code

```python
from openai import OpenAI

# Uses pre-configured environment variables
client = OpenAI()

response = client.chat.completions.create(
    model="claude-sonnet-4",
    messages=[{"role": "user", "content": "Explain agentic AI"}]
)
```

### Framework Integration

Works seamlessly with LangChain, CrewAI, and other frameworks:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()  # Uses BMW Gaia API automatically
```

---

**Ready to develop?** Your BMW Gaia LLM API is ready to use in all course modules and exercises!

</div>

<!-- Public Network Alternative Content -->
<div class="bmw-public-alternative" markdown="1">

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