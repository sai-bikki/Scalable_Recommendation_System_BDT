#!/usr/bin/env python3
"""Debug Flux query for session events"""

from influxdb_client import InfluxDBClient
import os
from dotenv import load_dotenv
import json

load_dotenv()

influx_url = os.getenv('INFLUX_URL', 'http://localhost:8086')
influx_token = os.getenv('INFLUX_TOKEN', 'my-super-secret-token')
influx_org = os.getenv('INFLUX_ORG', 'analytics')

client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
api = client.query_api()

# Try simple query first
query1 = '''
from(bucket: "events")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "clicks")
  |> limit(n: 3)
'''

print("Test 1: All events (no filter)")
result = api.query(query1)
print(f"Tables: {len(result)}")
for i, table in enumerate(result):
    print(f"  Table {i}: {len(table.records)} records")
    if table.records:
        rec = table.records[0]
        print(f"    Sample: {rec.values}")

# Try with session filter
sessionId = "5faf2d31-a0ff-4e26-bef3-6597acb91478"
query2 = f'''
from(bucket: "events")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "clicks")
  |> filter(fn: (r) => r.session_id =~ /^{sessionId[:8]}/)
  |> limit(n: 5)
'''

print(f"\nTest 2: Events for session {sessionId[:8]}...")
result = api.query(query2)
print(f"Tables: {len(result)}")
for i, table in enumerate(result):
    print(f"  Table {i}: {len(table.records)} records, fields: {[c.label for c in table.columns]}")
    if table.records:
        for j, rec in enumerate(table.records[:2]):
            print(f"    Record {j}: field={rec.values.get('_field')} value={rec.values.get('_value')}")
