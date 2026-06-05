# Research & Technical Guide: OpenRouter Integration
> **Scope**: Unified API Gateway, Free Tier Models, Next.js Vercel AI SDK Integration, and Resource Optimization.

---

## 1. Why OpenRouter?
OpenRouter serves as a single API gateway to dozens of Large Language Model (LLM) providers. By routing our chatbot requests through OpenRouter, we achieve:
* **Model Agnosticism**: We can switch the backend LLM (e.g., from Gemini to Claude, DeepSeek, or Llama) by changing a single string in our config, without modifying the integration code or installing new SDKs.
* **Unified API Key**: The club only needs one OpenRouter account/API key to experiment with models from Google, Anthropic, OpenAI, Meta, and Mistral.
* **OpenAI-Compatible Payload**: OpenRouter uses the standard OpenAI API request/response format, meaning we can use existing OpenAI client libraries or the Vercel AI SDK's OpenAI provider.
* **Aggregated Free Tiers**: OpenRouter aggregates free-tier and low-cost models from multiple providers, allowing the club to build the MVP without paying any licensing or compute costs.

---

## 2. Recommended OpenRouter Models

We evaluate the best free-tier and low-cost models available on OpenRouter for the Success Coach Chatbot:

| Model String on OpenRouter | Provider | Context Window | Best Use Case | Cost per 1M Tokens (Input/Output) |
| :--- | :--- | :--- | :--- | :--- |
| `google/gemini-2.5-flash` | Google (via OpenRouter) | 1,000,000 | Core RAG answering, speed, and parsing. | Free Tier ($0.00) or ~$0.075 / $0.30 |
| `google/gemini-2.5-flash:free` | Google (via OpenRouter) | 1,000,000 | Standard developer/test runs. | **$0.00 / $0.00** |
| `meta-llama/llama-3-8b-instruct:free` | Meta (via OpenRouter) | 8,192 | Low-latency chat flow, basic greeting routing. | **$0.00 / $0.00** |
| `qwen/qwen-2-7b-instruct:free` | Alibaba (via OpenRouter) | 32,768 | Alternative reasoning and multi-lingual queries. | **$0.00 / $0.00** |
| `deepseek/deepseek-chat` | DeepSeek | 64,000 | Complex reasoning & multi-step tool planning. | ~$0.14 / $0.28 |

---

## 3. Integration Code Patterns

### 🌐 Next.js Backend Integration (Vercel AI SDK)
Because OpenRouter matches the OpenAI API schema, we configure the OpenAI provider in Next.js pointing to OpenRouter's endpoint `https://openrouter.ai/api/v1`.

```typescript
// apps/frontend/app/api/chat/route.ts
import { createOpenAI } from '@ai-sdk/openai';
import { streamText } from 'ai';

// Initialize the OpenRouter client using Vercel AI SDK
const openrouter = createOpenAI({
  baseURL: 'https://openrouter.ai/api/v1',
  apiKey: process.env.OPENROUTER_API_KEY || '',
  defaultHeaders: {
    'HTTP-Referer': 'https://dc-success-coach.vercel.app', // Required by OpenRouter rankings
    'X-Title': 'Dallas College AI Success Coach', // Required by OpenRouter rankings
  },
});

export async function POST(req: Request) {
  const { messages } = await req.json();

  // Use Gemini 2.5 Flash as the default model
  const result = await streamText({
    model: openrouter('google/gemini-2.5-flash'),
    messages,
    maxTokens: 4000, // Explicitly limit max output tokens to preserve credits
    system: `You are the Dallas College Success Coach AI. Answer student questions accurately using catalog facts.`,
  });

  return result.toDataStreamResponse();
}
```

### 🐍 Python Data/Scraping Layer (using `litellm` or `openai`)
To invoke OpenRouter from our Python data scripts (e.g., to summarize scraped catalogs or generate metadata), we can use the LiteLLM library.

```python
# apps/data/dallasai/summary.py
import os
from litellm import completion

def generate_summary(text_chunk: str) -> str:
    response = completion(
        model="openrouter/google/gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "You are a catalog data parser. Summarize this degree requirement in 2 sentences."},
            {"role": "user", "content": text_chunk}
        ],
        api_base="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        max_tokens=2000 # Keep limit low to avoid credit reservation errors
    )
    return response.choices[0].message.content
```

---

## 4. Resource Optimization & Credit Preservation (Crucial Protocols)

OpenRouter uses a **Credit Pre-authorization** model. When a client initiates a request without specifying a `max_tokens` parameter, LiteLLM/OpenRouter assumes the maximum potential output size (e.g., 65,535 tokens for Gemini 2.5 Flash). If your OpenRouter balance is low or on a free/shared plan, the request is rejected with a **402 Payment Required** error:
`This request requires more credits, or fewer max_tokens.`

### 🛠️ Mitigation Rules:
1. **Explicitly Cap Output Tokens**: Always supply `max_tokens` (or `maxTokens` in JS) in all API calls. Capping this at `4000` to `8000` tokens ensures OpenRouter pre-authorizes only a few cents worth of tokens, preventing credit locks.
2. **Aider Configuration Overrides**:
   When developers run Aider locally with OpenRouter, they must include a `.aider.model.settings.yml` file to restrict `max_tokens` to `8000` and lock the edit format to `diff-fenced`:
   ```yaml
   - name: openrouter/google/gemini-2.5-flash
     edit_format: diff-fenced
     extra_params:
       max_tokens: 8000
   ```
3. **Use the `:free` Endpoint suffixes**: During testing and staging runs, prioritize models with the `:free` suffix (e.g., `google/gemini-2.5-flash:free`) to consume $0.00 credits.
