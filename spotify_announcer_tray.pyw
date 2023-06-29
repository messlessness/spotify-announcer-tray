from __future__ import print_function
from infi.systray import SysTrayIcon
import os
import ctypes
import pyttsx3
import time
from SwSpotify import spotify
import argparse
import multiprocessing
from threading import Thread

prevsong = ""
prevartist = ""
initEngine = pyttsx3.init()
terminate = False
need_announce_new_track = False
dt = 0.5
delay = 0.0
global volume
global rate
global voice
global term
term = True
global t
t = None

parser = argparse.ArgumentParser("Spotify Announcer Tray")
parser.add_argument("-l", "--list", help="Lists available voices, quits", required=False, action='store_true')
parser.add_argument("-s", "--set", help="Sets the voice[Default: 1]", type=int, default=1, required=False)
parser.add_argument("-d", "--delay", help="Delay before announcement(seconds)[Default: 3]", type=float, default=3, required=False)
parser.add_argument("-r", "--rate", help="Speaking rate in words per minute[Default: 150]", type=int, default=150, required=False)
parser.add_argument("-v", "--volume", help="Set volume of announcer (0.0-1.0)[Default: 1]", type=float, default=1, required=False)
args = parser.parse_args()

if (args.list):
	voices = initEngine.getProperty('voices')
	i=0
	for voice in voices:
		print (str(i) + ":")
		print(" - Name: %s" % voice.name)
		i=i+1
	quit()
	
if (args.set != None):
	voices = initEngine.getProperty('voices')
	if (args.set > len(voices)-1):
		print ("Input voice out of range. Please input a number from 0 to " + str(len(voices)-1))
		quit()
	initEngine.setProperty('voice', voices[args.set].id)

delay = args.delay

icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
volume = args.volume
prev_volume = volume
rate = args.rate
voice = voices[args.set].id
initEngine.stop()

def on_quit(systray):
	print("Bye")
	global terminate
	terminate = True

def on_about(systray):
	ctypes.windll.user32.MessageBoxW(None, u"Created using infi.systray, SwSpotify, pyttsx3", u"Spotify Announcer Tray", 0)

def on_change_volume(diff):
	global volume
	current_volume = volume
	target_volume = current_volume + diff
	
	if (target_volume > 1.0):
		target_volume = 1.0
	if (target_volume < 0.0):
		target_volume = 0.0

	volume = target_volume

def on_increase_volume(systray):
	on_change_volume(0.25)

def on_decrease_volume(systray):
	on_change_volume(-0.25)

def threaded(fn):
	def wrapper(*args, **kwargs):
		thread = Thread(target=fn, args=args, kwargs=kwargs)
		thread.start()
		return thread
	return wrapper

def speak(phrase):
	engine = pyttsx3.init()
	engine.setProperty('voice', voice)
	engine.setProperty('volume', volume)
	engine.setProperty('rate', rate)
	engine.say(phrase)
	engine.runAndWait()
	engine.stop()

def stop_speaker():
	global t
	global term
	term = True
	if (t != None):
		t.join()

@threaded
def manage_process(p):
	global term
	while p.is_alive():
		if term:
			p.terminate()
			print("stopping speak...")
			term = False
		else:
			continue

	
def say(phrase):
	global t
	global term
	term = False
	p = multiprocessing.Process(target=speak, args=(phrase,))
	p.start()
	t = manage_process(p)
      
if __name__ == '__main__':
	menu_options = (
		("Voice Volume +25%", None, on_increase_volume), 
		("Voice Volume -25%", None, on_decrease_volume),
		("About", None, on_about)
	)
	systray = SysTrayIcon(icon_path, "Spotify Announcer Tray", menu_options, on_quit)
	systray.start()

	while not terminate:
		try:
			trackInfo = spotify.current()
			song = trackInfo[0]
			artist = trackInfo[1]

			volume_changed = False
			isInDelay = False

			if (prev_volume != volume):
				volume_changed = True
				
			if (not(song == None or artist == None) and (song != prevsong or artist!=prevartist)):
				need_announce_new_track = True
				isInDelay = False

			if (volume_changed):
				stop_speaker()
				say("Current volume is " + str(volume))

				print("Current volume is " + str(volume))
				prev_volume = volume

			if (need_announce_new_track):
				if (delay != 0):
					delay = delay - dt
					isInDelay = True
				else:
					delay = args.delay
				
				if (not isInDelay):
					stop_speaker()
					say("Playing " + song + " by " + artist)

					print("Playing " + song + " by " + artist)
					systray.update(hover_text=artist + " - " + song)
					prevsong = song
					prevartist = artist
					need_announce_new_track = False

		except spotify.SpotifyNotRunning as e:
			pass
		time.sleep(dt)