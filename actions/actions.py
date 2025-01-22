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

'''program to check the influxdb connection'''

from influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from sanic import Sanic
from sanic.response import file, empty
import os

static_file_path = r"E:\rasa2\static\graphs"

app = Sanic.get_app()  # Get the Sanic app instance

@app.route("/static/graphs/<filename>")
async def serve_static(request, filename):
    file_path = os.path.join(static_file_path, filename)
    if os.path.exists(file_path):
        return await file(file_path)
    return {"error": f"File '{filename}' not found."}, 404

@app.route("/favicon.ico")
async def favicon(request):
    # You can replace this path with the actual path to your favicon file
    return empty()  # Return an empty response to stop the error

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
        
class ActionQueryMin(Action):
    """Action to query the min value of various sensor data fields within a specified time range.""" 
    
    # Dictionary to map user-friendly terms to InfluxDB field names
    field_mapping = {
        "voltage": "PWRS0095_BAT_VOL_FINE_SEL_RT",
        "charge": "PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT",
        "logic status": "AOE03030_LPD_LOGIC_STS",
        "frame id": "OBC0T004_FRAME_ID"
    }

    def name(self) -> str:
        return "action_query_min"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:

        # Get start, stop times, and field from user input through tracker
        start_time = tracker.get_slot("start_time")
        stop_time = tracker.get_slot("stop_time")
        field = tracker.get_slot("field")

        if not start_time or not stop_time or not field:
            dispatcher.utter_message(text="Please provide start time, stop time, and the field.")
            return []

        # Print debug information for raw input
        print(f"Raw Start Time: {start_time}, Raw Stop Time: {stop_time}, Field: {field}")

        # Map user-friendly field name to InfluxDB field name
        influxdb_field = self.field_mapping.get(field.lower())

        if influxdb_field is None:
            dispatcher.utter_message(text=f"Sorry, I don't recognize the field '{field}'. Please provide a valid field.")
            return []

        # Normalize the time format before using in the query
        try:
            normalized_start_time = normalize_time_format(start_time)
            normalized_stop_time = normalize_time_format(stop_time)
        except ValueError as e:
            dispatcher.utter_message(text=str(e))
            return []

        # Print debug information for normalized time and field
        print(f"Normalized Start Time: {normalized_start_time}, Normalized Stop Time: {normalized_stop_time}, Field: {influxdb_field}")

        # InfluxDB query for the specific field and time range, with normalized times
        query = f'''
        from(bucket: "{InfluxDBConfig.BUCKET}")
        |> range(start: {normalized_start_time}, stop: {normalized_stop_time})
        |> filter(fn: (r) => r._measurement == "sensor_data" and r._field == "{influxdb_field}")
        |> min()
        '''

        print(f"{query}")

        try:
            # Execute the query
            result = InfluxDBQueryHelper.execute_query(query)

            # Check for valid results
            if result and result[0].records:
                min_value = result[0].records[0].get_value()
                dispatcher.utter_message(text=f"The minimum value for {field} between {normalized_start_time} and {normalized_stop_time} is {min_value}.")
            else:
                dispatcher.utter_message(text=f"No data found for {field} in the specified time range.")
        except ConnectionError as e:
            dispatcher.utter_message(text=f"Connection error: {str(e)}")
        except Exception as e:
            dispatcher.utter_message(text=f"Unexpected error: {str(e)}")

        return []

