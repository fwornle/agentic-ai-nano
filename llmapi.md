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
```
