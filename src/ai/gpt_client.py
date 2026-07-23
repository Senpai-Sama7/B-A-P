"""
OpenAI GPT client for AI-powered features.
"""

from openai import AsyncOpenAI
from typing import Optional
from src.config import get_settings

settings = get_settings()

# Initialize async OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_text(
    prompt: str,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
) -> str:
    """Generate text using OpenAI's GPT model asynchronously."""
    model = model or settings.OPENAI_MODEL
    max_tokens = max_tokens or settings.MAX_TOKENS
    temperature = temperature or settings.TEMPERATURE

    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )

    content = response.choices[0].message.content
    return content.strip() if content else ""
