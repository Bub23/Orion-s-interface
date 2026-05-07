"""
HeyGen API client wrapper
Avatar + talking video generation
"""


class HeyGenClient:
    """Wrapper for HeyGen API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def generate_video(self, script: str, avatar: str) -> str:
        """Generate talking head video"""
        # TODO: Implement HeyGen API integration
        pass
