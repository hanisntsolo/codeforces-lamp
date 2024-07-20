from dotenv import load_dotenv
import os
import hashlib
import random
import string
import time
import requests
import json
from tuya_connector import TuyaOpenAPI
from datetime import datetime
from pprint import pp

# Load environment variables from a specified .env file
load_dotenv(dotenv_path='/.env')
# Path to your log file
LAB_LOG_FILE_PATH = os.getenv('LAB_LOG_FILE_PATH')

def initialize_tuya_api():
    access_id = os.getenv("TUYA_ACCESS_ID")
    access_key = os.getenv("TUYA_ACCESS_KEY")
    if not all([access_id, access_key]):
        raise ValueError("Tuya credentials must be set as environment variables.")
    openapi = TuyaOpenAPI("https://openapi.tuyaus.com", access_id, access_key)
    openapi.connect()
    return openapi
    
def send_tuya_command(openapi, endpoint, commands):
    response = openapi.post(endpoint, commands)
    if response.get("success"):
        write_log("Lamp turned on successfully")
    else:
        write_log(f"Failed to execute command: {response.get('msg')}")
        
def calculate_sha512(text):
    return hashlib.sha512(text.encode('utf-8')).hexdigest()

def add_authorization_parameters(method, parameters, key, secret):
    parameters["apiKey"] = key
    parameters["time"] = str(int(time.time()))

    rand = ''.join(random.choices(string.ascii_lowercase, k=6))
    
    sorted_params = sorted(parameters.items())
    query_string = '&'.join(f'{k}={v}' for k, v in sorted_params)
    
    api_sig_base = f"{rand}/{method}?{query_string}#{secret}"
    api_sig = rand + calculate_sha512(api_sig_base)
    
    parameters["apiSig"] = api_sig

def write_log(message):
    log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [CODEFORCES_LAMP] : {message}"
    print(log_message)
    return # When inside container.
    try:
        # Read the existing contents of the log file
        if os.path.exists(LAB_LOG_FILE_PATH):
            with open(LAB_LOG_FILE_PATH, 'r') as file:
                existing_content = file.read()
        else:
            existing_content = ''

        # Prepend the new log entry
        with open(LAB_LOG_FILE_PATH, 'w') as file:
            file.write(f"{message}\n{existing_content}")

    except Exception as e:
        print(f'Error occurred while writing to log file: {e}')

def codeforces_api_request(method, parameters):
    base_url = "https://codeforces.com/api/"
    url = f"{base_url}{method}"
    if not parameters:
        parameters = {}
    key = os.getenv("CODEFORCES_API_KEY")
    secret = os.getenv("CODEFORCES_API_SECRET")
    if not key or not secret:
        raise ValueError("API key and secret must be set as environment variables.")
    
    add_authorization_parameters(method, parameters, key, secret)
    
    combined_parameters = '&'.join(f'{k}={v}' for k, v in parameters.items())
    full_url = f"{url}?{combined_parameters}"
    # pp(f"Parameters before :: {parameters}")  # For debugging
    # pp(f"New Combined Parameters are :: {combined_parameters}")  # For debugging
    # pp(f"Formed Request is as follows :: {full_url}")  # For debugging
    response = requests.get(full_url)
    if response.status_code == 200:
        return response.json()
    else:
        write_log(f"Failed to fetch data: {response}")
        return None
        
def map_rating_to_color(rating):
    if rating < 1200:
        return {"h": 240, "s": 1000, "v": 1000}  # Blue
    elif rating < 1400:
        return {"h": 120, "s": 1000, "v": 1000}  # Green
    elif rating < 1600:
        return {"h": 180, "s": 1000, "v": 1000}  # Cyan
    elif rating < 1900:
        return {"h": 60, "s": 1000, "v": 1000}   # Yellow
    elif rating < 2100:
        return {"h": 30, "s": 1000, "v": 1000}   # Orange
    else:
        return {"h": 0, "s": 1000, "v": 1000}    # Red
        
def get_bulb_state(openapi):
    bulb_id = os.getenv("TUYA_BULB_ID")
    if not bulb_id:
        raise ValueError("Tuya bulb ID must be set as an environment variable.")
    
    response = openapi.get(f"/v1.0/iot-03/devices/{bulb_id}/status")
    if response.get("success"):
        return response.get("result")
    else:
        print(f"Failed to get bulb state: {response}")
        return None        
        
def set_bulb_color(openapi, color):
    bulb_id = os.getenv("TUYA_BULB_ID")
    if not bulb_id:
        raise ValueError("Tuya bulb ID must be set as an environment variable.")

    commands = {
        "commands": [
            {"code": "switch_led", "value": True},
            {"code": "bright_value_v2", "value": 1000},
            {"code": "colour_data_v2", "value": color}
        ]
    }

    send_tuya_command(openapi, f"/v1.0/iot-03/devices/{bulb_id}/commands", commands)

def is_bulb_on(bulb_state):
    for item in bulb_state:
        if item['code'] == 'switch_led':
            return item['value']
    return None
    
def is_bulb_on_and_codeforces_pallete(bulb_state):   
    hue_values = {0, 30, 60, 120, 180, 240}
    # Initialize variables to check for switch state and color state
    is_on = False
    is_codeforces_pallete = False
    
    # Iterate over the bulb state to check for required conditions
    for item in bulb_state:
        # Check if work mode is on and refrain from changing color
        if item['code'] == 'work_mode':
            work_state = item['value']
            if work_state == "white":
                write_log(f"Work mode is on : {item['value']} : Skipping lamp color change!")
                return False
        if item['code'] == 'switch_led':
            is_on = item['value']
        if item['code'] == 'colour_data_v2':
            color_state = item['value']
            if isinstance(color_state, str):
                color_state = json.loads(color_state)
            if color_state.get('h') in hue_values:
                is_codeforces_pallete = True
    
    # Return True only if the bulb is on and the color is blue
    return is_on and is_codeforces_pallete
    
