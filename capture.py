from asyncio.windows_events import NULL
from inspect import modulesbyfile
import os
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import PIL.ImageGrab as ImageGrab
import imutils
import time
import psutil


def checkIfProcessRunning(processName):
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

# Prevent multiple screens from running
if checkIfProcessRunning('scrcpy.exe'):
	print('>> Android screen already mirrored')
	os.system('start scrcpy-win64/scrcpy-noconsole.vbs')
else:
	print('>> Mirroring android screen')
	os.system('start scrcpy-win64/scrcpy-noconsole.vbs')

#Reading paths
orig_dir = os.getcwd()
adb_dir = os.path.join(os.getcwd(), "scrcpy-win64")


# Finger events
def tap(x,y):
	try:
		os.chdir(adb_dir)
		tap_coordinates = f"adb shell input tap {x} {y}"
		os.system(tap_coordinates) # Run the adb command
		os.chdir(orig_dir)
	except Exception as e:
		print(e)
		cv2.destroyAllWindows()
		input('>> adb failed, press Enter to continue')

drag_duration = 100
def drag(x1, y1, x2, y2):
	try:
		os.chdir(adb_dir)
		tap_coordinates = f"adb shell input swipe {x1} {y1} {x2} {y2} {drag_duration}"
		os.system(tap_coordinates) # Run the adb command
		os.chdir(orig_dir)
	except Exception as e:
		print(e)
		cv2.destroyAllWindows()
		input('>> adb failed, press Enter to continue')