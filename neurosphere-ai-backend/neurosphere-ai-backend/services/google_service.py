import logging

logger = logging.getLogger(__name__)

class GoogleAPIService:
    def __init__(self):
        logger.info("Google API disabled")

    def analyze_sentiment(self, text):
        return {"error": "Google API disabled"}

    def analyze_entities(self, text):
        return {"error": "Google API disabled"}

    def analyze_syntax(self, text):
        return {"error": "Google API disabled"}