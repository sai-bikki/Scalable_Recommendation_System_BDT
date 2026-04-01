#!/usr/bin/env python3
import requests
import json

# Test the /event endpoint
session_id = "5faf2d31-a0ff-4e26-bef3-6597acb91478"

try:
    print(f"Testing /event?sessionId={session_id}...\n")
    response = requests.get(f'http://localhost:3000/event?sessionId={session_id}')
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
