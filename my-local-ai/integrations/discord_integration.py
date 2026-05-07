import os
import discord
from discord.ext import commands
import asyncio

class DiscordIntegration:
    """Discord bot integration for Orion."""
    
    def __init__(self, token, callback):
        self.token = token
        self.callback = callback
        self.client = None
        self.running = False
    
    def setup(self):
        """Setup Discord bot."""
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            self.client = commands.Bot(command_prefix='!', intents=intents)
            
            @self.client.event
            async def on_ready():
                print(f'✓ Discord bot logged in as {self.client.user}')
            
            @self.client.event
            async def on_message(message):
                if message.author == self.client.user:
                    return
                
                # Call callback with message
                response = await self.callback(message.content)
                
                # Send response
                await message.channel.send(f"🧠 Orion: {response[:2000]}")
            
            return True
        except Exception as e:
            print(f"Discord setup error: {e}")
            return False
    
    def start(self):
        """Start Discord bot."""
        if self.token:
            try:
                asyncio.run(self.client.start(self.token))
                self.running = True
            except Exception as e:
                print(f"Discord start error: {e}")
    
    def send_message(self, channel_id, message):
        """Send message to Discord channel."""
        if not self.running:
            return False
        
        try:
            channel = self.client.get_channel(channel_id)
            if channel:
                asyncio.run_coroutine_threadsafe(channel.send(message), self.client.loop)
                return True
        except Exception as e:
            print(f"Discord send error: {e}")
        
        return False
