import requests
import json

# Test AI service directly
response = requests.post(
    'http://localhost:8000/v1/srs/generate',
    json={'project_input': 'Create a simple task management system with user authentication'}
)

print(f'Status: {response.status_code}')
data = response.json()
provider = data.get('document', {}).get('metadata', {}).get('provider', 'unknown')
title = data.get('document', {}).get('title', 'unknown')

print(f'Provider: {provider}')
print(f'Title: {title}')
print(f'\nFull response:')
print(json.dumps(data, indent=2))
