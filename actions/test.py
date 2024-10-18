from influxdb_client import InfluxDBClient, QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS

# Define your InfluxDB connection details
url = "http://localhost:8086"  # Your InfluxDB instance URL
token = "kjseorOWtRfYjroWzk2CiPFuOHyjRo3Vrtv0JirIzbPLQTWmqRMSuLCDqmVW5jwr6pBWYVWrQxzM838lRzg1nw=="  # Your InfluxDB authentication token
org = "msrit"  # Your InfluxDB organization
bucket = "data"  # Your InfluxDB bucket

# Initialize InfluxDB client
client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

# Define your time range
start_time = "2023-08-08T01:49:04.654Z"
stop_time = "2023-08-08T07:59:59.602Z"

# Flux query to fetch battery voltage when frame ID is 15
query = f'''
from(bucket: "{bucket}")
  |> range(start: {start_time}, stop: {stop_time})
  |> filter(fn: (r) => r._measurement == "sensor_data" and 
                       r._field == "PWRS0095_BAT_VOL_FINE_SEL_RT" and 
                       r.OBC0T004_FRAME_ID == "15")
'''

# Execute the query
result = query_api.query(org=org, query=query)

# Process and print the result
if result:
    for table in result:
        for record in table.records:
            print(f"Time: {record.get_time()}, Battery Voltage: {record.get_value()}")
else:
    print("No data found matching the query.")

# Close the client connection
client.close()
