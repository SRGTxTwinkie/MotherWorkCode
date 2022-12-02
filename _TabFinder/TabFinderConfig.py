from json import dump
from json import load


class TabFinderSettings:
    def __init__(self) -> None:
        self.topLeft = (0, 0)
        self.bottomRight = (0, 0)
        self.isDebug = False
