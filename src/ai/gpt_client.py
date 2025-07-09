import os
import openai
from typing import Any

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]  # Fail fast if missing
openai.api_key = OPENAI_API_KEY

def generate_text(prompt: str, model: str = "gpt-4", max_tokens: int = 256) -> str:
    """Generate text using OpenAI's GPT model."""
    response: Any = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()
