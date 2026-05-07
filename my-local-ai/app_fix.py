def _get_orion_response(user_message, memory_context, behavioral_rules):
    """Get Orion's response from Lightning AI, influenced by memories and directives."""
    
    # Build system prompt with behavior rules
    directives = "\n".join(behavioral_rules.get("all_directives", []))
    identity = behavioral_rules.get("identity", "You are Orion, an AI assistant.")
    
    full_prompt = f"""You are Orion. {identity}

BEHAVIORAL DIRECTIVES (MUST FOLLOW):
{directives}

RELEVANT MEMORIES:
{memory_context}

User: {user_message}

Respond as Orion. Be authentic. Follow your directives. Remember your context."""
    
    try:
        response = llm.chat(full_prompt)
        
        # Handle response format
        if isinstance(response, dict):
            return response.get("choices", [{}])[0].get("message", {}).get("content", str(response))
        elif isinstance(response, str):
            return response
        else:
            return str(response)
    
    except Exception as e:
        return f"Orion encountered an error: {str(e)}"
