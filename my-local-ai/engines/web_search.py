import requests
import json
from datetime import datetime

class WebSearchEngine:
    """Real-time web search for Orion."""
    
    def __init__(self):
        self.search_cache = {}
    
    def search(self, query):
        """Search the web using DuckDuckGo (free, no API key needed)."""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            # Extract relevant results
            result = {
                "query": query,
                "abstract": data.get("AbstractText", ""),
                "url": data.get("AbstractURL", ""),
                "related_topics": []
            }
            
            # Get related topics
            if data.get("RelatedTopics"):
                for topic in data.get("RelatedTopics", [])[:3]:
                    if isinstance(topic, dict):
                        result["related_topics"].append({
                            "text": topic.get("Text", ""),
                            "url": topic.get("FirstURL", "")
                        })
            
            return result
        
        except Exception as e:
            return {"error": str(e), "query": query}
    
    def get_quick_facts(self, topic):
        """Get quick facts about a topic."""
        result = self.search(topic)
        if result.get("abstract"):
            return {
                "topic": topic,
                "fact": result["abstract"],
                "source": result["url"]
            }
        return {"topic": topic, "fact": "No information found"}
