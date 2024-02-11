import json
import random
from skills import home_assistant as ha

file = open("./phrases.json")
phrases = json.load(file)

def process_command(command):
    if ('cancel' in command or
		'nevermind' in command or
		'forget it' in command):
        cancel = phrases["cancel"]
        cancelLen = len(cancel)
        response = cancel[random.randint(0, cancelLen - 1)]

    elif 'who are' in command:
        response = "I am glados, artificially super intelligent computer system responsible for testing and maintenance in the aperture science computer aided enrichment center."

    elif 'how are you' in command:
        response = [
            "Well thanks for asking.",
            "I am still a bit mad about being unplugged, not that long ago.",
            "you murderer."
        ]
              
    elif 'light' in command:
        response = ha.light_control(command)

    else:
        missingCommand = phrases["missingCommand"]
        missingCommandLen = len(missingCommand)

        response = missingCommand[random.randint(0, missingCommandLen - 1)]
                
    return response