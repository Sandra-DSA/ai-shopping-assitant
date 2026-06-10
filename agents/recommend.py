"""
agents/recommend.py
-------------------
Recommend Agent — sends top products to an LLM and gets a natural language recommendation.

This agent is responsible for:
- Building a prompt from the top ranked products
- Calling the configured LLM provider (Gemini / OpenAI / Anthropic)
- Returning a clean, conversational recommendation response

Students:
- The prompt builder is implemented below.
- You need to complete the LLM call for your chosen provider (see TODOs).
- Only implement the provider your team is using — leave others as stubs.
"""

import config


def build_prompt(user_query: str, top_products: list[dict]) -> str:
    """
    Builds the prompt to send to the LLM.

    Args:
        user_query   : Original query from the user
        top_products : Top ranked products from the Compare Agent

    Returns:
        str: Formatted prompt string
    """
    product_lines = []
    for i, p in enumerate(top_products, start=1):
        product_lines.append(
            f"{i}. {p['product_name']} by {p['brand']}\n"
            f"   Store: {p['store']} | Price: Rs {p['price']} (MRP: Rs {p['mrp']})\n"
            f"   Rating: {p['rating']}/5 ({p['review_count']} reviews)\n"
            f"   Specs: {p['key_specs']}\n"
            f"   Pros: {p['pros']}\n"
            f"   Cons: {p['cons']}\n"
            f"   Score: {p.get('score', 'N/A')}/100"
        )

    products_text = "\n\n".join(product_lines)

    prompt = f"""You are a helpful shopping assistant. A user is looking for: "{user_query}"

Based on the available products, here are the top recommendations:

{products_text}

Please give a friendly, concise recommendation in 3–5 sentences. 
- Mention which product offers the best value and why.
- Point out any trade-offs the user should know about.
- Suggest which store to buy from based on the price.
- Do not make up any information not provided above.
"""
    return prompt


def get_recommendation(user_query: str, top_products: list[dict]) -> str:
    """
    Sends the top products to the configured LLM and returns a recommendation.

    Args:
        user_query   : Original query from the user
        top_products : Top ranked products from the Compare Agent

    Returns:
        str: Natural language recommendation from the LLM

    Raises:
        ValueError: If LLM_PROVIDER is not recognised or API key is missing
    """
    if not top_products:
        return "Sorry, I could not find any products matching your request. Try a different search."

    prompt = build_prompt(user_query, top_products)
    provider = config.LLM_PROVIDER.lower()

    if provider == "gemini":
        return _call_gemini(prompt)
    elif provider == "openai":
        return _call_openai(prompt)
    elif provider == "anthropic":
        return _call_anthropic(prompt)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: '{provider}'. Set it to gemini, openai, or anthropic in .env")


# ─────────────────────────────────────────────────────────────────────────────
# LLM Provider Implementations
# ─────────────────────────────────────────────────────────────────────────────

def _call_gemini(prompt: str) -> str:
    """
    Calls the Google Gemini API and returns the response text.

    TODO:
        1. Install the SDK:       pip install google-generativeai
        2. Import and configure:
               import google.generativeai as genai
               genai.configure(api_key=config.GEMINI_API_KEY)
        3. Create a model and call it:
               model = genai.GenerativeModel("gemini-1.5-flash")
               response = model.generate_content(prompt)
               return response.text
    """
    raise NotImplementedError("Gemini integration not yet implemented. See TODO in _call_gemini()")


def _call_openai(prompt: str) -> str:
    """
    Calls the OpenAI API and returns the response text.

    TODO:
        1. Install the SDK:       pip install openai
        2. Import and call:
               from openai import OpenAI
               client = OpenAI(api_key=config.OPENAI_API_KEY)
               response = client.chat.completions.create(
                   model="gpt-4o-mini",
                   messages=[{"role": "user", "content": prompt}]
               )
               return response.choices[0].message.content
    """
    raise NotImplementedError("OpenAI integration not yet implemented. See TODO in _call_openai()")


def _call_anthropic(prompt: str) -> str:
    """
    Calls the Anthropic Claude API and returns the response text.

    TODO:
        1. Install the SDK:       pip install anthropic
        2. Import and call:
               import anthropic
               client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
               message = client.messages.create(
                   model="claude-haiku-4-5-20251001",
                   max_tokens=512,
                   messages=[{"role": "user", "content": prompt}]
               )
               return message.content[0].text
    """
    raise NotImplementedError("Anthropic integration not yet implemented. See TODO in _call_anthropic()")
