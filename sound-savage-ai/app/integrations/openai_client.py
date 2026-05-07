"""
OpenAI client wrapper
Isolated integration layer for OpenAI API calls
"""

import openai
from app.core.config import settings


class OpenAIClient:
    """Wrapper for OpenAI API"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4"
    
    async def generate_hook(
        self,
        base_hook: str,
        content: str,
        pattern_type: str
    ) -> str:
        """Generate AI-powered hook from base pattern"""
        
        prompt = f"""
You are a viral content expert. Create a hook that:
- Starts with: "{base_hook}"
- Relates to: "{content}"
- Pattern type: {pattern_type}
- Is 1 sentence max (under 100 chars)
- Creates curiosity gap or shock

Output ONLY the hook, nothing else:
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a viral hook expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
    
    async def generate_hook_variations(
        self,
        hook_text: str,
        num_variations: int = 5
    ) -> list[str]:
        """Generate variations of a hook"""
        
        prompt = f"""
You are a viral hook master. The following hook is a high performer:
"{hook_text}"

Create {num_variations} variations with SAME structure but DIFFERENT emotional angles:
1. Curiosity angle
2. Urgency angle
3. Fear angle
4. Aspiration angle
5. Rebellion angle

Format: Output each on new line, numbered. No explanations.
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a hook variation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        variations = response.choices[0].message.content.strip().split('\n')
        return [v.replace(f"{i+1}.", "").strip() for i, v in enumerate(variations) if v.strip()][:num_variations]
    
    async def generate_script_body(
        self,
        hook: str,
        pacing: str = "medium"
    ) -> list[str]:
        """Generate script body (list of sections/paragraphs)"""
        
        pacing_guide = {
            "fast": "Short, punchy sentences. Quick cuts.",
            "medium": "Balanced pacing. Mix of short and medium sentences.",
            "slow": "Longer sentences. Build tension. More dramatic."
        }
        
        prompt = f"""
You are a script writer. Generate a short script body (3-4 paragraphs) for:
Hook: "{hook}"
Pacing: {pacing_guide.get(pacing, pacing_guide['medium'])}

Output as JSON array of paragraphs, each under 100 words.
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a script writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip().split('\n')
    
    async def generate_cta(self, hook: str) -> str:
        """Generate call-to-action"""
        
        prompt = f"""
Generate a short, punchy CTA for this hook:
"{hook}"

Output ONLY the CTA (under 20 words), nothing else.
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a copywriter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        return response.choices[0].message.content.strip()
