import os;
import io;
from os.path import exists;
from pocketsphinx import LiveSpeech;
import requests;
import yaml;
from playsound import playsound
from tempfile import NamedTemporaryFile
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

settings = "config.yaml"

def take_command():
    samplerate = 44100  # Hertz
    duration = 5  # seconds
    threshold = 20  # audio levels below this value will be considered silence

    print("Listening...")
    while True:
        audio = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=2, blocking=True)
        if np.mean(np.abs(audio)) < threshold:
            break

    print("Recording finished")

    # Convert the audio data to WAV format in memory
    buffer = io.BytesIO()
    write(buffer, samplerate, audio)
    buffer.seek(0)
    files = {'audioData': ('output.wav', buffer, 'audio/wav')}

    # Return the audio data
    return files

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
        # TODO: Added Error Handling
        command = take_command()
        response = requests.post(settings["url"] + "/command", files=command)
        with NamedTemporaryFile(delete=False, suffix='.wav') as f:
            f.write(response.content)
            playsound(f.name)
    except Exception as e:
        print(e)