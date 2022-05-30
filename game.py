from turtle import width


class Game:
    def __init__(self, capture_width, capture_height):
        # Customer dialogue text box position
        self.update_capture_bounds(capture_width, capture_height)

        # Ingredients
        self.valid_ingredients = ["sauce", "cheese", "pepperoni", "sausage", "mushroom", "olive"]

        # Recipes
        self.recipes = {
            "cheese": ["sauce"]
        }

    def update_capture_bounds(self, new_width, new_height):
        self.capture_width, self.capture_height = new_width, new_height
        
        self.text_bounds = {
            'x': int(570 / 2352 * self.capture_width),
            'y': int(170 / 1119 * self.capture_height),
            'width': int(1500 / 2352 * self.capture_width),
            'height': int(315 / 1119 * self.capture_height)
        }

        self.text_bounds["width"] = self.text_bounds["x"] + self.text_bounds["width"]
        self.text_bounds["height"] = self.text_bounds["y"] + self.text_bounds["height"]
        

    def get_recipe(self, words):
        self.requested_ingredients = []
        words = str(words).lower().strip(".")
        for index, word in enumerate(words.split()):
            word = str(word).lower()
            print(word)

            if word not in self.valid_ingredients:
                # If part of the word exists in valid_ingredients. Example: "olives" or "olives!"
                if word[:len(word)-1] not in self.valid_ingredients:
                    word = word[:len(word)-1] # Cut word down one letter. Example: "olive" or "olives"
                print(word)
                # If part of the word exists in valid_ingredients. Example: "olives" or "olives!"
                if word not in self.valid_ingredients:
                    word = word[:len(word)-1] # Cut word down one letter. Example: "olive" or "olives"
                
                print(word)
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
            if words[index - 1] == "no":
                continue

            if "less" in word:
                continue

            # Ingredient is acceptable, add it to the list
            self.requested_ingredients.append(word)
            continue
        
        return self.requested_ingredients