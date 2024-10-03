# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

# from typing import Any, Text, Dict, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from influxdb_client import InfluxDBClient, QueryApi
# from datetime import datetime

# # Initialize InfluxDB client (replace with your connection details)
# INFLUXDB_URL = "http://localhost:8086"
# INFLUXDB_TOKEN = "kjseorOWtRfYjroWzk2CiPFuOHyjRo3Vrtv0JirIzbPLQTWmqRMSuLCDqmVW5jwr6pBWYVWrQxzM838lRzg1nw=="
# INFLUXDB_ORG = "msrit"
# INFLUXDB_BUCKET = "data"

# client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
# query_api = client.query_api()

# class ActionQueryBatteryVoltage(Action):
#     def name(self) -> Text:
#         return "action_query_battery_voltage"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         sensor_id = tracker.get_slot("sensor_id")
#         frame_id = tracker.get_slot("frame_id")

#         query = f'''
#         from(bucket: "{INFLUXDB_BUCKET}")
#           |> range(start: -30d)
#           |> filter(fn: (r) => r["_measurement"] == "sensor_data" and r["OBC0T004_FRAME_ID"] == "{frame_id}")
#           |> filter(fn: (r) => r["_field"] == "PWRS0095_BAT_VOL_FINE_SEL_RT")
#           |> last()
#         '''
#         result = query_api.query(org=INFLUXDB_ORG, query=query)

#         voltage = None
#         for table in result:
#             for record in table.records:
#                 voltage = record.get_value()

#         if voltage:
#             dispatcher.utter_message(text=f"Battery voltage for sensor {sensor_id} at frame ID {frame_id} is {voltage}V.")
#         else:
#             dispatcher.utter_message(text=f"No battery voltage data found for sensor {sensor_id} at frame ID {frame_id}.")

#         return []

# class ActionQuerySensorData(Action):
#     def name(self) -> Text:
#         return "action_query_sensor_data"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         sensor_id = tracker.get_slot("sensor_id")
#         timestamp = tracker.get_slot("timestamp")

#         query = f'''
#         from(bucket: "{INFLUXDB_BUCKET}")
#           |> range(start: {timestamp}, stop: {timestamp})
#           |> filter(fn: (r) => r["_measurement"] == "sensor_data" and r["_time"] == {timestamp})
#         '''
#         result = query_api.query(org=INFLUXDB_ORG, query=query)

#         sensor_data = {}
#         for table in result:
#             for record in table.records:
#                 sensor_data[record.get_field()] = record.get_value()

#         if sensor_data:
#             dispatcher.utter_message(text=f"Sensor data for {sensor_id} at {timestamp}: {sensor_data}")
#         else:
#             dispatcher.utter_message(text=f"No sensor data found for {sensor_id} at {timestamp}.")

#         return []

# class ActionQueryLogicStatus(Action):
#     def name(self) -> Text:
#         return "action_query_logic_status"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         sensor_id = tracker.get_slot("sensor_id")
#         timestamp = tracker.get_slot("timestamp")

#         query = f'''
#         from(bucket: "{INFLUXDB_BUCKET}")
#           |> range(start: {timestamp}, stop: {timestamp})
#           |> filter(fn: (r) => r["_measurement"] == "sensor_data" and r["_field"] == "AOE03030_LPD_LOGIC_STS" and r["_time"] == {timestamp})
#           |> last()
#         '''
#         result = query_api.query(org=INFLUXDB_ORG, query=query)

#         logic_status = None
#         for table in result:
#             for record in table.records:
#                 logic_status = record.get_value()

#         if logic_status:
#             dispatcher.utter_message(text=f"Logic status for sensor {sensor_id} at {timestamp} is {logic_status}.")
#         else:
#             dispatcher.utter_message(text=f"No logic status found for sensor {sensor_id} at {timestamp}.")

#         return []

# class ActionQueryAllData(Action):
#     def name(self) -> Text:
#         return "action_query_all_data"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         sensor_id = tracker.get_slot("sensor_id")
#         frame_id = tracker.get_slot("frame_id")

#         query = f'''
#         from(bucket: "{INFLUXDB_BUCKET}")
#           |> range(start: -30d)
#           |> filter(fn: (r) => r["_measurement"] == "sensor_data" and r["OBC0T004_FRAME_ID"] == "{frame_id}")
#         '''
#         result = query_api.query(org=INFLUXDB_ORG, query=query)