class ActionQueryMax(Action):
    """Action to query the max value of various sensor data fields within a specified time range.""" 
    
    # Dictionary to map user-friendly terms to InfluxDB field names
    field_mapping = {
        "voltage": "PWRS0095_BAT_VOL_FINE_SEL_RT",
        "charge": "PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT",
        "logic status": "AOE03030_LPD_LOGIC_STS",
        "frame id": "OBC0T004_FRAME_ID"
    }

    def name(self) -> str:
        return "action_query_max"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:

        # Get start, stop times, and field from user input through tracker
        start_time = tracker.get_slot("start_time")
        stop_time = tracker.get_slot("stop_time")
        field = tracker.get_slot("field")

        if not start_time or not stop_time or not field:
            dispatcher.utter_message(text="Please provide start time, stop time, and the field.")
            return []

        # Print debug information for raw input
        print(f"Raw Start Time: {start_time}, Raw Stop Time: {stop_time}, Field: {field}")

        # Map user-friendly field name to InfluxDB field name
        influxdb_field = self.field_mapping.get(field.lower())

        if influxdb_field is None:
            dispatcher.utter_message(text=f"Sorry, I don't recognize the field '{field}'. Please provide a valid field.")
            return []

        # Normalize the time format before using in the query
        try:
            normalized_start_time = normalize_time_format(start_time)
            normalized_stop_time = normalize_time_format(stop_time)
        except ValueError as e:
            dispatcher.utter_message(text=str(e))
            return []

        # Print debug information for normalized time and field
        print(f"Normalized Start Time: {normalized_start_time}, Normalized Stop Time: {normalized_stop_time}, Field: {influxdb_field}")

        # InfluxDB query for the specific field and time range, with normalized times
        query = f'''
        from(bucket: "{InfluxDBConfig.BUCKET}")
        |> range(start: {normalized_start_time}, stop: {normalized_stop_time})
        |> filter(fn: (r) => r._measurement == "sensor_data" and r._field == "{influxdb_field}")
        |> max()
        '''

        print(f"{query}")

        try:
            # Execute the query
            result = InfluxDBQueryHelper.execute_query(query)

            # Check for valid results
            if result and result[0].records:
                min_value = result[0].records[0].get_value()
                dispatcher.utter_message(text=f"The maximum value for {field} between {normalized_start_time} and {normalized_stop_time} is {min_value}.")
            else:
                dispatcher.utter_message(text=f"No data found for {field} in the specified time range.")
        except ConnectionError as e:
            dispatcher.utter_message(text=f"Connection error: {str(e)}")
        except Exception as e:
            dispatcher.utter_message(text=f"Unexpected error: {str(e)}")

        return []


class ActionQueryCheck(Action):
    """Action to check query of various sensor data fields within a specified time range.""" 

    def name(self) -> str:
        return "action_query_check"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Define the InfluxDB query
        query = '''
        from(bucket: "data")
        |> range(start: 2023-08-08T01:49:04.654Z, stop: 2023-08-08T07:59:59.602Z)
        |> filter(fn: (r) => r._measurement == "sensor_data")
        |> filter(fn: (r) => r._field == "PWRS0095_BAT_VOL_FINE_SEL_RT" or r._field == "PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> filter(fn: (r) => r.PWRS0095_BAT_VOL_FINE_SEL_RT == 8)
        |> keep(columns: ["_time", "PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT"])
        '''

        try:
            # Execute the query
            result = InfluxDBQueryHelper.execute_query(query)

            # Format results for Rasa output
            if result:
                formatted_results = []
                for record in result[0].records:
                    time = record.get_time().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                    voltage = record.values.get("PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT", "N/A")
                    formatted_results.append(f"Time: {time}, Charge Current: {voltage}")

                # Send the formatted output to the user
                if formatted_results:
                    dispatcher.utter_message(text="\n".join(formatted_results))
                else:
                    dispatcher.utter_message(text="No matching data found for the specified query.")

            else:
                dispatcher.utter_message(text="No data returned from the query.")

        except ConnectionError as e:
            dispatcher.utter_message(text=f"Connection error: {str(e)}")
        except Exception as e:
            dispatcher.utter_message(text=f"Unexpected error: {str(e)}")

        return []
    
