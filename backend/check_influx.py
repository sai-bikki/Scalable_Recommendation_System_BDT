#!/usr/bin/env python3
"""Quick script to check InfluxDB stored data"""

from influxdb_client import InfluxDBClient
import os
from dotenv import load_dotenv

load_dotenv()

def check_influx_data():
    # Connect to InfluxDB
    influx_url = os.getenv('INFLUX_URL', 'http://localhost:8086')
    influx_token = os.getenv('INFLUX_TOKEN', 'my-super-secret-token')
    influx_org = os.getenv('INFLUX_ORG', 'analytics')
    
    client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
    query_api = client.query_api()
    
    # Query all clicks in the last 30 days
    flux_query = '''
    from(bucket: "events")
      |> range(start: -30d)
      |> filter(fn: (r) => r._measurement == "clicks")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: 100)
    '''
    
    print("InfluxDB Data (Last 100 clicks):\n")
    
    # Collect all events in a dict keyed by timestamp
    events_by_time = {}
    
    # Query x and y fields separately (InfluxDB returns them in different tables)
    flux_query = '''
    from(bucket: "events")
      |> range(start: -30d)
      |> filter(fn: (r) => r._measurement == "clicks")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: 100)
    '''
    
    records_stream = query_api.query_stream(query=flux_query, org=influx_org)
    
    for record in records_stream:
        values = record.values
        time_key = str(values.get('_time'))
        
        # Initialize or update event
        if time_key not in events_by_time:
            events_by_time[time_key] = {
                '_time': values.get('_time'),
                'session_id': values.get('session_id'),
                'user_id': values.get('user_id'),
                'page': values.get('page'),
                'x': None,
                'y': None
            }
        
        # Fill in x or y based on _field
        field = values.get('_field')
        if field == 'x':
            events_by_time[time_key]['x'] = values.get('_value')
        elif field == 'y':
            events_by_time[time_key]['y'] = values.get('_value')
    
    row_count = 0
    for event in events_by_time.values():
        row_count += 1
        print(f"[{row_count}] Time: {event['_time']} | "
              f"Session: {str(event['session_id'])[:8]}... | "
              f"User: {str(event['user_id'])[:8]}... | "
              f"X: {event['x']}, Y: {event['y']} | "
              f"Page: {event['page']}")
    
    if row_count == 0:
        print("No data found in InfluxDB yet.")
        print("\nTo generate data:")
        print("   1. Visit http://localhost:3000/demo")
        print("   2. Click some buttons on the demo page")
        print("   3. Then run this script again")
    else:
        print(f"\nFound {row_count} click events in InfluxDB")
    
    client.close()

if __name__ == "__main__":
    check_influx_data()
