import sys
sys.path.append('./glados_tts')

from glados_tts.glados import tts_runner;

glados = tts_runner(False, True)

glados.speak("Hello, world!", True)