class ActionQueryFieldCondition(Action):
    """Action to query specific fields based on conditions between measurements."""

    field_mapping = {
        "voltage": "PWRS0095_BAT_VOL_FINE_SEL_RT",
        "charge": "PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT",
        "logic status": "AOE03030_LPD_LOGIC_STS",
        "frame id": "OBC0T004_FRAME_ID"
    }

    def name(self) -> str:
        return "action_query_field_condition"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Retrieve user-provided parameters
        condition_field = tracker.get_slot("condition_field")  # e.g., "frame id"
        condition_value = tracker.get_slot("condition_value")  # e.g., 5
        field = tracker.get_slot("field")        # e.g., "voltage"
        start_time = tracker.get_slot("start_time")
        stop_time = tracker.get_slot("stop_time")

        # Validate input
        if not condition_field or not condition_value or not field or not start_time or not stop_time:
            dispatcher.utter_message(text="Please provide all required fields: condition field, condition value, target field, start time, and stop time.")
            return []

        # Map user-friendly field names to InfluxDB field names
        condition_influxdb_field = self.field_mapping.get(condition_field.lower())
        target_influxdb_field = self.field_mapping.get(field.lower())

        if not condition_influxdb_field or not target_influxdb_field:
            dispatcher.utter_message(text="One of the provided fields is not recognized. Please use valid field names like 'voltage', 'charge', 'logic status', or 'frame id'.")
            return []

        # Normalize time formats
        try:
            normalized_start_time = normalize_time_format(start_time)
            normalized_stop_time = normalize_time_format(stop_time)
        except ValueError as e:
            dispatcher.utter_message(text=str(e))
            return []

        # Format the condition value for the query
        if isinstance(condition_value, str) and condition_field.lower() == "logic status":
            condition_value = f'"{condition_value}"'  # For string values, use double quotes

        # Construct the InfluxDB query
        query = f'''
        from(bucket: "{InfluxDBConfig.BUCKET}")
        |> range(start: {normalized_start_time}, stop: {normalized_stop_time})
        |> filter(fn: (r) => r._measurement == "sensor_data")
        |> filter(fn: (r) => r._field == "PWRS0095_BAT_VOL_FINE_SEL_RT" or r._field == "PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT" or r._field == "AOE03030_LPD_LOGIC_STS" or r._field == "OBC0T004_FRAME_ID")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> filter(fn: (r) => r.{condition_influxdb_field} == {condition_value})
        |> keep(columns: ["_time", "{condition_influxdb_field}","{target_influxdb_field}"])
        '''

        print(f"Constructed Query: {query}")

        try:
            # Execute the query
            result = InfluxDBQueryHelper.execute_query(query)
            formatted_result = self.format_records(result)
            # entries = InfluxDBQueryHelper.format_records(result)
            

            # Handle the query result
            if formatted_result :
                dispatcher.utter_message(text=formatted_result)
            else:
                dispatcher.utter_message(text=f"No data found for specified query.")
            
        except ConnectionError as e:
            dispatcher.utter_message(text=f"Connection error: {str(e)}")
        except Exception as e:
            dispatcher.utter_message(text=f"Unexpected error: {str(e)}")
            print(f"result :{result}")

        return []
    
    def format_records(self, result):
        """Format the InfluxDB result into a user-friendly string."""
        if not result:
            return "No data available for the specified query."

        output_lines = ["Results:"]
        for table in result:
            for record in table.records:
                # Extract relevant information from the record
                time = record.get_time().strftime("%Y-%m-%d %H:%M:%S UTC")  # Format time for clarity
                battery_voltage = record.values.get("PWRS0095_BAT_VOL_FINE_SEL_RT", "N/A")
                charge_current = record.values.get("PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT", "N/A")
                logic_status = record.values.get("AOE03030_LPD_LOGIC_STS", "N/A")
                frame_id = record.values.get("OBC0T004_FRAME_ID", "N/A")

                # Construct a user-friendly line
                output_lines.append(
                    f"Time: {time}\n"
                    f"  - Battery Voltage: {battery_voltage} V\n"
                    f"  - Charge Current: {charge_current} A\n"
                    f"  - Logic Status: {logic_status}\n"
                    f"  - Frame ID: {frame_id}"
                )

        return "\n".join(output_lines)

# class ActionOperators(Action):
#     """Action to query the operators value of various sensor data fields within a specified time range.""" 
    
