#!/usr/bin/env python3
"""Show all clicks for a specific session"""

from influxdb_client import InfluxDBClient
import os
from dotenv import load_dotenv
import sys

load_dotenv()

influx_url = os.getenv('INFLUX_URL', 'http://localhost:8086')
influx_token = os.getenv('INFLUX_TOKEN', 'my-super-secret-token')
influx_org = os.getenv('INFLUX_ORG', 'analytics')

client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
query_api = client.query_api()

# Get session ID from command line or use first one
session_id_filter = sys.argv[1] if len(sys.argv) > 1 else "5faf2d31"

flux_query = f'''
from(bucket: "events")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "clicks" and r.session_id =~ /^{session_id_filter}/)
  |> sort(columns: ["_time"])
'''

print(f"Session data (filter: {session_id_filter}):\n")

# Collect events by timestamp
events = {}
records_stream = query_api.query_stream(query=flux_query, org=influx_org)

for record in records_stream:
    values = record.values
    time_key = str(values.get('_time'))
    if time_key not in events:
        events[time_key] = {
            'time': values.get('_time'),
            'session': values.get('session_id'),
            'user': values.get('user_id'),
            'page': values.get('page'),
            'x': None,
            'y': None
        }
    if values.get('_field') == 'x':
        events[time_key]['x'] = values.get('_value')
    elif values.get('_field') == 'y':
        events[time_key]['y'] = values.get('_value')

if not events:
    print("No events found for this session.")
    sys.exit(1)

print(f"Total clicks: {len(events)}\n")
for idx, (time_key, event) in enumerate(sorted(events.items(), reverse=True), 1):
    print(f"{idx:3d}. Time: {event['time']} | X: {event['x']:6.0f} | Y: {event['y']:6.0f} | Page: {event['page']}")

print(f"\nSession: {list(events.values())[0]['session']}")
print(f"User: {list(events.values())[0]['user']}")
