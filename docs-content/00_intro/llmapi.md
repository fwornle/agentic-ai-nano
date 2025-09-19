# LLM API Configuration

<script>
// Corporate network redirect
if (window.location.hostname.includes('fwornle.github.io') && 
    window.CorporateContentLoader && 
    window.networkDetection && 
    window.networkDetection.isCorporateNetwork) {
    // Redirect to corporate version
    window.location.href = '../corporate-only/00_intro/llmapi-detailed/';
}
</script>

This guide helps you set up LLM API access for the Agentic AI Nano-Degree course modules. Corporate users have access to pre-configured APIs, while public users can set up their own API keys.

## OpenAI Setup

1. Sign up at [OpenAI](https://platform.openai.com/)  
2. Create an API key in your dashboard  
3. Add to your `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Anthropic Claude Setup

1. Sign up at [Anthropic](https://console.anthropic.com/)  
2. Create an API key in your console  
3. Add to your `.env` file:

```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## Testing Your Setup

```python
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

## Framework Integration

Works seamlessly with LangChain, CrewAI, and other frameworks:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()  # Uses your configured API keys
```

## Local LLM Options

For development without API costs:

- **Ollama**: Run models locally (`ollama pull llama2`)
- **LM Studio**: User-friendly local LLM interface  
- **GPT4All**: Open-source local models  

## Enterprise Setup

For corporate environments, API access may be pre-configured. Contact your IT department for:

- Pre-configured API endpoints
- Corporate-approved models
- Security compliance requirements
- Usage monitoring and billing

---

**Ready to develop?** Your LLM API configuration is ready for use in all course modules and exercises!