#     # Dictionary to map user-friendly terms to InfluxDB field names
#     field_mapping = {
#         "voltage": "PWRS0095_BAT_VOL_FINE_SEL_RT",
#         "charge": "PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT",
#         "logic status": "AOE03030_LPD_LOGIC_STS",
#         "frame id": "OBC0T004_FRAME_ID"
#     }
#     operator_mapping = {
#         "equals": "==",
#         "not equals": "!=",
#         "greater than": ">",
#         "less than": "<",
#         "greater than or equal to": ">=",
#         "less than or equal to": "<="
#     }
#     # log_operator_mapping = {
#     #     "and": "AND",
#     #     "or":"OR"
#     # }

#     def name(self) -> str:
#         return "action_query_operators"
    
#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:

#         # Get start, stop times, and field from user input through tracker
#         start_time = tracker.get_slot("start_time")
#         stop_time = tracker.get_slot("stop_time")
#         field = tracker.get_slot("field")
#         # log_operator = tracker.get_slot("log_operator")
#         operator = tracker.get_slot("operator")
#         condition_value = tracker.get_slot("condition_value")

        
#         if not start_time or not stop_time or not field:
#             dispatcher.utter_message(text="Please provide start time, stop time, and the field.")
#             return []

#         # Print debug information for raw input
#         print(f"Raw Start Time: {start_time}, Raw Stop Time: {stop_time}, Field: {field}")

#         # Map user-friendly field name to InfluxDB field name
#         influxdb_field = self.field_mapping.get(field.lower())
#         # influxdb_log_operator = self.log_operator_mapping.get(field.lower())
#         influxdb_operator = self.operator_mapping.get(operator.lower())

#         if influxdb_field is None:
#             dispatcher.utter_message(text=f"Sorry, I don't recognize the field '{field}'. Please provide a valid field.")
#             return []
        
#         # if influxdb_log_operator is None:
#         #     dispatcher.utter_message(text=f"Sorry, I don't recognize the logical operator '{log_operator}'. Please provide a valid logical operator.")
#         #     return []
        
#         if influxdb_operator is None:
#             dispatcher.utter_message(text=f"Sorry, I don't recognize the operator '{operator}'. Please provide a valid operator.")
#             return []

#         # Normalize the time format before using in the query
#         try:
#             normalized_start_time = normalize_time_format(start_time)
#             normalized_stop_time = normalize_time_format(stop_time)
#         except ValueError as e:
#             dispatcher.utter_message(text=str(e))
#             return []

#         # Print debug information for normalized time and field
#         print(f"Normalized Start Time: {normalized_start_time}, Normalized Stop Time: {normalized_stop_time}, Field: {influxdb_field}, operator: {influxdb_operator}")

#         # Format the condition value for the query
#         if isinstance(condition_value, str) and field.lower() == "logic status":
#             condition_value = f'"{condition_value}"'  # For string values, use double quotes

#         # InfluxDB query for the specific field and time range, with normalized times
#         query = f'''
#         from(bucket: "{InfluxDBConfig.BUCKET}")
#         |> range(start: {normalized_start_time}, stop: {normalized_stop_time})
#         |> filter(fn: (r) => r._measurement == "sensor_data")
#         |> filter(fn: (r) => r._field == "{influxdb_field}")
#         |> filter(fn: (r) => r._value {influxdb_operator} {condition_value})
#         |> keep(columns: ["_time", "_value"])
#         '''

#         print(f"Constructed Query: {query}")

#         try:
#             # Execute the query
#             result = InfluxDBQueryHelper.execute_query(query)

#             # Check for valid results
#             if result and result[0].records:
#                 table_data = []
#                 for record in result[0].records:
#                     row = {
#                         "timestamp": record.get_time(),
#                         "value": record.get_value()
#                     }
#                     table_data.append(row)
#                 table_display = "Timestamp\t\tValue\n"
#                 for row in table_data:
#                     table_display += f"{row['timestamp']}\t{row['value']}\n"  # Format each row as "timestamp\tvalue"
#                 dispatcher.utter_message(text=f"The values for {field} between {normalized_start_time} and {normalized_stop_time} are:\n{table_display}")
#             else:
#                 dispatcher.utter_message(text=f"No data found for {field} in the specified time range.")
#         except ConnectionError as e:
#             dispatcher.utter_message(text=f"Connection error: {str(e)}")
#         except Exception as e:
#             dispatcher.utter_message(text=f"Unexpected error: {str(e)}")

