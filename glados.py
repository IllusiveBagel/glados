import os
import sys
import json
import random
sys.path.append('./glados_tts')

from glados_tts.glados import tts_runner;
from skills import homeAssistant;
from pocketsphinx import LiveSpeech;
import speech_recognition as sr;

glados = tts_runner(False, True)

file = open("./phrases.json")
phrases = json.load(file)

def start_up():
    homeAssistant.home_assistant_initialize()
    glados.speak("oh, its you", True)
    print("\nWaiting for keyphrase: ")

def take_command():
    greetings = phrases["greetings"]
    greetLen = len(greetings)

    glados.speak(greetings[random.randint(0, greetLen - 1)], True)
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en').lower()
    except Exception as e:
        print(e)
        print("Say that again please...")
        return "None"
    return query

# Process the command
def process_command(command):

	if ('cancel' in command or
		'nevermind' in command or
		'forget it' in command):
		glados.speak("Sorry.", cache=True)

		# Todo: Save the used trigger audio as a negative voice sample for further learning

	##### LIGHTING CONTROL ###########################

	elif 'turn off' in command or 'turn on' in command and 'light' in command:
		glados.speak(homeAssistant.home_assistant_process_command(command))
				
	
	##### PLEASANTRIES ###########################

	elif 'who are' in command:
		glados.speak("I am GLaDOS, artificially super intelligent computer system responsible for testing and maintenance in the aperture science computer aided enrichment center.", cache=True)

	elif 'how are you' in command:
		glados.speak("Well thanks for asking.", cache=True)
		glados.speak("I am still a bit mad about being unplugged, not that long time ago.", cache=True)
		glados.speak("you murderer.", cache=True)

	
	print("\nWaiting for trigger...")

start_up()

speech = LiveSpeech(
    lm=False,
    dict=os.path.join('glados.dict'),
    keyphrase='hey glados',
    kws_threshold=1e-20,
)

for phrase in speech:
    try:
        command = take_command()
        process_command(command)

        print(command)
    except Exception as e:
        print(e)