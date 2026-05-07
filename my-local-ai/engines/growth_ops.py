class GrowthOps:
    """
    One system that packages Orion output for:
    YouTube, Facebook, Spotify.
    """

    def build(self, idea, response):
        return {
            "youtube": self.youtube_pack(idea, response),
            "facebook": self.facebook_pack(idea, response),
            "spotify": self.spotify_pack(idea)
        }

    # -------------------------
    # YOUTUBE OPTIMIZATION
    # -------------------------
    def youtube_pack(self, idea, response):
        return {
            "title": self.title(idea),
            "description": self.description(response),
            "tags": self.tags(idea),
            "playlist": self.playlist(idea)
        }

    def title(self, idea):
        return f"{idea} | Official Drop (Outlaw Energy)"

    def description(self, response):
        return (response[:300] + "\n\n#CountryRap #OutlawMusic #AIArtist")

    def tags(self, idea):
        base = ["country rap", "outlaw rap", "music video", "AI music", "independent artist"]
        words = idea.lower().split()
        return base + words[:5]

    def playlist(self, idea):
        return f"{idea} - Official Collection"

    # -------------------------
    # FACEBOOK OPTIMIZATION
    # -------------------------
    def facebook_pack(self, idea, response):
        return {
            "post": f"🔥 {idea}\n\n{response[:200]}...\n\nWhat y’all think?",
            "hashtags": self.tags(idea)[:5]
        }

    # -------------------------
    # SPOTIFY STRATEGY
    # -------------------------
    def spotify_pack(self, idea):
        return {
            "playlist_name": f"{idea} Vibes",
            "strategy": "Release single → add to themed playlist → stack related tracks → boost algorithm placement",
            "genre_tags": ["country rap", "outlaw", "sad rap", "heartbreak", "rural hip hop"]
        }