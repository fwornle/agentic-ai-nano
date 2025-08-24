# LLM API Configuration

<!-- BMW Corporate Network Content -->
<div class="bmw-corporate-only" markdown="1">

## BMW Gaia LLM API

The [BMW Gaia LLM API](https://pages.atc-github.azure.cloud.bmw/Data-Transformation-AI/llm-api/getting_started/introduction/) is available automatically from the Coder AI nanodegree instances.

The following environment variables are automatically configured:

```bash
$ env | grep OPENAI
OPENAI_BASE_URL=...
OPENAI_API_KEY=...
```

OpenAI-compatible tools and libraries work out of the box in this environment.

To try it out you can run the [`llm`](https://llm.datasette.io/en/stable/index.html) command that is preinstalled:

```bash
llm -m "claude-sonnet-4" "How many r's in blueberry?"
There are 2 r's in "blueberry".
```

### Available Models

The BMW Gaia API provides access to multiple LLM models:
- Claude Sonnet 4
- GPT-4 variants
- Other enterprise-approved models

</div>

<!-- Public Network Alternative Content -->
<div class="bmw-public-alternative" markdown="1">

## Public LLM API Configuration

For public access, you'll need to configure your own LLM API keys. We recommend starting with OpenAI or Anthropic Claude.

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

Test your API configuration:

```python
# Test OpenAI
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### Local LLM Options

For local development without API costs:

- **Ollama**: Run models locally
- **LM Studio**: User-friendly local LLM interface  
- **GPT4All**: Open-source local models

</div>

## Preinstalled tools

### [`coding_assistant`](https://github.com/msc94/coding_assistant)

```bash
coding-assistant --task "Create a program fibonacci.py that asks a user and calculates N numbers."
```

### ollama

```bash
ollama run qwen:0.6b
```

### [`llm`](https://llm.datasette.io/en/stable/index.html)

```bash
llm -m "claude-sonnet-4" "How many r's in blueberry?"
There are 2 r's in "blueberry".
```

## Agentic Frameworks

### Pydantic AI - Getting started

To follow along the [tutorial](https://ai.pydantic.dev/agents/):

```bash
mkdir pydantic-tutorial
cd pydantic-tutorial
uv init
uv add pydantic-ai
```

Create `roulette_wheel.py` as provided in the tutorial:

```python
from pydantic_ai import Agent, RunContext
import random

roulette_agent = Agent(
    "openai:gpt-4o",
    deps_type=int,
    output_type=bool,
    system_prompt=(
        "Use the `roulette_wheel` function to see if the " "customer has won based on the number they provide."
    ),
)


@roulette_agent.tool
async def roulette_wheel(ctx: RunContext[int], square: int) -> str:
    """check if the square is a winner"""
    return "winner" if square == ctx.deps else "loser"


# Run the agent
success_number = random.randint(0, 36)
result = roulette_agent.run_sync("Put my money on square eighteen", deps=success_number)
print(result.output)
# > True

result = roulette_agent.run_sync("I bet five is the winner", deps=success_number)
print(result.output)
# > False
```

You can run the agent like this:

```bash
uv run python roulette_agent.py
```