#         data = {}
#         for table in result:
#             for record in table.records:
#                 data[record.get_field()] = record.get_value()

#         if data:
#             dispatcher.utter_message(text=f"All data for sensor {sensor_id} at frame ID {frame_id}: {data}")
#         else:
#             dispatcher.utter_message(text=f"No data found for sensor {sensor_id} at frame ID {frame_id}.")

#         return []


'''program to check the influxdb connection'''

from influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import List, Dict, Any
from datetime import datetime

class InfluxDBConfig:
    """Configuration for InfluxDB connection."""
    TOKEN = "kjseorOWtRfYjroWzk2CiPFuOHyjRo3Vrtv0JirIzbPLQTWmqRMSuLCDqmVW5jwr6pBWYVWrQxzM838lRzg1nw=="
    ORG = "msrit"
    BUCKET = "data"
    URL = "http://localhost:8086"

    @staticmethod
    def get_client() -> InfluxDBClient:
        """Return an InfluxDB client instance."""
        return InfluxDBClient(
            url=InfluxDBConfig.URL, 
            token=InfluxDBConfig.TOKEN, 
            org=InfluxDBConfig.ORG
        )

class InfluxDBQueryHelper:
    """Helper class to perform InfluxDB queries."""
    
    @staticmethod
    def execute_query(query: str) -> List[Dict[str, Any]]:
        """Execute an InfluxDB query and return the result."""
        client = InfluxDBConfig.get_client()
        query_api: QueryApi = client.query_api()

        try:
            result = query_api.query(org=InfluxDBConfig.ORG, query=query)
            return result
        except Exception as e:
            raise ConnectionError(f"Error executing query: {str(e)}")
    
    @staticmethod
    def format_records(result: List) -> List[Dict[str, Any]]:
        """Format the query result into a more readable form."""
        entries = []
        for table in result:
            for record in table.records:
                entry = {
                    "measurement": record.get_measurement(),
                    "time": record.get_time(),
                    "fields": {
                        record.get_field(): record.get_value()
                    },
                    "tags": record.values.get('tags', {})
                }
                entries.append(entry)
        return entries
    


