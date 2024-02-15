import json
import random
from gladosTTS import speak
from skills import home_assistant as ha
from skills import time

file = open("./phrases.json")
phrases = json.load(file)

def process_command(command):
	if ('cancel' in command or
		'nevermind' in command or
		'forget it' in command):
		cancel = phrases["cancel"]
		cancelLen = len(cancel)
		speak(cancel[random.randint(0, cancelLen - 1)])

	elif 'who are' in command:
		speak((
			"I am glados, artificially super intelligent computer system"
			"responsible for testing and maintenance in the aperture science"
			"computer aided enrichment center."
		))

	elif 'how are you' in command:
		response = [
			"Well thanks for asking.",
			"I am still a bit mad about being unplugged, not that long ago.",
			"you murderer."
		]
		
		for text in response:
			speak(text)
			
	elif 'light' in command:
		response = ha.light_control(command)
		speak(response)

	elif 'timer' in command:
		response = time.startTimer(command)
		speak(response)

	else:
		missingCommand = phrases["missingCommand"]
		missingCommandLen = len(missingCommand)

		speak(missingCommand[random.randint(0, missingCommandLen - 1)])