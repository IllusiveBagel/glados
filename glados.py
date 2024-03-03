import os
from os.path import exists
from pocketsphinx import LiveSpeech;
import speech_recognition as sr;
import requests;
import yaml;
from playsound import playsound
from tempfile import NamedTemporaryFile

settings = "config.yaml"
headers = {
    'Content-Type': 'application/json'
}

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en').lower()
        print(f"User said: {query}")
    except Exception as e:
        print(e)
        print("Say that again please...")
        return "None"
    return query

# Check and load the YAML settings file
def validate_settings(load=False):
	global settings

	# Check if YAML file exists
	if not exists(settings):
		print("\033[1;31mERROR 1:\033[1;97m "+settings+" file not found.")
		return False


	# Check if YAML is valid and load it to RAM
	with open(settings, "r") as stream:
		try:
			settings = yaml.safe_load(stream)
		except yaml.YAMLError as exc:
			print("\033[1;31mERROR 2:\033[1;97m Error parsing "+settings+" file:\n")
			print(exc)
			return False
          
# Check for setting YAML
if (exists(settings)):
    # Validate and load
    validate_settings(load=True)

speech = LiveSpeech(
    lm=False,
    dict=os.path.join('glados.dict'),
    keyphrase='glados',
    kws_threshold=1e-15,
)

for phrase in speech:
    try:
        command = take_command()
        response = requests.post(settings["url"] + "/command", headers=headers, data='{"command":"'+command+'"}', stream=True)
        with NamedTemporaryFile(delete=False, suffix='.wav') as f:
            f.write(response.content)
            playsound(f.name)
    except Exception as e:
        print(e)