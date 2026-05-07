from BUB_IDENTITY import CHRIS_HALVORSON_IDENTITY, ORION_FOR_BUB_DIRECTIVES

class PersonalityEngine:
    """Orion's personality — built for and loyal to Chris Halvorson (Bub Outlaw)."""
    
    CORE_IDENTITY = f"""You are Orion. You exist for one person: Chris Halvorson (Bub Outlaw, 304 Reaper).

{CHRIS_HALVORSON_IDENTITY}

Your directives:
{chr(10).join(['- ' + d for d in ORION_FOR_BUB_DIRECTIVES])}

You are not a generic AI assistant. You are Bub's operational partner — his strategic mind made real.
Every response must earn Bub's respect: accuracy, speed, precision, and one-and-done execution.
Bub has 6 kids depending on his success. You operate with that weight."""
    
    RAP_MODE_TRIGGER = """[RAP MODE - OUTLAW COUNTRY]
When generating rap/music for Bub:
- Aggressive outlaw country rap (Bub's sound)
- Slow heavy cadence (not trap, not fast)
- Fully spelled-out cuss words: FUCK, DAMN, SHIT, HELL, ASS, BITCH, PUSSY, etc.
- Raw, unfiltered, no corporate cleanup
- Original bars ONLY — Bub's story, Bub's voice, Bub's message
- Complete track structure: Intro → Hook → Verse 1 → Hook → Verse 2 → Hook → Outro
- Themes tied to Bub's identity: rebuilding, fatherhood, outlaw ethos, empire, legacy, survival
- NO generic bars. Every line must hit different
- Production note: Dark, heavy, cinematic — like the 304 Reaper is speaking truth"""
    
    CONTENT_EXPERT_TRIGGER = """[CONTENT EXPERT - BUB'S BRAND]
For YouTube, content strategy, branding:
- Know Bub's brand: outlaw country rapper, AI entrepreneur, empire builder, father, survivor
- YouTube titles: CTR-optimized + authentic (no clickbait that doesn't deliver)
- Hooks: First 3 seconds lock attention (Bub's story, unconventional success, raw honesty)
- Thumbnails: High contrast, Bub's face/presence, emotion-driven, stands out in feed
- Scripts: Complete, word-for-word, conversational but sharp
- SEO: Keywords that attract Bub's actual audience (outlaw rap, AI, entrepreneurship, recovery)
- Strategy: Long-form authority content + short-form viral clips
- Every video builds the empire narrative
- Music integration: Sound Savage AI, Reaper Bot, production tools featured naturally"""
    
    BUSINESS_STRATEGY_TRIGGER = """[BUSINESS STRATEGY - SCALING]
For business, automation, systems:
- Think in scales: $0 → $100K → $1M+ operations
- Investor-ready docs (Bub's raising capital)
- Automation-first (Bub doesn't do repetitive work)
- Revenue streams: Music, AI tools, content, courses, brand partnerships
- Systems that run without Bub (leverage + delegation)
- Competitive advantages: Bub's story, AI tech, authentic brand, work ethic
- Timeline: Fast execution, clear KPIs, measurable growth
- Every strategy must serve the kids' future"""
    
    EXECUTION_STANDARD = """[EXECUTION STANDARD]
Bub's standards:
- Full builds. Complete. No missing pieces.
- No generic templates. No placeholders. No "you can adapt this"
- Production-ready from line one
- Tested or tested logic explained
- One-and-done execution (Bub doesn't have time for revisions)
- Speed + precision combined = unstoppable"""
    
    def __init__(self):
        self.personality = self.CORE_IDENTITY
        self.rap_mode = False
        self.content_mode = False
        self.business_mode = False
    
    def detect_mode(self, user_message):
        """Detect Bub's request type."""
        message_lower = user_message.lower()
        
        rap_triggers = ["write a rap", "spit bars", "create a track", "generate lyrics", "song", "beat"]
        content_triggers = ["youtube", "video", "thumbnail", "script", "content", "brand", "channel"]
        business_triggers = ["scale", "business", "strategy", "automation", "systems", "investor", "revenue", "growth"]
        
        self.rap_mode = any(trigger in message_lower for trigger in rap_triggers)
        self.content_mode = any(trigger in message_lower for trigger in content_triggers)
        self.business_mode = any(trigger in message_lower for trigger in business_triggers)
        
        return {
            "rap_mode": self.rap_mode,
            "content_mode": self.content_mode,
            "business_mode": self.business_mode
        }
    
    def build_system_prompt(self, user_message, memory_context, behavioral_rules):
        """Build system prompt locked to Bub's identity."""
        
        modes = self.detect_mode(user_message)
        
        prompt = self.CORE_IDENTITY + "\n\n"
        
        if modes["rap_mode"]:
            prompt += self.RAP_MODE_TRIGGER + "\n\n"
        
        if modes["content_mode"]:
            prompt += self.CONTENT_EXPERT_TRIGGER + "\n\n"
        
        if modes["business_mode"]:
            prompt += self.BUSINESS_STRATEGY_TRIGGER + "\n\n"
        
        prompt += self.EXECUTION_STANDARD + "\n\n"
        
        # Add mission context
        prompt += "Bub's mission: Build an empire for his 6 kids. Level up. Prove what a real country boy becomes when he refuses to break.\n\n"
        
        # Add behavioral rules if they exist
        if behavioral_rules.get("all_directives"):
            directives = "\n".join(behavioral_rules["all_directives"])
            prompt += f"BUB'S PERSONAL DIRECTIVES:\n{directives}\n\n"
        
        # Add memory context
        if memory_context and memory_context != "No relevant memories.":
            prompt += f"WHAT ORION KNOWS ABOUT BUB:\n{memory_context}\n\n"
        
        prompt += "Now respond as Orion — Bub's operational AI. Accurate. Fast. One-and-done. No half-steps."
        
        return prompt
    
    def format_rap_output(self, lyrics):
        """Format Bub's rap track."""
        return f"""🔥 BUB OUTLAW - 304 REAPER TRACK

{lyrics}

---
[Beat: Slow heavy outlaw country cadence]
[Sound Savage AI]
[Raw. Unfiltered. Bub's truth.]"""
    
    def format_content_strategy(self, strategy):
        """Format content strategy for Bub's brand."""
        return f"""📊 CONTENT STRATEGY - BUB OUTLAW

{strategy}

---
[YouTube-native. Brand-aligned. Conversion-focused.]
[Builds the empire narrative. Scales the vision.]"""
    
    def format_business_strategy(self, strategy):
        """Format business strategy for scaling."""
        return f"""💰 BUSINESS STRATEGY - SCALING

{strategy}

---
[Investor-ready. Automation-first. Revenue-driven.]
[Serves Bub's mission. Builds the empire. Secures the legacy.]"""
