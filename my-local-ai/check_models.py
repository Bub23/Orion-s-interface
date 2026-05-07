import requests
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('GROQ_API_KEY')

models = ['llama-3.2-90b-vision-preview', 'llama-3.2-11b-vision-preview', 'llama-3.1-8b-instant', 'gemma-7b-it']

print("Testing Groq models...")
for model in models:
    try:
        r = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
            json={'model': model, 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 10},
            timeout=5
        )
        print(f'{model}: {r.status_code}')
        if r.status_code == 200:
            print(f'  ✓ THIS ONE WORKS')
    except Exception as e:
        print(f'{model}: ERROR')
