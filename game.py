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
    
    # Update the bounds of text capture when the ABD window is resized
    def update_text_bounds(self):        
        self.text_bounds = {
            'x': int(570 / 2352 * self.window.width),
            'y': int(175 / 1119 * self.window.height),
            'width': int(1500 / 2352 * self.window.width),
            'height': int(330 / 1119 * self.window.height)
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

    def get_recipe(self):
        pass

    def get_ingredient_position(self, ingredient):
        return self.ingredient_positions[ingredient]

    def place_in_circle(self):
        total_ingredients = 18
        theta = math.radians(360 / total_ingredients)
        radius = 160

        centre_x, centre_y = self.get_ingredient_position("base_0")

        for i in range(1, total_ingredients + 1):
            theta = math.radians(360 / total_ingredients * i)
            x = radius * math.cos(theta) + centre_x
            y = radius * math.sin(theta) + centre_y
            self.click(x, y)

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
        self.click(doughposx, doughposy)
        self.dough_count += 1
        time.sleep(0.5)

        # For each ingredient
            # MoveTo ingredient
            # Click ingredient
            # Click base
        base_x, base_y = self.get_ingredient_position("base_0")
        for ingredient in self.requested_ingredients:
            time.sleep(0.5)
            ingredient_x, ingredient_y = self.get_ingredient_position(ingredient)
            self.click(ingredient_x, ingredient_y)

            self.place_in_circle()
            # self.click(base_x, base_y)
        
        self._making_pizza = False

    ### Actions
    # CHeck if provided (x, y) coordinates are within the window's bounds
    def is_in_bounds(self, x, y):
        if (x + self.window.left > self.window.width + self.window.left) or (y + self.window.top > self.window.height + self.window.top):
            return False
        return True
    
    # Click on the website
    def click(self, x, y):
        print("CLICKED x%s y%s" % (x, y))

        if not self.is_in_bounds:
            return

        # Calculate (x, y) in terms of the window position
        x += self.window.left
        y += self.window.top

        # Move cursor to (x, y)
        pyautogui.moveTo(x, y, _pause=False)

        # Click mouse
        pyautogui.click(button="left")

    def drag(self, drag_from, drag_to):
        if not self.is_in_bounds:
            return

        from_x, from_y = drag_from
        to_x, to_y = drag_to

        # Calculate x, y coordinates in terms of the window position
        from_x += self.window.left
        from_y += self.window.top

        to_x += self.window.left
        to_y += self.window.top

        # Move cursor to (from_x, from_y)
        pyautogui.moveTo(from_x, from_y, _pause=False)

        # Drag cursor to (to_x, to_y)
        pyautogui.dragTo(to_x, to_y, button="left")