import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import os
import time
import imutils
import pytesseract
from pytesseract import Output
from capture import *
from game import *

# Cleanup when script is exited
import atexit
def exit_handler():
    cv2.destroyAllWindows()
    os.system("TASKKILL /F /IM scrcpy.exe")
atexit.register(exit_handler)


window_name = "CPH1979"
w = gw.getWindowsWithTitle(window_name)
while len(w) == 0:
    w = gw.getWindowsWithTitle(window_name)
    time.sleep(0.1)
w = w[0]
w.activate()

capture_height, capture_width = w.height, w.width
print(f"h: {capture_height}, w: {capture_width}")

screen_width = 900
screen_ratio = None

fixed_x, fixed_y = None, None

mouse_down = False
drag_start_x, drag_start_y = None, None

def fixedCoordinatesToResolution(x, y):
    screen_ratio_x, screen_ratio_y = screen_ratio
    fixed_x, fixed_y = (x / screen_ratio_x), (y / screen_ratio_y)
    return (fixed_x, fixed_y)

def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_down = True
        x, y = fixedCoordinatesToResolution(x, y)
        drag_start_x, drag_start_y = x, y
    elif event == cv2.EVENT_LBUTTONUP and mouse_down:
        mouse_down = False
        x, y = fixedCoordinatesToResolution(x, y)
        drag(drag_start_x, drag_start_y, x, y)

cv2.namedWindow("pizza_game_capture")
cv2.setMouseCallback("pizza_game_capture", click)

resize_scale_percent = (60 / 100)

game = Game()

while True:
    # Capture application screen
    img = pyautogui.screenshot(region=(w.left, w.top, w.width, w.height))
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert text image to grayscale and apply binary threshold
    threshold_img = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    # Crop image
    threshold_img = threshold_img[game.text_position["y"]:game.text_position["height"], game.text_position["x"]:game.text_position["width"]]
  
    threshold_img = cv2.threshold(threshold_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # Extract text data from image
    custom_config = r'--oem 3 --psm 6'
    details = pytesseract.image_to_data(threshold_img, output_type=Output.DICT, config=custom_config, lang="eng")
    
    total_text_boxes = len(details["text"])
    game.text = ""
    # Loop through recognised text and apply a border to each word
    for i in range(total_text_boxes):
        if int(float(details["conf"][i])) > 75:
            game.text += details["text"][i] + " "

            (x, y, width, height) = (details["left"][i], details["top"][i], details["width"][i], details["height"][i])
            
            x += game.text_position["x"]
            y += game.text_position["y"]
            frame = cv2.rectangle(frame, (x, y), (x+width, y+height), (0, 255, 0), 3)
            frame = cv2.putText(frame, details["text"][i], (x, y), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    print(game.text)
    # Downscale the frame so it isn't massive
    resized_width = int(frame.shape[1] * resize_scale_percent)
    resized_height = int(frame.shape[0] * resize_scale_percent)
    frame = cv2.resize(frame, dsize=(resized_width, resized_height), interpolation=cv2.INTER_AREA)
    # Add an empty border to the frame image so that we can numpy stack it
    frame = cv2.copyMakeBorder(frame, 0, 0, 0, threshold_img.shape[1]-frame.shape[1], borderType=cv2.BORDER_CONSTANT)
    # Convert the threshold/text image to RGB so that it has the same size as the frame
    threshold_img = cv2.cvtColor(threshold_img, cv2.COLOR_GRAY2RGB)
    # Vertically stack the frame and threshold/text images
    concatenation = np.vstack((frame, threshold_img))
    
    cv2.imshow("pizza_game_capture", concatenation)


    screen_height = frame.shape[0]
    screen_ratio = (screen_width / capture_width, screen_height / capture_height)
    # print(screen_ratio, frame.shape, [capture_width, capture_height])

    # Quit application when "Q" pressed
    if cv2.waitKey(1) == ord("q"):
        break
