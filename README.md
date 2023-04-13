# Spotify Announcer Tray
Announces spotify song&artist on new track start and silently sits in taskbar tray, shows current song name on mouse hover.
Uses [Spotify Song Announcer](https://github.com/BatuhanUsluel/Spotify-Song-Announcer) to announce and [infi.systray](https://github.com/Infinidat/infi.systray) to implement windows system tray. 

Supported Platforms:
+ Windows

```
usage: pythonw spotify_announcer_tray.pyw [-h] [-l] [-s SET] [-d DELAY] [-r RATE] [-v VOLUME]

optional arguments:
	-h, --help                      Show this help message and exit
	-l, --list                      Lists available voices, quits
	-s SET, --set SET               Sets the voice
	-d DELAY, --delay DELAY         Delay before announcement(seconds)[Default: 5]
	-r RATE, --rate RATE            Speaking rate in words per minute[Default: 170]
	-v VOLUME --volume VOLUME       Set volume of announcer (0.0-1.0)[Default: 0.5]
```