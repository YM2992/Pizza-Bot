import cv2
import numpy as np
import os
import time
import pytesseract
from pytesseract import Output
from capture import *
from game import Game
import imutils
import textwrap

# Cleanup when script is exited
import atexit
def exit_handler():
    cv2.destroyAllWindows()
    os.system("TASKKILL /F /IM scrcpy.exe")
atexit.register(exit_handler)

# Initialise the game object
game = Game("CPH1979")

cv2.namedWindow("pizza_game_capture")


on_hint_page = False

dbclick_armed = False

def handle_click(event, x, y, flags, param):
    global dbclick_armed
    if event == cv2.EVENT_LBUTTONDOWN:
        if dbclick_armed:
            time.sleep(1)
            game.make_pizza()
            dbclick_armed = False
        else:
            dbclick_armed = True
    elif event == cv2.EVENT_RBUTTONDOWN:
        dbclick_armed = False
cv2.setMouseCallback("pizza_game_capture", handle_click)


resize_scale_percent = (50 / 100)


def get_frame():
    img = game.get_screenshot()
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame

def in_motion(last_frame, frame):
    motion_detected = False

    return motion_detected

last_frame = get_frame()

what_clicked = False
ok_btn_details = None
reading_progress = 0
reading_ingredients_complete = False

while True:
    start_time = time.time()
    # Update game capture size
    game.update_text_bounds()

    # Capture application screen
    frame = get_frame()

    # Convert text image to grayscale and apply binary threshold
    threshold_img = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    # Crop image
    threshold_img = threshold_img[game.text_bounds["y"]:game.text_bounds["height"], game.text_bounds["x"]:game.text_bounds["width"]]

    threshold_img = cv2.threshold(threshold_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # Extract text data from image
    custom_config = r'--oem 3 --psm 12'
    details = pytesseract.image_to_data(threshold_img, output_type=Output.DICT, config=custom_config, lang="eng")
    
    game._text = ""
    # Loop through recognised text and apply a border to each word
    for i in range(len(details["text"])):
        if int(float(details["conf"][i])) > 25:
            game._text += details["text"][i] + " "

            (x, y, width, height) = (details["left"][i], details["top"][i], details["width"][i], details["height"][i])
            
            x += game.text_bounds["x"]
            y += game.text_bounds["y"]


            # Add colour-coded boundary boxes based on confidence level
            if int(float(details["conf"][i])) <= 50:
                frame = cv2.rectangle(frame, (x, y), (x+width, y+height), (0, 0, 255), 3)
                frame = cv2.putText(frame, details["text"][i], (x, y), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            elif int(float(details["conf"][i])) < 75:
                frame = cv2.rectangle(frame, (x, y), (x+width, y+height), (0, 100, 255), 3)
                frame = cv2.putText(frame, details["text"][i], (x, y), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            else:
                frame = cv2.rectangle(frame, (x, y), (x+width, y+height), (0, 255, 0), 3)
                frame = cv2.putText(frame, details["text"][i], (x, y), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)


            if "what?" in details["text"][i].lower():
                if what_clicked == False:
                    game.click(int(x + 0.5 * width), int(y + 0.5 * height), print_text="what?")
            
            if "hint" in details["text"][i].lower():
                on_hint_page = True
                game.click(int(x + 0.5 * width), int(y + 0.5 * height), print_text="hint")
            

            if on_hint_page:
                if "okay" in details["text"][i].lower():
                    ok_btn_details = {
                        "left": x,
                        "top": y,
                        "width": width,
                        "height": height,
                        "text": details["text"][i]
                    }

    # if not dbclick_armed:
    #     print("TEXT: {%s} | ORDER: %s" % (game._text, game.get_order()))
    order = game.get_order()
    if not on_hint_page:
        # print("Text: {%s} | Ingredients: {%s}" % (game._text, ingredients))
        pass
    else:
        if ok_btn_details and not reading_ingredients_complete:
            if reading_progress < 15:
                reading_progress += 1
                print("reading_progress=%s/20" % (reading_progress))
            else:
                reading_progress = 0
                reading_ingredients_complete = True

        if reading_ingredients_complete and ok_btn_details:
            print(ok_btn_details)
            (ok_x, ok_y, ok_w, ok_h) = (ok_btn_details["left"], ok_btn_details["top"], ok_btn_details["width"], ok_btn_details["height"])
            game.click(int(ok_x + ok_w), int(ok_y + ok_h), print_text="okayButton")
            time.sleep(2)

            print("PIZZA ORDER %s" % (order))
            game.make_pizza()

            what_clicked = False
            on_hint_page = False
            ok_btn_details = None
            reading_ingredients_complete = False
 

    # Downscale the frame so it isn't massive
    resized_width = int(frame.shape[1] * resize_scale_percent)
    resized_height = int(frame.shape[0] * resize_scale_percent)
    frame = cv2.resize(frame, dsize=(resized_width, resized_height), interpolation=cv2.INTER_AREA)

    threshold_img = imutils.resize(threshold_img, width=750)
    

    # Add an empty border to the frame image so that we can numpy stack it
    if frame.shape[1] < threshold_img.shape[1]:
        frame = cv2.copyMakeBorder(frame, 0, threshold_img.shape[0]-frame.shape[0], 0, 0, borderType=cv2.BORDER_CONSTANT)
    else:
        threshold_img = cv2.copyMakeBorder(threshold_img, 0, frame.shape[0]-threshold_img.shape[0], 0, 0, borderType=cv2.BORDER_CONSTANT)
    
    # Time taken for code execution in seconds
    frame = cv2.putText(frame, "{:.2f}".format(time.time() - start_time)+"s", (0, 30), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 0, 255), 3)

    # Convert the threshold image to RGB so that it has the same size as the frame
    threshold_img = cv2.cvtColor(threshold_img, cv2.COLOR_GRAY2RGB)
    
    # Horizontally stack the frame and threshold images
    concatenation = np.hstack((frame, threshold_img))
    
    blank_img = np.zeros((concatenation.shape[0], concatenation.shape[1], 3), np.uint8)
    blank_img_text = f"Text:\n{game._text}\n-\n-\nOrder:\n{order}"
    blank_img_text = blank_img_text.split('\n')
    blank_img_text = [line for para in blank_img_text for line in textwrap.wrap(para, width=45, break_long_words=False, replace_whitespace=False)]
    for i, line in enumerate(blank_img_text):
        line_gap = cv2.getTextSize(line, fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=2, thickness=2)[0][1] + 10

        x = 0
        y = int(30 + i * line_gap)

        blank_img = cv2.putText(blank_img, line, (x, y), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=2, color=(255, 255, 255), thickness=2)

    # concatenation = np.vstack((concatenation, blank_img))

    cv2.imshow("pizza_game_capture", concatenation)
    cv2.imshow("pizza_game_log", blank_img)

    # Quit application when "Q" pressed
    if cv2.waitKey(1) == ord("q"):
        break
