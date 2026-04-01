#!/usr/bin/env python3
import requests
import json

try:
    print("Testing /event/recent endpoint...")
    response = requests.get('http://localhost:3000/event/recent?limit=5')
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Events found: {data['count']}")
    
    for i, event in enumerate(data['events'][:5], 1):
        print(f"{i}. Time: {event['timestamp']} | X: {event['x']} Y: {event['y']}")
    
except Exception as e:
    print(f"Error: {e}")
