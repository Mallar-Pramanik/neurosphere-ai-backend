import ollama
import logging

logger = logging.getLogger(__name__)

class OdysseusAIService:
    def __init__(self):
        self.is_loaded = False

    async def initialize(self):
        try:
            logger.info("Initializing Odysseus AI with Ollama...")

            ollama.chat(
                model="qwen3:1.7b",
                messages=[
                    {"role": "user", "content": "Hello"}
                ]
            )

            self.is_loaded = True
            logger.info("✅ Qwen3 loaded successfully via Ollama")

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.is_loaded = False

    async def chat(self, message, **kwargs):
        response = ollama.chat(
            model="qwen3:1.7b",
            messages=[
                {"role": "user", "content": message}
            ]
        )

        return response["message"]["content"]

    async def cleanup(self):
        pass