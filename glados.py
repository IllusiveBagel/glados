import os
import sys
import json
import random
sys.path.append('./glados_tts')

from glados_tts.glados import tts_runner;
from skills import home_assistant as ha;
from skills import commands as cmd;
from pocketsphinx import LiveSpeech;
import speech_recognition as sr;

glados = tts_runner(False, True)

# Get json of phrases
file = open("./phrases.json")
phrases = json.load(file)

def start_up():
    ha.initialize()
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
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en').lower()
    except Exception as e:
        print(e)
        print("Say that again please...")
        return "None"
    return query

start_up()

speech = LiveSpeech(
    lm=False,
    dict=os.path.join('glados.dict'),
    keyphrase='glados',
    kws_threshold=1e-15,
)

for phrase in speech:
    try:
        command = take_command()

        response = cmd.process_command(command)

        if type(response).__name__ == 'str':
            glados.speak(response, True)
        elif type(response).__name__ == 'list':
             for text in response:
                  glados.speak(text, True)
    except Exception as e:
        print(e)