#         return []

# class ActionOperators(Action):
#     """Action to query the operators value of various sensor data fields within a specified time range."""

#     # Dictionary to map user-friendly terms to InfluxDB field names
#     field_mapping = {
#         "voltage": "PWRS0095_BAT_VOL_FINE_SEL_RT",
#         "charge": "PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT",
#         "logic status": "AOE03030_LPD_LOGIC_STS",
#         "frame id": "OBC0T004_FRAME_ID"
#     }
#     operator_mapping = {
#         "equals": "==",
#         "not equals": "!=",
#         "greater than": ">",
#         "less than": "<",
#         "greater than or equal to": ">=",
#         "less than or equal to": "<="
#     }

#     def name(self) -> str:
#         return "action_query_operators"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:
#         start_time = tracker.get_slot("start_time")
#         stop_time = tracker.get_slot("stop_time")
#         field = tracker.get_slot("field")
#         operator = tracker.get_slot("operator")
#         condition_value = tracker.get_slot("condition_value")

#         if not start_time or not stop_time or not field:
#             dispatcher.utter_message(text="Please provide start time, stop time, and the field.")
#             return []

#         influxdb_field = self.field_mapping.get(field.lower())
#         influxdb_operator = self.operator_mapping.get(operator.lower())

#         if influxdb_field is None or influxdb_operator is None:
#             dispatcher.utter_message(text="Invalid field or operator. Please try again.")
#             return []

#         try:
#             normalized_start_time = normalize_time_format(start_time)
#             normalized_stop_time = normalize_time_format(stop_time)
#         except ValueError as e:
#             dispatcher.utter_message(text=str(e))
#             return []

#         if isinstance(condition_value, str) and field.lower() == "logic status":
#             condition_value = f'"{condition_value}"'

#         query = f'''
#         from(bucket: "{InfluxDBConfig.BUCKET}")
#         |> range(start: {normalized_start_time}, stop: {normalized_stop_time})
#         |> filter(fn: (r) => r._measurement == "sensor_data")
#         |> filter(fn: (r) => r._field == "{influxdb_field}")
#         |> filter(fn: (r) => r._value {influxdb_operator} {condition_value})
#         |> keep(columns: ["_time", "_value"])
#         '''

#         try:
#             result = InfluxDBQueryHelper.execute_query(query)

#             if result and result[0].records:
#                 # Prepare data for table formatting
#                 table_data = [
#                     {"Timestamp": record.get_time(), "Value": record.get_value()}
#                     for record in result[0].records
#                 ]

#                 # Generate formatted table
#                 formatted_table = self.format_table(table_data, headers=["Timestamp", "Value"])

#                 dispatcher.utter_message(
#                     text=f"The values for {field} between {normalized_start_time} and {normalized_stop_time} are:\n\n{formatted_table}"
#                 )
#             else:
#                 dispatcher.utter_message(text=f"No data found for {field} in the specified time range.")
#         except ConnectionError as e:
#             dispatcher.utter_message(text=f"Connection error: {str(e)}")
#         except Exception as e:
#             dispatcher.utter_message(text=f"Unexpected error: {str(e)}")

#         return []

#     def format_table(self, data: list[dict], headers: list[str]) -> str:
#         """
#         Format data as a table string.

#         Args:
#             data (list[dict]): List of dictionaries with data to format.
#             headers (list[str]): List of header names.

#         Returns:
#             str: Formatted table as a string.
#         """
#         table = f"{' | '.join(headers)}\n"
#         table += "-" * (len(table) + 3 * len(headers)) + "\n"
#         for row in data:
#             row_values = [str(row.get(header, '')) for header in headers]
#             table += f"{' | '.join(row_values)}\n"
#         return table

# class ActionOperators(Action):
#     """Action to query sensor data fields within a specified time range and send graph data for frontend rendering."""

