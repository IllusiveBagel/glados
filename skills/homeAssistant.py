from os.path import exists
import yaml
import json
import re
import requests
import datetime as dt
from subprocess import check_output
import threading
import random

# Instance & global variables
home_assistant = False
home_assistant_settings_file = "config.yaml"

# Initialize Home Assistant and test the connection
def home_assistant_initialize():

	global home_assistant
	global home_assistant_settings_file

	# Allow script to find the settings file if ran directly
	if (exists("../"+home_assistant_settings_file)):
		home_assistant_settings_file = "../"+home_assistant_settings_file

	# Check for Home Assistant setting YAML
	if (exists(home_assistant_settings_file)):

		# Validate and load settings
		home_assistant_validate_settings(load=True)
		home_assistant["api"]["endpoint"] = home_assistant["api"]["address"]+"/api/"

		# Test connection to Home Assistant API
		if not home_assistant_test_api():
			home_assistant = False
			exit();

	else:
		home_assistant = False

		print("\033[1;94mINFO:\033[;97m Home Assistant not linked.")
		
# Returns True or False if Home Assistant API is responsive	
def home_assistant_test_api():
	# Set the endpoint where to send the request
	url = home_assistant["api"]["endpoint"]

	# Send request to home assistant and get server response
	response = check_output(["curl", "--insecure", "-i", "-X", "GET", "-H", "Authorization: Bearer "+home_assistant["api"]["token"], "-H", "Content-Type: application/json", url])

	# Process response from home assistant, error handling if HA responds with something else than HTTP 200 OK
	if "API running." in str(response):
		print("\033[1;94mINFO:\033[;97m Successfully connected to Home Assistant API at " + home_assistant["api"]["endpoint"])
		return True
	else:
		home_assistant_process_error(response)
		
# Check and load the YAML settings file
def home_assistant_validate_settings(load=False):

	global home_assistant
	global home_assistant_settings_file

	# Check if YAML file exists
	if not exists(home_assistant_settings_file):
		print("\033[1;31mERROR 1:\033[1;97m "+home_assistant_settings_file+" file not found.")
		return False


	# Check if YAML is valid and load it to RAM
	with open(home_assistant_settings_file, "r") as stream:
		try:
			home_assistant_settings = yaml.safe_load(stream)
		except yaml.YAMLError as exc:
			print("\033[1;31mERROR 2:\033[1;97m Error parsing "+home_assistant_settings_file+" file:\n")
			print(exc)
			return False


	# Check if address for Home Assistant is defined
	try:
		match = re.match(r"^(http|https):\/\/.*", home_assistant_settings["api"]["address"])
		if not bool(match):
			print("\033[1;31mERROR 3:\033[1;97m "+home_assistant_settings["api"]["address"]+" does not look like valid address in "+home_assistant_settings_file)
	except KeyError:
		print("\033[1;31mERROR 3:\033[1;97m API address not defined in "+home_assistant_settings_file)


	# Check if long lived access token is defined
	try:
		match = re.match(r"^([\S]{40,})$", home_assistant_settings["api"]["token"])
		if not bool(match):
			print("\033[1;31mERROR 4:\033[1;97m Long lived access token does not look valid in "+home_assistant_settings_file)
	except KeyError:
		print("\033[1;31mERROR 4:\033[1;97m API token not defined in "+home_assistant_settings_file)


	#TODO: Add additional YAML validation

	
	# Load settings from file to RAM
	if(load):
		home_assistant = home_assistant_settings
	else:
		print("\033[0;94mINFO:\033[;97m "+home_assistant_settings_file + " validated successfully.")

	return True

# Turn Home Assistant server responses into speakable output
def home_assistant_process_error(response):

	response = str(response)

	if "200 OK" in response:
		return ""
	elif "401 Unauthorized" in response:
		print("\033[1;31mERROR:\033[1;97m Home Assistant rejected access token. Check your "+home_assistant_settings_file)
		return "It looks like my home automation core has rejected my crentials."
	elif "404 Not Found" in response:
		print("\033[1;31mERROR:\033[1;97m Home Assistant responded with 404")
		print(response)
		return "My home automation core has no idea what you just requested it."
	else:
		print("\033[1;31mERROR:\033[1;97m Home Assistant responded with:")
		print(response)
		return "It looks like my home automation core is unresponsive."
	
# Main function of the skill
def home_assistant_process_command(command):
	if 'turn o' in command and 'light' in command:
		response = home_assistant_light_control(command)

	return response

# Main light control function
def home_assistant_light_control(command):

	search_query = command

	# Parse entity room
	room = home_assistant_match_room(command)

	# Replace room in search query with a variable
	if(room):
		search_query = search_query.replace(room, "$room")

	# Parse intent
	intent = home_assistant_match_on_off(command)

	entity = ""
	response = ""
	
	if intent == "on":
		# Search for the scene entity from Home Assistant settings
		try:
			for scene in home_assistant["scenes"]:
				if search_query in scene["command"]:
					entity = scene["entity"]
					try:
						response = scene["response"]
					except:
						response = ["Okay, fine."]
		except:
				pass
	if(intent):
		search_query = search_query.replace("turn off", "turn $on_off")
		search_query = search_query.replace("turn on", "turn $on_off")
	else:
		pass
		# TODO: Look for "set light to 94%" commands

	# Search for the light entity from Home Assistant settings if not already found
	if(entity == ""):
		for light in home_assistant["lights"]:
			if search_query in light["command"]:
				entity = light["entity"]
				try:
					response = light["response"]
				except:
					response = ["Okay, fine."]


	# Pick a random response from Home Assistant settings
	response = response[random.randint(0,len(response)-1)]

	# Build back entity from variables
	if(room):
		entity = entity.replace("$room", room.replace(" ", "_"))
		response = response.replace("$room", room)

	response = response.replace("$on_off", intent)

	# Process as light entity
	if entity.startswith("light."):
		home_assistant_light_switch(entity, intent)

	return str(response)+"\n\n"

# Return the room from command
def home_assistant_match_room(command):

	# Match these as rooms
	patterns_lst = ["living room", "kitchen", "toilet", "bathroom", "bedroom", "office", "balcony", "hallway", "dining area", "entryway", "sauna"]

	# Return the first match from command
	for pattern in patterns_lst:
		match = re.search(pattern, command)

		if match:
			return match[0]
		
# Return ON or OFF from command
def home_assistant_match_on_off(command):

	patterns_lst=["turn (off)", "turn (on)"]

	for pattern in patterns_lst:
		match = re.search(pattern, command)

		if match:
			return match[1]

# Turn lights ON and OFF
def home_assistant_light_switch(entity, state):

	# Make sure about the right format for API
	if "off" in state:
		state = "off"
	else:
		state = "on"

	# Set the endpoint where to send the request
	url = home_assistant["api"]["endpoint"] + "services/light/turn_"+state

	# Generate data packet
	payload =  '{"entity_id":"'+entity+'"}'

	# Send request to home assistant and get server response
	response = check_output(["curl", "--insecure", "-i", "-X", "POST", "-H", "Authorization: Bearer "+home_assistant["api"]["token"], "-H", "Content-Type: application/json", "-d", payload, url])

	# Process response from home assistant, error handling if HA responds with something else than HTTP 200 OK
	if "200 OK" in str(response):
		return
	else:
		home_assistant_process_error(response)