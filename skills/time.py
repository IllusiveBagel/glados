import re
import datetime as dt
from threading import Timer
from gladosTTS import speak

# Start a new timer
def startTimer(command):
	command = command.replace('-', ' ')
	
	# Parse the time and context from the command
	regex = r"^set (a|the)?\s?([\D]*timer[\D]*)?(([\d]{1,3}) hour)?([\D]*([\d]{1,3}) minute)?([\D]*([\d]{1,3}) second(s)?)?( timer)?( for ([\D]+))?"
	matches = re.search(regex, command, re.MULTILINE | re.IGNORECASE)

	if matches:
		hours = int(matches[4] or 0)
		minutes = int(matches[6] or 0)
		seconds = int(matches[8] or 0)

		# Calculate duration to seconds
		duration = hours*3600+minutes*60+seconds

		if duration > 1:
			t = Timer(duration, timerEnd, [duration])
			t.start()
			print(str(duration)+" second timer started at "+str(dt.datetime.now()))
			return "The timer starts now"
	else:
		return "I didn't understand the duration you wanted the timer for"

# Run this when the timer ends
def timerEnd(duration):
	print (str(duration)+" second timer ended "+str(dt.datetime.now()))
	speak("the time is up")