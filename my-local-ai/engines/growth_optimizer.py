class GrowthOptimizer:

    def optimize_youtube(self, idea, response):
        """
        Creates SEO optimized YouTube packaging.
        """

        title = self._create_title(idea)
        description = self._create_description(response)
        tags = self._generate_tags(idea)

        return {
            "title": title,
            "description": description,
            "tags": tags,
            "playlist": self._suggest_playlist(idea)
        }

    def optimize_facebook(self, idea, response):
        """
        Creates high engagement FB post format.
        """

        return {
            "post": f"🔥 {idea}\n\n{response[:200]}...\n\nWhat y’all think?",
            "hashtags": self._generate_tags(idea)[:5]
        }

    def optimize_spotify_strategy(self, song_name):
        """
        Suggests playlist positioning + release logic.
        """

        return {
            "playlist_theme": f"{song_name} - Mood Collection",
            "placement_strategy": "Release single → playlist seed → algorithm stacking",
            "tags": ["country rap", "outlaw", "sad rap", "heartbreak", "rural hip hop"]
        }

    # --------------------
    # INTERNAL HELPERS
    # --------------------

    def _create_title(self, idea):
        return f"{idea} (Official Drop) | Outlaw Energy"

    def _create_description(self, response):
        return (
            response[:300] +
            "\n\n#CountryRap #OutlawMusic #AIArtist #BubOutlaw"
        )

    def _generate_tags(self, idea):
        base = ["country rap", "outlaw", "rap music", "AI music", "independent artist"]
        dynamic = idea.lower().split()
        return base + dynamic[:5]

    def _suggest_playlist(self, idea):
        return f"🔥 {idea} Collection"