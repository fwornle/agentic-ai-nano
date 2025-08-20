# LLM API

The [BMW LLM API](https://pages.atc-github.azure.cloud.bmw/Data-Transformation-AI/llm-api/getting_started/introduction/) is available automatically from the Coder AI nanodegree instances.

The following environment variables are set:

```bash
$ env | grep OPENAI
OPENAI_BASE_URL=...
OPENAI_API_KEY=...
```

Openai compatible tools and libraries should work out of the box in this environment.

To try it out you can run the [`llm`](https://llm.datasette.io/en/stable/index.html) command that is also preinstalled:

```bash
llm -m "claude-sonnet-4" "How many r's in blueberry?"
There are 2 r's in "blueberry".
```

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

roulette_agent = Agent(  
    'openai:gpt-4o',
    deps_type=int,
    output_type=bool,
    system_prompt=(
        'Use the `roulette_wheel` function to see if the '
        'customer has won based on the number they provide.'
    ),
)


@roulette_agent.tool
async def roulette_wheel(ctx: RunContext[int], square: int) -> str:  
    """check if the square is a winner"""
    return 'winner' if square == ctx.deps else 'loser'


# Run the agent
success_number = 18  
result = roulette_agent.run_sync('Put my money on square eighteen', deps=success_number)
print(result.output)  
#> True

result = roulette_agent.run_sync('I bet five is the winner', deps=success_number)
print(result.output)
#> False
```

You can run the agent like this:

```bash
uv run python roulette_agent.py
```
