from __future__ import print_function
from infi.systray import SysTrayIcon
import os
import ctypes
import pyttsx3
import time
from SwSpotify import spotify
import argparse

prevsong = ""
prevartist = ""
engine = pyttsx3.init()
terminate = False

parser = argparse.ArgumentParser("Spotify Announcer Tray")
parser.add_argument("-l", "--list", help="Lists available voices, quits", required=False, action='store_true')
parser.add_argument("-s", "--set", help="Sets the voice", type=int, default=1, required=False)
parser.add_argument("-d", "--delay", help="Delay before announcement(seconds)", type=float, default=5, required=False)
parser.add_argument("-r", "--rate", help="Speaking rate in words per minute[Default: 170]", type=int, default=170, required=False)
parser.add_argument("-v", "--volume", help="Set volume of announcer (0.0-1.0)", type=float, default=0.5, required=False)
args = parser.parse_args()

if (args.list):
	voices = engine.getProperty('voices')
	i=0
	for voice in voices:
		print (str(i) + ":")
		print(" - Name: %s" % voice.name)
		i=i+1
	quit()
	
if (args.set != None):
	voices = engine.getProperty('voices')
	if (args.set > len(voices)-1):
		print ("Input voice out of range. Please input a number from 0 to " + str(len(voices)-1))
		quit()
	engine.setProperty('voice', voices[args.set].id)

engine.setProperty('rate', args.rate)
engine.setProperty('volume', args.volume)

icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
volume = engine.getProperty('volume')
prev_volume = volume

def on_quit(systray):
	print("Bye")
	global terminate
	terminate = True

def on_about(systray):
	ctypes.windll.user32.MessageBoxW(None, u"Created using infi.systray, SwSpotify, pyttsx3", u"Spotify Announcer Tray", 0)

def on_change_volume(diff):
	current_volume = engine.getProperty('volume')
	target_volume = current_volume + diff
	if (target_volume > 1.0):
		target_volume = 1.0
	if (target_volume < 0.0):
		target_volume = 0.0

	engine.setProperty('volume', target_volume)
	global volume
	volume = target_volume

def on_increase_volume(systray):
	on_change_volume(0.25)

def on_decrease_volume(systray):
	on_change_volume(-0.25)

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
			song = spotify.song()
			artist = spotify.artist()
			volume_changed = False
			if (prev_volume != volume):
				volume_changed = True
			if (not(song == None or artist == None) and (song != prevsong or artist!=prevartist)):
				if (args.delay!=0):
					time.sleep(args.delay)
				engine.say("Playing " + song + " by " + artist)
				engine.runAndWait()
				print("Playing " + song + " by " + artist)
				systray.update(hover_text=artist + " - " + song)
				prevsong = song
				prevartist = artist
			if (volume_changed):
				engine.say("Current volume is " + str(volume))
				engine.runAndWait()
				print("Current volume is " + str(volume))
				prev_volume = volume

		except spotify.SpotifyNotRunning as e:
			pass
		time.sleep(1)