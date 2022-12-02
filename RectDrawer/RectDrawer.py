import win32gui, win32ui
from threading import Thread
from win32api import GetSystemMetrics, RGB
from enum import Enum
from time import sleep


class RectDrawerSettings(Enum):
    MIN_FRAME_RATE = 0.1
    MAX_FRAME_RATE = 10
    DEFAULT_FRAME_RATE = 1


class Color(Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)


class RectDrawer:
    def __init__(
        self, color: Color = Color.RED, persist: bool = False, updateLimit: int = 400
    ) -> None:
        """Initializes the RectDrawer class

        :param color: Color of outline, in RGB format, defaults to Color.RED
        :type color: Color|tupe(int), optional

        :param persist: Keep outline on screen thru window updates, defaults to False
        :type persist: bool, optional

        :param updateLimit: how many miliseconds to render outline, defaults to 400
        :type updateLimit: int, optional
        :note updateLimit is only used if persist is True
        :note 400 is more than enough, but if you want to change it be my guest
        """

        self.dc = win32gui.GetDC(0)
        self.dcObj = win32ui.CreateDCFromHandle(self.dc)
        self.hwnd = win32gui.WindowFromPoint((0, 0))
        self.monitor = (0, 0, GetSystemMetrics(0), GetSystemMetrics(1))
        self.color = RGB(*color.value)
        self.persist = persist

        self.updateLimit = updateLimit
        if (
            updateLimit < RectDrawerSettings.MIN_FRAME_RATE.value * 1000
            or updateLimit > RectDrawerSettings.MAX_FRAME_RATE.value * 1000
            or not isinstance(updateLimit, int)
        ):
            self.updateLimit = 100

    def _infiniDraw(self, coords: tuple) -> None:
        while True:
            self._createRect(coords)
            sleep(self.updateLimit / 1000)

    def _createRect(self, coords: list[int]) -> None:
        """Creates an outline of a rect with the SetPixel function

        :param coords: The coordinates of the rect
        """

        x1, y1, x2, y2 = coords
        for x in range(x1, x2):
            self.dcObj.SetPixel(x, y1, self.color)
            self.dcObj.SetPixel(x, y2, self.color)

        for y in range(y1, y2):
            self.dcObj.SetPixel(x1, y, self.color)
            self.dcObj.SetPixel(x2, y, self.color)

        if self.persist:
            win32gui.InvalidateRect(
                self.hwnd, self.monitor, True
            )  # Refresh the entire monitor

    def draw(self, coords: list[int]) -> None:
        """Draws a rectangle on the screen

        :param coords: The coordinates of the rectangle
        :type coords: list[int], len=4, [x1, y1, x2, y2]
        """

        if self.persist:
            # Shove it to a thread so it doesn't block the main thread
            Thread(target=self._infiniDraw, args=(coords,)).start()

        self._createRect(coords)


if __name__ == ("__main__"):
    CUBE_SIZE = 100
    PADDING = 2
    USE_PERSIST_EXAMPLE = True

    # Draw a cube in the middle of the screen

    if USE_PERSIST_EXAMPLE:
        drawer = RectDrawer(persist=True)
        drawer.draw(
            [
                GetSystemMetrics(0) // 2 - CUBE_SIZE // 2,
                GetSystemMetrics(1) // 2 - CUBE_SIZE // 2,
                GetSystemMetrics(0) // 2 + CUBE_SIZE // 2,
                GetSystemMetrics(1) // 2 + CUBE_SIZE // 2,
            ]
        )
    else:
        drawer = RectDrawer()
        drawer.draw(
            [
                GetSystemMetrics(0) // 2 - CUBE_SIZE // 2,
                GetSystemMetrics(1) // 2 - CUBE_SIZE // 2,
                GetSystemMetrics(0) // 2 + CUBE_SIZE // 2,
                GetSystemMetrics(1) // 2 + CUBE_SIZE // 2,
            ]
        )
