import tweepy

class TwitterIntegration:
    """Twitter integration for Orion."""
    
    def __init__(self, api_key, api_secret, access_token, access_token_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.client = None
        self.setup()
    
    def setup(self):
        """Setup Twitter client."""
        try:
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            self.client = tweepy.API(auth)
            return True
        except Exception as e:
            print(f"Twitter setup error: {e}")
            return False
    
    def post_tweet(self, text):
        """Post a tweet."""
        if not self.client:
            return {"success": False, "error": "Twitter not connected"}
        
        try:
            tweet = self.client.update_status(text[:280])
            return {
                "success": True,
                "tweet_id": tweet.id,
                "url": f"https://twitter.com/i/web/status/{tweet.id}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_mentions(self, limit=5):
        """Get recent mentions."""
        if not self.client:
            return []
        
        try:
            mentions = self.client.mentions_timeline(count=limit)
            
            results = []
            for mention in mentions:
                results.append({
                    "author": mention.user.screen_name,
                    "text": mention.text,
                    "created_at": str(mention.created_at),
                    "tweet_id": mention.id
                })
            
            return results
        except Exception as e:
            return []
    
    def search_tweets(self, query, limit=5):
        """Search tweets."""
        if not self.client:
            return []
        
        try:
            tweets = self.client.search_tweets(q=query, count=limit, lang="en")
            
            results = []
            for tweet in tweets:
                results.append({
                    "author": tweet.user.screen_name,
                    "text": tweet.text,
                    "likes": tweet.favorite_count,
                    "retweets": tweet.retweet_count,
                    "url": f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
                })
            
            return results
        except Exception as e:
            return []
    
    def reply_to_tweet(self, tweet_id, text):
        """Reply to a tweet."""
        if not self.client:
            return {"success": False}
        
        try:
            reply = self.client.update_status(text[:280], in_reply_to_status_id=tweet_id)
            return {"success": True, "reply_id": reply.id}
        except Exception as e:
            return {"success": False, "error": str(e)}
