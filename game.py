import math
import pyautogui
import pygetwindow as gw
import time
import string

class Game:
    # Current states
    _making_pizza = False

    # Ingredients
    valid_ingredients = ["sauce", "cheese", "pepperoni", "sausage", "mushroom", "olive", "eggplant"]
    requested_ingredients = []
    # Positions
    ingredient_positions = {
        "base_0": (795, 680),
        "dough_0": (215, 485),
        "dough_1": (375, 485),
        "dough_2": (215, 600),
        "dough_3": (375, 600),
        "dough_4": (215, 715),
        "dough_5": (375, 715),
        "dough_6": (215, 830),
        "dough_7": (375, 830),
        "sauce": (275, 235),
        "cheese": (645, 235),
        "pepperoni": (935, 235),
        "sausage": (1235, 235),
        "mushroom": (1530, 235),
        "eggplant": (1820, 235),
        "olive": (1820, 510),
        
        "paddle_0": (795, 930),
        "oven_entry": (2000, 680),
        "move_to_cutting": (10, 680),
        "oven_exit": (145, 580),
        "cutting_board": (850, 560),
        "cutting_tool": (1100, 285)
    }
    # Counts
    dough_count = 0

    def __init__(self, window_name):
        # Get the window of the phone ADB/scrcpy application to capture
        self.window = gw.getWindowsWithTitle(window_name)
        while len(self.window) == 0:
            self.window = gw.getWindowsWithTitle(window_name)
            time.sleep(0.1)
        self.window = self.window[0]
        self.window.activate()

        print(f"w: {self.window.width}, h: {self.window.height}")

        # Update customer dialogue text box bounds
        self.update_text_bounds()

        # Set ingredient_positions to be proportionate to the current width and height
        for i in self.ingredient_positions:
            i_x, i_y = self.ingredient_positions.get(i)[0], self.ingredient_positions.get(i)[1]
            i_x = int(i_x / 2352 * self.window.width)
            i_y = int(i_y / 1119 * self.window.height)
        
        print(self.ingredient_positions)
            

    # Update the bounds of text capture when the ABD window is resized
    def update_text_bounds(self):        
        self.text_bounds = {
            'x': int(590 / 2352 * self.window.width),
            'y': int(175 / 1119 * self.window.height),
            'width': int(1480 / 2352 * self.window.width),
            'height': int(650 / 1119 * self.window.height)
        }

        self.text_bounds["width"] = self.text_bounds["x"] + self.text_bounds["width"]
        self.text_bounds["height"] = self.text_bounds["y"] + self.text_bounds["height"]
    
    # Capture and return a screenshot of the ADB window
    def get_screenshot(self):
        return pyautogui.screenshot(region=(self.window.left, self.window.top, self.window.width, self.window.height))
    
    # Get ingredients from a sentence
    def get_ingredients(self, sentence):
        if self._making_pizza:
            return "Currently making pizza"

        self.requested_ingredients = []
        sentence = str(sentence).lower().translate(str.maketrans('', '', string.punctuation))
        for index, word in enumerate(sentence.split()):
            word = str(word).lower()

            if word not in self.valid_ingredients:
                # If part of the word exists in valid_ingredients. Example: "olives" or "olives!"
                if word[:len(word)-1] not in self.valid_ingredients:
                    word = word[:len(word)-1] # Cut word down one letter. Example: "olive" or "olives"
                # If part of the word exists in valid_ingredients. Example: "olives" or "olives!"
                if word not in self.valid_ingredients:
                    word = word[:len(word)-1] # Cut word down one letter. Example: "olive" or "olives"
                
                if word not in self.valid_ingredients:
                    continue

            # Ingredient is already in the list
            if word in self.requested_ingredients:
                continue
            
            # The first word of provided words
            if index == 0:
                self.requested_ingredients.append(word)
                continue

            # Handle requests that ask for none of that ingredient
            if sentence[index - 1] == "no":
                continue
            if "less" in word:
                continue

            # Ingredient is acceptable, add it to the list
            self.requested_ingredients.append(word)
            continue
            
        # Add sauce and cheese if they weren't added but should be
        if "sauce" not in self.requested_ingredients and "sauce" in sentence:
            self.requested_ingredients.insert(0, "sauce")

        if "cheese" not in self.requested_ingredients and "cheese" in sentence:
            self.requested_ingredients.insert(0, "cheese")
        
        return self.requested_ingredients


    def get_ingredient_position(self, ingredient):
        return self.ingredient_positions[ingredient]

    def place_in_circle(self):
        total_ingredients = 18
        radius = 160

        centre_x, centre_y = self.get_ingredient_position("base_0")

        for i in range(1, total_ingredients + 1):
            theta = math.radians(360 / total_ingredients * i)
            x = radius * math.cos(theta) + centre_x
            y = radius * math.sin(theta) + centre_y
            self.click(x, y)
    
    def bake_pizza(self):
        self.dragTo(self.get_ingredient_position("paddle_0"), self.get_ingredient_position("oven_entry"))
        print("!!!!! BAKING PIZZA !!!!!")
    
    def cut_pizza(self):
        print("!!!!! CUTTING PIZZA !!!!!")

        cuts = 6
        radius = 300

        centre_x, centre_y = self.get_ingredient_position("cutting_board")

        for i in range(1, cuts + 1):
            theta = math.radians(360 / cuts * i)
            x = radius * math.cos(theta) + centre_x
            y = radius * math.sin(theta) + centre_y

            self.dragTo(self.get_ingredient_position("cutting_tool"), (x, y))


    def make_pizza(self):
        if self._making_pizza:
            return "Already making pizza"
        elif len(self.requested_ingredients) == 0:
            return "0 ingredients requested on pizza"

        self._making_pizza = True
        
        # MoveTo dough
        # Click dough
        doughposx, doughposy = self.get_ingredient_position(f"dough_{self.dough_count}")
        print(doughposx, doughposy, self.dough_count)
        self.click(doughposx, doughposy, print_text="dough")
        self.dough_count += 1
        time.sleep(2)

        # For each ingredient
            # MoveTo ingredient
            # Click ingredient
            # Click base
        base_x, base_y = self.get_ingredient_position("base_0")
        for ingredient in self.requested_ingredients:
            time.sleep(0.25)
            ingredient_x, ingredient_y = self.get_ingredient_position(ingredient)
            self.click(ingredient_x, ingredient_y, pause=True, print_text="ingredient", clicks=2)

            self.place_in_circle()
            # self.click(base_x, base_y)
        
        # Pizza made, now bake it
        self.bake_pizza()

        # Scroll screen to cutting board
        self.dragTo(self.get_ingredient_position("oven_entry"), self.get_ingredient_position("move_to_cutting"))
        self.dragTo(self.get_ingredient_position("oven_entry"), self.get_ingredient_position("move_to_cutting"))
        # self.drag((2000, 680), (10, 680))

        # Wait for the pizza to be cooked
        time.sleep(9)

        # Drag pizza onto the cutting board
        self.dragTo(self.get_ingredient_position("oven_exit"), self.get_ingredient_position("cutting_board"))
        # self.drag((200, 570), (1600, 520))

        # Cut pizza
        self.cut_pizza()

        self._making_pizza = False

    ### Actions
    # CHeck if provided (x, y) coordinates are within the window's bounds
    def is_in_bounds(self, x, y):
        if (x + self.window.left > self.window.width + self.window.left) or (y + self.window.top > self.window.height + self.window.top):
            print("COORDS {%s,%s} OUT OF BOUNDS" % (x, y))
            return False
        return True
    
    # Click the mouse at (x, y)
    def click(self, x, y, pause=False, print_text="", clicks=1):
        if print_text:
            print("%s CLICKED x%s y%s" % (print_text, x, y))

        if not self.is_in_bounds(x, y):
            return

        # Calculate (x, y) in terms of the window position
        x += self.window.left
        y += self.window.top

        # Move cursor to (x, y)
        # Click mouse
        mouse_duration = 0
        if pause:
            mouse_duration = 0.05
        else:
            mouse_duration = 0.1
        time.sleep(0.01)
        pyautogui.click(x=x, y=y, button="left", clicks=clicks, _pause=False, duration=0)
        time.sleep(0.01)

    # Drag the mouse from drag_from(x,y) to drag_to(x,y)
    def dragTo(self, drag_from, drag_to):
        from_x, from_y = drag_from
        to_x, to_y = drag_to

        if not self.is_in_bounds(from_x, from_y):
            return print("dragTo FROM NOT IN BOUNDS")
        if not self.is_in_bounds(to_x, to_y):
            return print("dragTo TO NOT IN BOUNDS")

        # Calculate x, y coordinates in terms of the window position
        from_x += self.window.left
        from_y += self.window.top

        to_x += self.window.left
        to_y += self.window.top

        print("DRAGGING FROM %s to %s" % (drag_from, drag_to))

        # Move cursor to (from_x, from_y)
        pyautogui.moveTo(from_x, from_y, duration=0.1)

        # Drag cursor to (to_x, to_y)
        pyautogui.dragTo(to_x, to_y, button="left", duration=0.5)
    
    # Drag the mouse from current(x,y) to drag_to(x,y)
    def drag(self, x, y):
        current_x, current_y = self.position()
        self.dragTo((current_x, current_y), (x, y))