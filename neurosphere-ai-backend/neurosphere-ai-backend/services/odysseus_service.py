import logging

logger = logging.getLogger(__name__)

class OdysseusAIService:
    def __init__(self):
        self.is_loaded = True

    async def initialize(self):
        logger.info("Odysseus AI initialized")

    async def chat(self, message, **kwargs):
        return f"You said: {message}"

    async def cleanup(self):
        pass