def normalize_time_format(time_str: str) -> str:
    """Normalize the user-provided time to the required format YYYY-MM-DDTHH:MM:SS.SSSZ."""
    try:
        # Replace slashes with dashes for dates
        time_str = time_str.replace("/", "-")

        # Ensure that there's a 'T' between date and time parts
        if "T" not in time_str:
            time_str = time_str.replace(" ", "T")

        # Split the time part from the date part
        date_part, time_part = time_str.split("T")

        # Handle any colons in the time part and make sure milliseconds are separated with a dot
        if time_part.count(":") > 2:
            hours_minutes_seconds = time_part[:time_part.rfind(":")]
            milliseconds = time_part[time_part.rfind(":") + 1:]
            time_part = f"{hours_minutes_seconds}.{milliseconds}"

        # If there are no milliseconds, add ".000"
        if "." not in time_part:
            time_part += ".000"

        # Reassemble the date and time parts
        normalized_time = f"{date_part}T{time_part}"

        # Ensure it ends with 'Z'
        if not normalized_time.endswith("Z"):
            normalized_time += "Z"

        # Validate and parse the string into datetime format, then convert back to the final string format
        parsed_time = datetime.strptime(normalized_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        final_time = parsed_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        return final_time

    except Exception as e:
        raise ValueError(f"Invalid time format: {time_str}. Please provide the time in a valid format (e.g., 2023-08-08T01:49:28.205Z).")


class ActionCalculateAverage(Action):
    """Action to calculate the average battery voltage between specific timestamps provided by the user."""

    def name(self) -> str:
        return "action_calculate_average"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Get start and stop times from user input through tracker
        start_time = tracker.get_slot("start_time")
        stop_time = tracker.get_slot("stop_time")

        if not start_time or not stop_time:
            dispatcher.utter_message(text="Please provide both start and stop times.")
            return []

        # Print debug information for raw input
        print(f"Raw Start Time: {start_time}, Raw Stop Time: {stop_time}")

        # Normalize the time format before using in the query
        try:
            normalized_start_time = normalize_time_format(start_time)
            normalized_stop_time = normalize_time_format(stop_time)
        except ValueError as e:
            dispatcher.utter_message(text=str(e))
            return []

        # Print debug information for normalized time
        print(f"Normalized Start Time: {normalized_start_time}, Normalized Stop Time: {normalized_stop_time}")

        # InfluxDB query for the specific field and time range, with normalized times
        query = f'''
        from(bucket: "{InfluxDBConfig.BUCKET}")
        |> range(start: {normalized_start_time}, stop: {normalized_stop_time})
        |> filter(fn: (r) => r._measurement == "sensor_data" and r._field == "PWRS0095_BAT_VOL_FINE_SEL_RT")
        |> mean()
        '''

        try:
            # Execute the query
            result = InfluxDBQueryHelper.execute_query(query)

            # Check for valid results
            if result and result[0].records:
                average_voltage = result[0].records[0].get_value()
                dispatcher.utter_message(text=f"The average battery voltage (PWRS0095_BAT_VOL_FINE_SEL_RT) between {normalized_start_time} and {normalized_stop_time} is {average_voltage} volts.")
            else:
                dispatcher.utter_message(text="No voltage data found for the specified time range.")
        except ConnectionError as e:
            dispatcher.utter_message(text=f"Connection error: {str(e)}")
        except Exception as e:
            dispatcher.utter_message(text=f"Unexpected error: {str(e)}")

        return []

class ActionCheckConnection(Action):
    """Action to check the connection to InfluxDB and retrieve a few entries."""

    def name(self) -> str:
        return "action_check_connection"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        query = f'from(bucket: "{InfluxDBConfig.BUCKET}") |> range(start: 0) |> limit(n:2)'
        
        try:
            result = InfluxDBQueryHelper.execute_query(query)
            entries = InfluxDBQueryHelper.format_records(result)
            
            if entries:
                dispatcher.utter_message(text=f"Connection Successful! Retrieved entries: {entries}")
            else:
                dispatcher.utter_message(text="No entries found in InfluxDB.")
        except ConnectionError as e:
            dispatcher.utter_message(text=str(e))
        except Exception as e:
            dispatcher.utter_message(text=f"Unexpected error: {str(e)}")
        
        return []


class ActionCalculateChargeAverage(Action):
    """Action to calculate the average battery charge between specific timestamps provided by the user."""

    def name(self) -> str:
        return "action_calculate_charge_average"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Get start and stop times from user input through tracker
        start_time = tracker.get_slot("start_time")
        stop_time = tracker.get_slot("stop_time")

        if not start_time or not stop_time:
            dispatcher.utter_message(text="Please provide both start and stop times.")
            return []

        # Print debug information for raw input
        print(f"Raw Start Time: {start_time}, Raw Stop Time: {stop_time}")

        # Normalize the time format before using in the query
        try:
            normalized_start_time = normalize_time_format(start_time)
            normalized_stop_time = normalize_time_format(stop_time)
        except ValueError as e:
            dispatcher.utter_message(text=str(e))
            return []

        # Print debug information for normalized time
        print(f"Normalized Start Time: {normalized_start_time}, Normalized Stop Time: {normalized_stop_time}")

        # InfluxDB query for the specific field and time range, with normalized times
        query = f'''
        from(bucket: "{InfluxDBConfig.BUCKET}")
        |> range(start: {normalized_start_time}, stop: {normalized_stop_time})
        |> filter(fn: (r) => r._measurement == "sensor_data" and r._field == "PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT")
        |> mean()
        '''

        try:
            # Execute the query
            result = InfluxDBQueryHelper.execute_query(query)

            # Check for valid results
            if result and result[0].records:
                average_charge = result[0].records[0].get_value()
                dispatcher.utter_message(text=f"The average battery charge (PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT) between {normalized_start_time} and {normalized_stop_time} is {average_charge} volts.")
            else:
                dispatcher.utter_message(text="No charge data found for the specified time range.")
        except ConnectionError as e:
            dispatcher.utter_message(text=f"Connection error: {str(e)}")
        except Exception as e:
            dispatcher.utter_message(text=f"Unexpected error: {str(e)}")

        return []





# from influxdb_client import InfluxDBClient
# from influxdb_client.client.query_api import QueryApi
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from typing import List, Dict, Any

# class InfluxDBConfig:
#     """Configuration for InfluxDB connection."""
#     TOKEN = "kjseorOWtRfYjroWzk2CiPFuOHyjRo3Vrtv0JirIzbPLQTWmqRMSuLCDqmVW5jwr6pBWYVWrQxzM838lRzg1nw=="
#     ORG = "msrit"
#     BUCKET = "data"
#     URL = "http://localhost:8086"

#     @staticmethod
#     def get_client() -> InfluxDBClient:
#         """Return an InfluxDB client instance."""
#         return InfluxDBClient(
#             url=InfluxDBConfig.URL, 
#             token=InfluxDBConfig.TOKEN, 
#             org=InfluxDBConfig.ORG
#         )

# class InfluxDBQueryHelper:
#     """Helper class to perform InfluxDB queries."""
    
#     @staticmethod
#     def execute_query(query: str) -> List[Dict[str, Any]]:
#         """Execute an InfluxDB query and return the result."""
#         client = InfluxDBConfig.get_client()
#         query_api: QueryApi = client.query_api()

#         try:
#             result = query_api.query(org=InfluxDBConfig.ORG, query=query)
#             return result
#         except Exception as e:
#             raise ConnectionError(f"Error executing query: {str(e)}")
    
#     @staticmethod
#     def format_records(result: List) -> List[Dict[str, Any]]:
#         """Format the query result into a more readable form."""
#         entries = []
#         for table in result:
#             for record in table.records:
#                 entry = {
#                     "measurement": record.get_measurement(),
#                     "time": record.get_time(),
#                     "fields": {
#                         record.get_field(): record.get_value()
#                     },
#                     "tags": record.values.get('tags', {})
#                 }
#                 entries.append(entry)
#         return entries

# class ActionCheckConnection(Action):
#     """Action to check the connection to InfluxDB and retrieve a few entries."""

#     def name(self) -> str:
#         return "action_check_connection"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:
#         query = f'from(bucket: "{InfluxDBConfig.BUCKET}") |> range(start: 0) |> limit(n:2)'
        
#         try:
#             result = InfluxDBQueryHelper.execute_query(query)
#             entries = InfluxDBQueryHelper.format_records(result)
            
#             if entries:
#                 dispatcher.utter_message(text=f"Connection Successful! Retrieved entries: {entries}")
#             else:
#                 dispatcher.utter_message(text="No entries found in InfluxDB.")
#         except ConnectionError as e:
#             dispatcher.utter_message(text=str(e))
#         except Exception as e:
#             dispatcher.utter_message(text=f"Unexpected error: {str(e)}")
        
#         return []

# class ActionCalculateAverage(Action):
#     """Action to calculate the average battery voltage and handle other fields between specific timestamps."""

#     def name(self) -> str:
#         return "action_calculate_average"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:
#         # Define start and stop times for the query
#         start_time = "2023-08-08T01:49:04.654Z"
#         stop_time = "2023-08-08T07:59:59.602Z"

#         # InfluxDB query for multiple fields and time range
#         query = f'''
#         from(bucket: "{InfluxDBConfig.BUCKET}")
#         |> range(start: {start_time}, stop: {stop_time})
#         |> filter(fn: (r) => r._measurement == "sensor_data" and
#                               (r._field == "PWRS0095_BAT_VOL_FINE_SEL_RT" or
#                                r._field == "PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT" or
#                                r._field == "AOE03030_LPD_LOGIC_STS"))
#         |> group(columns: ["_field"])
#         |> mean(column: "_value")
#         '''

#         try:
#             # Execute the query
#             result = InfluxDBQueryHelper.execute_query(query)
#             formatted_result = InfluxDBQueryHelper.format_records(result)

#             # Extract values for each field
#             battery_voltage = next((entry['fields'].get('PWRS0095_BAT_VOL_FINE_SEL_RT') for entry in formatted_result if 'PWRS0095_BAT_VOL_FINE_SEL_RT' in entry['fields']), None)
#             charge_current = next((entry['fields'].get('PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT') for entry in formatted_result if 'PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT' in entry['fields']), None)
#             logic_status = next((entry['fields'].get('AOE03030_LPD_LOGIC_STS') for entry in formatted_result if 'AOE03030_LPD_LOGIC_STS' in entry['fields']), None)

#             # Create a response based on the available data
#             response_message = f"Average battery voltage: {battery_voltage} volts\n"
#             response_message += f"Average charge current: {charge_current} A\n"

#             # Handle string value (logic status)
#             if logic_status:
#                 response_message += f"Logic status: {logic_status}"

#             dispatcher.utter_message(text=response_message)
#         except ConnectionError as e:
#             dispatcher.utter_message(text=f"Connection error: {str(e)}")
#         except Exception as e:
#             dispatcher.utter_message(text=f"Unexpected error: {str(e)}")

        # return []