def set_bulb_off(openapi):
    bulb_id = os.getenv("TUYA_BULB_ID")
    if not bulb_id:
        raise ValueError("Tuya bulb ID must be set as an environment variable.")
    
    commands = {
        "commands": [
            {"code": "switch_led", "value": False}
        ]
    }
    
    send_tuya_command(openapi, f"/v1.0/iot-03/devices/{bulb_id}/commands", commands)    
    
def contest_status(contestId, handle, asManager=False, submissionReturn=None, count=None):
    if not contestId:
        raise ValueError("ContestId must be provided")
    contestId = str(contestId)
    method = "contest.status"
    parameters = {}
    parameters["contestId"] = contestId
    if handle:
        parameters["handle"] = handle
    if asManager:
        parameters["asManager"] = asManager
    if submissionReturn:
        parameters["from"] = submissionReturn
    if count:
        parameters["count"] = count
    data = codeforces_api_request(method, parameters)
    return data
    
def contest_list():
    method = "contest.list"
    return codeforces_api_request(method, {})

def recent_submissions(count=None):
    if not count:
        count = 1
    method = "problemset.recentStatus"
    parameters = {}
    parameters["count"] = count
    return codeforces_api_request(method, parameters)

def user_info(handle="hanisntsolo"):
    method = "user.info"
    parameters = {"handles": handle}
    return codeforces_api_request(method, parameters)

def user_status(handle="hanisntsolo", count=1, tillFrom=1):
    method = "user.status"
    parameters = {}
    parameters["handle"] = handle
    parameters["from"] = tillFrom
    parameters["count"] = count
    return codeforces_api_request(method, parameters)
    
def codeforces_monitor_all_submissions():
    data = user_status()
    if not data:
        return None
    return data["result"][0]
    
def codeforces_submission_monitor():
    last_submission_timestamp = None
    last_submission_id = None
    openapi = initialize_tuya_api() # Set tupy api to be able to send instructions.
    while True:
        latest_submission = codeforces_monitor_all_submissions()
        if latest_submission:
            submission_id = latest_submission["id"]
            submission_timestamp = latest_submission["creationTimeSeconds"]
            bulb_state = get_bulb_state(openapi)
            # Get state of the bulb if its off means it was turned off manually hence don't do anything.
            if is_bulb_on(bulb_state) == False:
                sleep_seconds = 5
                write_log(f"Lamp is off, skipping automated control. Sleeping for {sleep_seconds} seconds")
                time.sleep(sleep_seconds)
                continue # Continue with state checking 
            # Check if the bulb is on and color is codeforces pallete only then change and check state.
            if is_bulb_on_and_codeforces_pallete(bulb_state):    
                if(last_submission_id is None or submission_id > last_submission_id) and (last_submission_timestamp is None or submission_timestamp > last_submission_timestamp):
                    write_log(f"New submission recorded : {submission_id}")
                    # Process the submission and update bulb color
                    verdict = latest_submission["verdict"]
                    process_submission(openapi)
                    if verdict == "OK":
                        sleep_seconds = 120
                        accepted_log = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Verdict Accepted for submission : {submission_id}]"
                        write_log(accepted_log)
                        color = map_rating_to_color(1201)
                        set_bulb_color(openapi, color)
                        time.sleep(sleep_seconds)
                    else:
                        sleep_seconds = 30
                        failure_log = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Verdict failure for submission : {submission_id}]"
                        write_log(failure_log)
                        pp(latest_submission) # To log failed submission
                        color = map_rating_to_color(2101)
                        set_bulb_color(openapi, color)
                        time.sleep(sleep_seconds)
                    #Update last processed submission timestamp or Id
                    last_submission_timestamp = submission_timestamp
                    last_submission_id = submission_id
                
                else:
                    #No new submission, default to profile color
                    data = user_info()
                    if data and is_bulb_on_and_codeforces_pallete(bulb_state):
                        user = data['result'][0]
                        rating = user['rating']
                        color = map_rating_to_color(rating)
                        set_bulb_color(openapi, color)
            else:
                write_log("Lamp is not in codeforces pallete color, skipping automated control.")
                    
        sleep_seconds = 10
        sleep_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [Sleeping for : {sleep_seconds} seconds]" 
        write_log(sleep_message)
        time.sleep(sleep_seconds) # Check for new submission every 10 seconds.

def process_submission(openapi):
    color = map_rating_to_color(1901) # Orange 
    for _ in range(3): # Number of blinks
        set_bulb_color(openapi, color)
        time.sleep(1)
        set_bulb_color(openapi, {"h": 0, "s": 0, "v": 0}) # Turn the bulb off
        time.sleep(1)
        
def main():
    codeforces_submission_monitor()
    
if __name__ == "__main__":
    main()

    
#chmod +x /media/hanisntsolo/WDBlue_ssd_hanis/docker/volumes/jupyter/notebooks/codeforces-lamp.py
#0 19 * * * /usr/bin/python3 /media/hanisntsolo/WDBlue_ssd_hanis/docker/volumes/jupyter/notebooks/codeforces-lamp.py >> /media/hanisntsolo/WDBlue_ssd_hanis/docker/volumes/jupyter/notebooks/AutoAddAndCommit.log 2>&1
