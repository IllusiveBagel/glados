from os.path import exists
import yaml
import json
import re
import random
import requests

# Instance & global variables
home_assistant = False
settings_file = "config.yaml"
headers ={}
file = open("./phrases.json")
phrases = json.load(file)

# Initialize Home Assistant and test the connection
def initialize():
    global home_assistant
    global settings_file
    global headers

    # Check for setting YAML
    if (exists(settings_file)):

        # Validate and load
        validate_settings(load=True)
        settings_file["api"]["endpoint"] = settings_file["api"]["address"]+"/api/"
        headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer "+settings_file["api"]["token"]
        }

        # Test connection to Home Assistant API
        if not test_api():
            home_assistant = False
            exit();

    else:
        home_assistant = False

        print("\033[1;94mINFO:\033[;97m Home Assistant not linked.")

# Returns True or False if Home Assistant API is responsive	
def test_api():
	# Set the endpoint and token
	url = settings_file["api"]["endpoint"]

	# Send request to home assistant and get server response
	response = requests.get(url, headers=headers)

	# Process response from home assistant, error handling if HA responds with something else than HTTP 200 OK
	if response.status_code == 200:
		print("\033[1;94mINFO:\033[;97m Successfully connected to Home Assistant API at " + settings_file["api"]["endpoint"])
		return True
	else:
		process_error(response)
            
# Check and load the YAML settings file
def validate_settings(load=False):
	global home_assistant
	global settings_file

	# Check if YAML file exists
	if not exists(settings_file):
		print("\033[1;31mERROR 1:\033[1;97m "+settings_file+" file not found.")
		return False


	# Check if YAML is valid and load it to RAM
	with open(settings_file, "r") as stream:
		try:
			settings_file = yaml.safe_load(stream)
		except yaml.YAMLError as exc:
			print("\033[1;31mERROR 2:\033[1;97m Error parsing "+settings_file+" file:\n")
			print(exc)
			return False
		
# Turn Home Assistant server responses into speakable output
def process_error(response):
    match response.status_code:
        case 401:
            print("\033[1;31mERROR:\033[1;97m Home Assistant rejected access token. Check your "+settings_file)
            return "It looks like my home automation core has rejected my crentials."
        case 404:
            print("\033[1;31mERROR:\033[1;97m Home Assistant responded with 404")
            print(response)
            return "My home automation core has no idea what you just requested it."
        case _:
            print("\033[1;31mERROR:\033[1;97m Home Assistant responded with:")
            print(response)
            return "It looks like my home automation core is unresponsive."
		
# Return the room from command
def match_room(command):
	# Return the first match from command
	for pattern in settings_file["rooms"]:
		match = re.search(pattern, command)

		if match:
			return match[0]
		
# Return ON or OFF from command
def match_on_off(command):
	patterns_lst=["off", "on"]

	for pattern in patterns_lst:
		match = re.search(pattern, command)

		if match:
			return match[0]

# Returns the brightness from 0-255 from percentage in command		
def format_brightness(command):
    # Search for a number followed by a percentage sign
    match = re.search(r'(\d+)%', command)
    if match:
        # Extract the number as an integer
        percentage = int(match.group(1))
        # Scale to 0-255 range (rounding to nearest integer)
        brightness = round(percentage * 255 / 100)
        return brightness
          
# Main light control function
def light_control(command):
	# Parse entity room
	room = match_room(command)

	# Replace room in search query with a variable
	if not room:
		noRoom = phrases["noRoom"]
		noRoomLen = len(noRoom)
		return noRoom[random.randint(0, noRoomLen - 1)]

	# Parse intent
	intent = match_on_off(command)

	entity = ""
	brightness = ""
	response = ""
	
	if not intent:
		brightness = format_brightness(command)

	if(entity == ""):
		entity = "light." + room.replace(" ", "_")
	
	if intent == "on":
		lightOn = phrases["lightOn"]
		lightOnLen = len(lightOn)
		response = lightOn[random.randint(0, lightOnLen - 1)]
	elif intent == "off":
		lightOff = phrases["lightOff"]
		lightOffLen = len(lightOff)
		response = lightOff[random.randint(0, lightOffLen - 1)]

	if brightness:
		lightBrightness = phrases["lightBrightness"]
		lightBrightnessLen = len(lightBrightness)
		response = lightBrightness[random.randint(0, lightBrightnessLen - 1)]

    # Process as light entity
	if entity.startswith("light."):
		if brightness:
			light_brightness(entity, brightness)
		else:
			light_switch(entity, intent)
			
	return response

# Turn lights ON and OFF
def light_switch(entity, state):
	# Make sure about the right format for API
	if "off" in state:
		state = "off"
	else:
		state = "on"

	# Set the endpoint where to send the request
	url = settings_file["api"]["endpoint"] + "services/light/turn_"+state

	# Generate data packet
	payload =  '{"entity_id":"'+entity+'"}'

	# Send request to home assistant and get server response
	response = requests.post(url, headers=headers, data=payload)

	# Process response from home assistant, error handling if HA responds with something else than HTTP 200 OK
	if response.status_code == 200:
		return
	else:
		process_error(response)

# Set light brightness
def light_brightness(entity, brightness):
	# Set the endpoint where to send the request
	url = settings_file["api"]["endpoint"] + "services/light/turn_on"

	# Generate data packet
	payload =  '{"entity_id":"'+entity+'", "brightness":'+str(brightness)+'}'

	# Send request to home assistant and get server response
	response = requests.post(url, headers=headers, data=payload)

	# Process response from home assistant, error handling if HA responds with something else than HTTP 200 OK
	if response.status_code == 200:
		return
	else:
		process_error(response)