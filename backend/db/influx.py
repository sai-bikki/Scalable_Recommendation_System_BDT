from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
from dotenv import load_dotenv

load_dotenv()

client = None
write_api = None
query_api = None

def connect_influx():
    global client, write_api, query_api
    
    influx_url = os.getenv('INFLUX_URL', 'http://localhost:8086')
    influx_token = os.getenv('INFLUX_TOKEN', 'my-super-secret-token')
    influx_org = os.getenv('INFLUX_ORG', 'analytics')
    
    client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
    write_api = client.write_api(write_type=SYNCHRONOUS)
    query_api = client.query_api()
    print('✅ InfluxDB connected')

def get_write_api():
    return write_api

def get_query_api():
    return query_api

def get_point():
    return Point

def close_influx():
    if client:
        client.close()