#     # Field and operator mappings
#     field_mapping = {
#         "voltage": "PWRS0095_BAT_VOL_FINE_SEL_RT",
#         "charge": "PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT",
#         "logic status": "AOE03030_LPD_LOGIC_STS",
#         "frame id": "OBC0T004_FRAME_ID"
#     }

#     operator_mapping = {
#         "equals": "==",
#         "not equals": "!=",
#         "greater than": ">",
#         "less than": "<",
#         "greater than or equal to": ">=",
#         "less than or equal to": "<="
#     }

#     def name(self) -> str:
#         return "action_query_operators"

#     def normalize_time_format(self, time_str: str) -> str:
#         """Normalize the user-provided time to the required format."""
#         try:
#             # Replace slashes with dashes for dates
#             time_str = time_str.replace("/", "-")

#             # Ensure that there's a 'T' between date and time parts
#             if "T" not in time_str:
#                 time_str = time_str.replace(" ", "T")

#             # Split the time part from the date part
#             date_part, time_part = time_str.split("T")

#             # Handle any colons in the time part and make sure milliseconds are separated with a dot
#             if time_part.count(":") > 2:
#                 hours_minutes_seconds = time_part[:time_part.rfind(":")]
#                 milliseconds = time_part[time_part.rfind(":") + 1:]
#                 time_part = f"{hours_minutes_seconds}.{milliseconds}"

#             # If there are no milliseconds, add ".000"
#             if "." not in time_part:
#                 time_part += ".000"

#             # Reassemble the date and time parts
#             normalized_time = f"{date_part}T{time_part}"

#             # Ensure it ends with 'Z'
#             if not normalized_time.endswith("Z"):
#                 normalized_time += "Z"

#             # Validate and parse the string into datetime format, then convert back to the final string format
#             parsed_time = datetime.strptime(normalized_time, "%Y-%m-%dT%H:%M:%S.%fZ")
#             final_time = parsed_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
#             return final_time

#         except Exception as e:
#             raise ValueError(f"Invalid time format: {time_str}. Please provide the time in a valid format (e.g., 2023-08-08T01:49:28.205Z).")

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:
#         # Retrieve slots from tracker
#         start_time = tracker.get_slot("start_time")
#         stop_time = tracker.get_slot("stop_time")
#         field = tracker.get_slot("field")
#         operator = tracker.get_slot("operator")
#         condition_value = tracker.get_slot("condition_value")

#         # Validate mandatory inputs
#         if not start_time or not stop_time or not field:
#             dispatcher.utter_message(text="Please provide start time, stop time, and the field.")
#             return []

#         # Map field and operator
#         influxdb_field = self.field_mapping.get(field.lower())
#         influxdb_operator = self.operator_mapping.get(operator.lower())

#         if influxdb_field is None:
#             dispatcher.utter_message(text=f"Sorry, I don't recognize the field '{field}'. Please provide a valid field.")
#             return []

#         if influxdb_operator is None:
#             dispatcher.utter_message(text=f"Sorry, I don't recognize the operator '{operator}'. Please provide a valid operator.")
#             return []

#         try:
#             normalized_start_time = self.normalize_time_format(start_time)
#             normalized_stop_time = self.normalize_time_format(stop_time)
#         except ValueError as e:
#             dispatcher.utter_message(text=str(e))
#             return []

#         # Mocked data for demo purposes (replace with database query results)
#         timestamps = ["2024-01-01T12:00:00Z", "2024-01-01T12:01:00Z", "2024-01-01T12:02:00Z"]
#         values = [50, 55, 60]

#         if timestamps and values:
#             graph_data = [{"name": t, "value": v} for t, v in zip(timestamps, values)]
#             dispatcher.utter_message(
#                 text=f"Here is the graph for '{field}' between {start_time} and {stop_time}.",
#                 custom={"graph_data": graph_data}  # Custom payload for frontend
#             )
#         else:
#             dispatcher.utter_message(
#                 text=f"No data found for '{field}' in the specified time range."
#             )

#         return []

