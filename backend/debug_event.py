#!/usr/bin/env python3
"""Debug: inspect actual event data stored in InfluxDB"""

from influxdb_client import InfluxDBClient
import os
from dotenv import load_dotenv

load_dotenv()

influx_url = os.getenv('INFLUX_URL', 'http://localhost:8086')
influx_token = os.getenv('INFLUX_TOKEN', 'my-super-secret-token')
influx_org = os.getenv('INFLUX_ORG', 'analytics')

client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
api = client.query_api()

query = '''
from(bucket: "events")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "clicks")
  |> limit(n: 3)
'''

print("Fetching raw event data from InfluxDB...\n")
result = api.query(query)

for table_idx, table in enumerate(result):
    print(f"Table {table_idx}:")
    print(f"  Columns: {[col.label for col in table.columns]}")
    print(f"  Records: {len(table.records)}\n")
    
    for rec_idx, record in enumerate(table.records):
        print(f"  Record {rec_idx + 1}:")
        print(f"    Time: {record.values.get('_time')}")
        print(f"    Measurement: {record.values.get('_measurement')}")
        print(f"    Field: {record.values.get('_field')} = {record.values.get('_value')}")
        print(f"    Tags: user={record.values.get('user_id')}, session={record.values.get('session_id')}")
        print(f"    Page: {record.values.get('page')}")
        print()
