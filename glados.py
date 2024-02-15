import os
import json
import random

from gladosTTS import speak
from skills import home_assistant as ha;
from skills import commands as cmd;
from pocketsphinx import LiveSpeech;
import speech_recognition as sr;

# Get json of phrases
file = open("./phrases.json")
phrases = json.load(file)

def start_up():
    ha.initialize()
    speak("oh, its you")
    print("\nWaiting for keyphrase: ")

def take_command():
    greetings = phrases["greetings"]
    greetLen = len(greetings)

    speak(greetings[random.randint(0, greetLen - 1)])
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

        cmd.process_command(command)
    except Exception as e:
        print(e)