import asyncio
from ai_analytics_platform.src.models.analytics_models import ForecastRequest, ForecastResponse
from ai_analytics_platform.src.ai.gpt_client import generate_text
from ai_analytics_platform.src.utils.logger import get_logger

logger = get_logger()

async def generate_forecast(request: ForecastRequest) -> ForecastResponse:
    """Generate a forecast asynchronously using GPT."""
    try:
        await asyncio.sleep(0.1)  # Simulate I/O
        prompt = f"Forecast the following data: {request.data}"
        forecast = generate_text(prompt)
        logger.info(f"Forecast generated for data: {request.data}")
        return ForecastResponse(forecast=forecast)
    except Exception as e:
        logger.error(f"Failed to generate forecast: {e}")
        raise
