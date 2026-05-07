import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('GROQ_API_KEY')

response = requests.post(
    'https://api.groq.com/openai/v1/chat/completions',
    headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    },
    json={
        'model': 'llama-3.1-70b-versatile',
        'messages': [{'role': 'user', 'content': 'test'}],
        'max_tokens': 100
    }
)

print(f'Status: {response.status_code}')
print(f'Response: {response.text}')

