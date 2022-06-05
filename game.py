import math
import random
import pyautogui
import pygetwindow as gw
import time
import string

class Game:
    # Current states
    _making_pizza = False
    _order = []
    _text = ""

    # Ingredients
    available_toppings = ["sauce", "cheese", "pepperoni", "sausage", "mushroom", "olive", "eggplant"]
    # Positions
    positions = {
        "base_0": (1055, 680),
        "dough_0": (475, 485),
        "dough_1": (635, 485),
        "dough_2": (475, 600),
        "dough_3": (635, 600),
        "dough_4": (475, 715),
        "dough_5": (635, 715),
        "dough_6": (475, 830),
        "dough_7": (635, 830),
        "sauce": (535, 235),
        "cheese": (905, 235),
        "pepperoni": (1195, 235),
        "sausage": (1495, 235),
        "mushroom": (1790, 235),
        "eggplant": (2080, 235),
        "olive": (2080, 510),
        
        "paddle_0": (1055, 930),
        "oven_entry": (2200, 680),

        "oven_exit": (100, 570),
        "move_to_cutting": (50, 680),
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

        print(self.positions)

        # Update positions with increment
        # for key in self.positions:
        #     position = self.positions.get(key)
        #     i_x, i_y = position[0], position[1]
        #     i_x += 260
            
        #     self.positions[key] = (i_x, i_y)
        
        # print(self.positions)

        # Set positions to be proportionate to the current width and height
        for i in self.positions:
            i_x, i_y = self.positions.get(i)[0], self.positions.get(i)[1]
            i_x = int(i_x / 2352 * self.window.width)
            i_y = int(i_y / 1119 * self.window.height)

            self.positions[i] = (i_x, i_y)            

    # Update the bounds of text capture when the ABD window is resized
    def update_text_bounds(self):        
        self.text_bounds = {
            'x': int(620 / 2352 * self.window.width),
            'y': int(175 / 1119 * self.window.height),
            'width': int(1450 / 2352 * self.window.width),
            'height': int(650 / 1119 * self.window.height)
        }

        self.text_bounds["width"] = self.text_bounds["x"] + self.text_bounds["width"]
        self.text_bounds["height"] = self.text_bounds["y"] + self.text_bounds["height"]
    
    # Capture and return a screenshot of the ADB window
    def get_screenshot(self):
        return pyautogui.screenshot(region=(self.window.left, self.window.top, self.window.width, self.window.height))
    
    # Convert a word to an integer
    def word_to_int(self, word):
        word_integers = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight"]
        
        if word not in word_integers:
            return f"Word '{word}' could not be converted to an integer"

        return word_integers.index(word)

    def get_toppings(self, pizza, pizza_order, current_half):
        # Find toppings for each half
        for topping in pizza.split():
            if topping not in self.available_toppings:
                # If part of the word exists in available_toppings. Example: "olives" or "olives!"
                if topping[:len(topping)-1] not in self.available_toppings:
                    topping = topping[:len(topping)-1] # Cut word down one letter. Example: "olive" or "olives"
                # If part of the word exists in available_toppings. Example: "olives" or "olives!"
                if topping not in self.available_toppings:
                    topping = topping[:len(topping)-1] # Cut word down one letter. Example: "olive" or "olives"
            
                if topping not in self.available_toppings:
                    continue
            
            # Ingredient is already in the list
            if topping in pizza_order["toppings_%s" % (current_half)]:
                continue

            # Ingredient is acceptable, add it to the list
            pizza_order["toppings_%s" % (current_half)].append(topping)
            continue

        # Add sauce and cheese if they weren't already added but should be
        if "cheese" not in pizza_order["toppings_%s" % (current_half)] and "cheese" in pizza:
            pizza_order["toppings_%s" % (current_half)].insert(0, "cheese")
        if "sauce" not in pizza_order["toppings_%s" % (current_half)] and "sauce" in pizza:
            pizza_order["toppings_%s" % (current_half)].insert(0, "sauce")
        
    # Get order from sentence
    def get_order(self):
        if self._making_pizza:
            return "Currently making pizza"
                
        requested_order = []
        
        # Remove punctuation marks from the sentence, e.g. (".,!?")
        # self._text = str(self._text).lower().translate(str.maketrans("", "", string.punctuation))
        self._text = str(self._text).lower().replace("...", "")
        
        # Split the sentence into each pizza order
        pizzas = self._text.split("for")

        for pizza in pizzas:
            pizza_order = {
                "half_and_half": False,
                "toppings_0": [],
                "toppings_1": [],
                "slices": 6
            }

            # if half_and_half then
                # Split pizza into each half
                # Within each half
                    # Add the toppings to the half

            # Check if this pizza should be half and half
            if "half" in pizza:
                pizza_order["half_and_half"] = True
            
            # Check how many slices the pizza should be cut into
            if "cut into" in pizza:
                words = pizza.split()
                word = words[words.index("into") + 1]
                print("cut into: ", word)
                word_to_slices = self.word_to_int(word)
                pizza_order["slices"] = word_to_slices
            
            if pizza_order["half_and_half"]:
                # Split pizza into each half
                pizza_halves = pizza.split("half")
                pizza_halves.pop(0)
                print("PIZZA_HALVES: ", pizza_halves)
                if len(pizza_halves) > 1:
                    for index, half in enumerate(pizza_halves):
                        print(index, half)
                        self.get_toppings(half, pizza_order, index)
            else:
                # Regular pizza, each half is the same
                self.get_toppings(pizza, pizza_order, 0)
                self.get_toppings(pizza, pizza_order, 1)
 
            
            if len(pizza_order["toppings_0"]) > 0 and len(pizza_order["toppings_1"]) > 0:
                requested_order.append(pizza_order)
        
        self._order = requested_order
        return self._order

    # Get ingredients from a sentence
    def get_ingredients(self, sentence):
        if self._making_pizza:
            return "Currently making pizza"

        self.requested_ingredients = []
        sentence = str(sentence).lower().translate(str.maketrans('', '', string.punctuation))
        for index, word in enumerate(sentence.split()):
            word = str(word).lower()

            if word not in self.available_toppings:
                # If part of the word exists in available_toppings. Example: "olives" or "olives!"
                if word[:len(word)-1] not in self.available_toppings:
                    word = word[:len(word)-1] # Cut word down one letter. Example: "olive" or "olives"
                # If part of the word exists in available_toppings. Example: "olives" or "olives!"
                if word not in self.available_toppings:
                    word = word[:len(word)-1] # Cut word down one letter. Example: "olive" or "olives"
                
                if word not in self.available_toppings:
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
        return self.positions[ingredient]

    def place_toppings(self, half=0):
        print("!!!!! PLACING TOPPINGS !!!!!")

        total_toppings = 9
        radius = 160

        centre_x, centre_y = self.get_ingredient_position("base_0")

        for i in range(1, total_toppings + 1):
            supplamentary_angle = 180 * half

            theta = math.radians((180 / total_toppings * i) - 90 + supplamentary_angle)

            if (i + 1) % 3 == 0:
                rand_radius = radius - 100
            else:
                rand_radius = radius

            # rand_radius = radius * (random.randint(7, 10) / 10)
            x = rand_radius * math.cos(theta) + centre_x
            y = rand_radius * math.sin(theta) + centre_y
            self.click(x, y)
    
    def bake_pizza(self):
        print("!!!!! BAKING PIZZA !!!!!")
        paddle_x, paddle_y = self.get_ingredient_position("paddle_0")
        self.moveTo(paddle_x, paddle_y)
        self.dragTo((paddle_x, paddle_y), self.get_ingredient_position("oven_entry"))

    def move_to_cutting_board(self, reversed=False):
        if reversed:
            print("!!!!! SCROLLING TO PREPARATION BOARD !!!!!")
            # Move back to the prepping board
            self.dragTo(self.get_ingredient_position("move_to_cutting"), self.get_ingredient_position("oven_entry"))
            self.dragTo(self.get_ingredient_position("move_to_cutting"), self.get_ingredient_position("oven_entry"))
        else:
            print("!!!!! SCROLLING TO CUTTING BOARD !!!!!")
            # Move to cutting boarding
            self.dragTo(self.get_ingredient_position("oven_entry"), self.get_ingredient_position("move_to_cutting"))
            self.dragTo(self.get_ingredient_position("oven_entry"), self.get_ingredient_position("move_to_cutting"))
        
        # Give the screen time to return to stationary
        time.sleep(1)

    def cut_pizza(self, pizza_order):
        print("!!!!! CUTTING PIZZA !!!!!")

        cuts = int(pizza_order["slices"] / 2)
        radius = 300

        centre_x, centre_y = self.get_ingredient_position("cutting_board")

        for i in range(1, cuts + 1):
            theta = math.radians((360 / cuts * i) - 90)
            x = radius * math.cos(theta) + centre_x
            y = radius * math.sin(theta) + centre_y

            self.dragTo(self.get_ingredient_position("cutting_tool"), (x, y))

    def pack_pizza(self):
        print("!!!!! PACKING PIZZA !!!!!")
        self.dragTo(self.get_ingredient_position("cutting_board"), (1500, 560))


    def make_pizza(self):
        if self._making_pizza:
            return "Already making pizza"
        elif len(self._order) == 0:
            return "0 ingredients requested on pizza"

        self._making_pizza = True
        
        # self.move_to_cutting_board(reversed=True)

        # Go through each pizza order
        for index, pizza in enumerate(self._order):
            # If this is the second or third.. pizza then move back to the prepping board
            # index = self._order.index(pizza)
            # if index > 0:
            #     self.move_to_cutting_board(reversed=True)
            self.move_to_cutting_board(reversed=True)

            # Spread dough onto paddle
            doughposx, doughposy = self.get_ingredient_position(f"dough_{self.dough_count}")
            print(doughposx, doughposy, self.dough_count)
            self.click(doughposx, doughposy, print_text="dough")
            self.dough_count += 1
            time.sleep(2)

            # Place toppings on pizza
            for topping in pizza["toppings_0"]:
                time.sleep(0.25)
                ingredient_x, ingredient_y = self.get_ingredient_position(topping)
                self.click(ingredient_x, ingredient_y, pause=True, print_text="ingredient", clicks=1)

                self.place_toppings(half=0)

            for topping in pizza["toppings_1"]:
                time.sleep(0.25)
                ingredient_x, ingredient_y = self.get_ingredient_position(topping)
                self.click(ingredient_x, ingredient_y, pause=True, print_text="ingredient", clicks=1)

                self.place_toppings(half=1)
        
            self.bake_pizza()

            # Scroll screen to cutting board
            self.move_to_cutting_board()

            # Wait for the pizza to be cooked
            time.sleep(9)

            # Drag pizza onto the cutting board
            self.dragTo(self.get_ingredient_position("oven_exit"), self.get_ingredient_position("cutting_board"))

            # Cut and pack the pizza
            self.cut_pizza(pizza_order=pizza)
            self.pack_pizza()

        # Wait for screen to transition back to customer
        time.sleep(3)

        # Hand the pizza to the customer
        self.dragTo((750, 1000), (400, 550))

        self._making_pizza = False

    ### Actions
    # CHeck if provided (x, y) coordinates are within the window's bounds
    def is_in_bounds(self, x, y):
        if (x + self.window.left > self.window.width + self.window.left) or (y + self.window.top > self.window.height + self.window.top):
            print("COORDS {%s,%s} OUT OF BOUNDS" % (x, y))
            return False
        return True
    
    def moveTo(self, x, y, pause=False, print_text=""):
        if not self.is_in_bounds(x, y):
            return

        pyautogui.moveTo(x=x, y=y, _pause=pause, duration=0.5)

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
        pyautogui.moveTo(x=x, y=y, _pause=False, duration=0.01)
        time.sleep(0.01)
        pyautogui.click(x=x, y=y, button="left", clicks=clicks, _pause=False, duration=0.05)
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