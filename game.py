from turtle import width


class Game:
    def __init__(self):
        self.text_position = {
            'x': 570,
            'y': 170,
            'width': 1500,
            'height': 315
        }
        self.text_position["width"] = self.text_position["x"] + self.text_position["width"]
        self.text_position["height"] = self.text_position["y"] + self.text_position["height"]