class ActionOperators(Action):
    """Action to query sensor data fields within a specified time range and send graph data for frontend rendering."""

    # Field and operator mappings
    field_mapping = {
        "voltage": "PWRS0095_BAT_VOL_FINE_SEL_RT",
        "charge": "PWRS0089_BAT_CHRG_CUR_TCR_SEL_RT",
        "logic status": "AOE03030_LPD_LOGIC_STS",
        "frame id": "OBC0T004_FRAME_ID"
    }

    operator_mapping = {
        "equals": "==",
        "not equals": "!=",
        "greater than": ">",
        "less than": "<",
        "greater than or equal to": ">=",
        "less than or equal to": "<="
    }

    def name(self) -> str:
        return "action_query_operators"

    def normalize_time_format(self, time_str: str) -> str:
        """Normalize the user-provided time to the required format."""
        try:
            time_str = time_str.replace("/", "-")
            if "T" not in time_str:
                time_str = time_str.replace(" ", "T")
            date_part, time_part = time_str.split("T")
            if time_part.count(":") > 2:
                hours_minutes_seconds = time_part[:time_part.rfind(":")]
                milliseconds = time_part[time_part.rfind(":") + 1:]
                time_part = f"{hours_minutes_seconds}.{milliseconds}"
            if "." not in time_part:
                time_part += ".000"
            normalized_time = f"{date_part}T{time_part}"
            if not normalized_time.endswith("Z"):
                normalized_time += "Z"
            parsed_time = datetime.strptime(normalized_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            final_time = parsed_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            return final_time
        except Exception as e:
            raise ValueError(f"Invalid time format: {time_str}. Please provide the time in a valid format.")

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Retrieve slots from tracker
        start_time = tracker.get_slot("start_time")
        stop_time = tracker.get_slot("stop_time")
        field = tracker.get_slot("field")
        operator = tracker.get_slot("operator")
        condition_value = tracker.get_slot("condition_value")

        # Validate mandatory inputs
        if not start_time or not stop_time or not field:
            dispatcher.utter_message(text="Please provide start time, stop time, and the field.")
            return []

        # Map field and operator
        influxdb_field = self.field_mapping.get(field.lower())
        influxdb_operator = self.operator_mapping.get(operator.lower())

        if influxdb_field is None:
            dispatcher.utter_message(text=f"Sorry, I don't recognize the field '{field}'. Please provide a valid field.")
            return []

        if influxdb_operator is None:
            dispatcher.utter_message(text=f"Sorry, I don't recognize the operator '{operator}'. Please provide a valid operator.")
            return []

        try:
            normalized_start_time = self.normalize_time_format(start_time)
            normalized_stop_time = self.normalize_time_format(stop_time)
        except ValueError as e:
            dispatcher.utter_message(text=str(e))
            return []

        # Format condition value for string fields
        if isinstance(condition_value, str) and field.lower() == "logic status":
            condition_value = f'"{condition_value}"'

        # InfluxDB query
        query = f'''
        from(bucket: "{InfluxDBConfig.BUCKET}")
        |> range(start: {normalized_start_time}, stop: {normalized_stop_time})
        |> filter(fn: (r) => r._measurement == "sensor_data")
        |> filter(fn: (r) => r._field == "{influxdb_field}")
        |> filter(fn: (r) => r._value {influxdb_operator} {condition_value})
        |> keep(columns: ["_time", "_value"])
        '''

        try:
            result = InfluxDBQueryHelper.execute_query(query)
            if result and result[0].records:
                # Convert timestamps to string format
                timestamps = [record.get_time().strftime("%Y-%m-%dT%H:%M:%SZ") for record in result[0].records]
                values = [record.get_value() for record in result[0].records]
                graph_data = [{"name": t, "value": v} for t, v in zip(timestamps, values)]
                dispatcher.utter_message(
                    text=f"Here is the graph for '{field}' between {start_time} and {stop_time}.",
                    custom={"graph_data": graph_data , "table_data": graph_data}
                )
            else:
                dispatcher.utter_message(
                    text=f"No data found for '{field}' in the specified time range."
                )
        except ConnectionError as e:
            dispatcher.utter_message(text=f"Connection error: {str(e)}")
        except Exception as e:
            dispatcher.utter_message(text=f"Unexpected error: {str(e)}")

        return []

