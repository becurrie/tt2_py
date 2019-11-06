from .constants import (
    MEMU_WINDOW_FILTER, NOX_WINDOW_FILTER
)

from pyautogui import _failSafeCheck

from PIL import Image
from threading import Lock
from ctypes import windll

import win32gui
import win32ui
import win32api
import win32con

import time


class Window(object):
    """Window can be used to define a single window/process."""
    SUPPORTED_CLICK_EVENTS = {
        "left": (win32con.WM_LBUTTONDOWN, win32con.WM_LBUTTONUP),
        "right": (win32con.WM_RBUTTONDOWN, win32con.WM_RBUTTONUP),
        "middle": (win32con.WM_MBUTTONDOWN, win32con.WM_MBUTTONUP),
    }

    EMULATOR_WIDTH = 480
    EMULATOR_HEIGHT = 800

    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.x_subtract = 0

        # Depending on the type of emulator being used (and supported), some differences in the way their window object is defined.
        # Nox: X Axis is not included in window rectangle.  MEmu: X Axis is included. Based on these differences, we should modify appropriately
        # the width and height values before calculating padding.
        if self.text.lower() in MEMU_WINDOW_FILTER:
            self.x_subtract = 38

        # We use a lock object to ensure that screenshots are only ever taken by a single
        # thread, we do this to avoid issues with the win32api and ctypes implementations.
        self.lock = Lock()

    def __str__(self):
        return "{text} ({x}, {y}, {w}, {h})".format(
            text=self.text, x=self.x, y=self.y, w=self.width, h=self.height)

    def __repr__(self):
        return "<Window: {window}>".format(window=self)

    @property
    def text(self):
        return win32gui.GetWindowText(self.hwnd)

    @property
    def rect(self):
        return win32gui.GetClientRect(self.hwnd)

    @property
    def x_padding(self):
        return self.width - 480

    @property
    def y_padding(self):
        return self.height - 800

    @property
    def x(self):
        return self.rect[0] + self.x_padding

    @property
    def y(self):
        return self.rect[1] + self.y_padding

    @property
    def width(self):
        return self.rect[2] - self.x_subtract

    @property
    def height(self):
        return self.rect[3]

    def find(self, search):
        """
        Check if the specified search key is present in the windows text.
        """
        if type(search) == str:
            search = [search]

        for s in search:
            if self.text.lower().find(s.lower()) != -1:
                return True

        return False

    def click(self, point, clicks=1, interval=0.0, button="left", pause=0.0):
        """
        Perform a click on the given window in the background.

        Sending a message to the specified window so the click takes place
        whether the window is visible or not.
        """
        _failSafeCheck()
        evt_d = self.SUPPORTED_CLICK_EVENTS[button][0]
        evt_u = self.SUPPORTED_CLICK_EVENTS[button][1]

        param = win32api.MAKELONG(
            point[0],
            point[1] + self.y_padding
        )

        # Loop through all clicks that should take place.
        for x in range(clicks):
            _failSafeCheck()
            win32api.SendMessage(self.hwnd, evt_d, 1, param)
            win32api.SendMessage(self.hwnd, evt_u, 0, param)

            # Interval sleeping?
            if interval:
                time.sleep(interval)

        # Pausing after clicks are finished?
        if pause:
            time.sleep(pause)

    def drag_mouse(self, start, end, button="left", pause=0.5):
        """
        Perform a mouse drag on the given window in the background.

        Sending a message to the specified window so the drag can take place whether
        the window is visible or not.
        """
        _failSafeCheck()
        evt_d = self.SUPPORTED_CLICK_EVENTS[button][0]
        evt_u = self.SUPPORTED_CLICK_EVENTS[button][1]

        start_param = win32api.MAKELONG(
            start[0],
            start[1] + self.y_padding
        )
        end_param = win32api.MAKELONG(
            end[0],
            end[1] + self.y_padding
        )

        # Perform actionable click on start point just to ensure that
        # our drag will take place.

        # Moving the mouse to the starting position for the mouse drag.
        # Mouse left button is DOWN after this point.
        win32api.SendMessage(self.hwnd, evt_d, 1, start_param)

        # How many mouse movements are needed to complete our drag?
        # DOWN DRAG
        if start[1] > end[1]:
            down = True
            clicks = start[1] - end[1]
        # UP DRAG.
        else:
            down = False
            clicks = end[1] - start[1]

        time.sleep(0.05)
        for i in range(clicks):
            param = win32api.MAKELONG(start[0], start[1] - i if down else start[1] + i)
            win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, 1, param)
            time.sleep(0.001)

        time.sleep(0.1)
        win32api.SendMessage(self.hwnd, evt_u, 0, end_param)

        if pause:
            time.sleep(pause)

    def screenshot(self, region=None):
        """
        Take a screenshot of the current window. The window may be visible or behind another window.
        """
        with self.lock:
            hwnd_dc = win32gui.GetWindowDC(self.hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, self.width, self.height)
            save_dc.SelectObject(save_bitmap)

            result = windll.user32.PrintWindow(self.hwnd, save_dc.GetSafeHdc(), 0)

            bmp_info = save_bitmap.GetInfo()
            bmp_str = save_bitmap.GetBitmapBits(True)
            image = Image.frombuffer("RGB", (bmp_info["bmWidth"], bmp_info["bmHeight"]), bmp_str, "raw", "BGRX", 0, 1)

            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwnd_dc)
            win32gui.DeleteObject(save_bitmap.GetHandle())

            image = image.crop(box=(0, self.y_padding, self.EMULATOR_WIDTH, self.EMULATOR_HEIGHT + self.y_padding))
            if not region:
                return image

            # If we have a region available, we can crop the screenshot
            # to represent the specified region of the emulator.
            return image.crop(box=region)

    def json(self):
        """Convert window instance to a json compliant dictionary."""
        return {
            "hwnd": self.hwnd,
            "text": self.text,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "formatted": str(self)
        }


class WindowNotFoundError(Exception):
    pass


class InvalidHwndValue(Exception):
    pass


class WindowHandler(object):
    """Window handle encapsulates all functionality for handling windows and processes needed."""
    def __init__(self):
        self.filter_lst = MEMU_WINDOW_FILTER + NOX_WINDOW_FILTER
        self.windows = dict()

    def _cb(self, hwnd, extra):
        """Callback handler used when current windows are enumerated."""
        if hwnd in self.windows:
            pass

        self.windows[hwnd] = Window(hwnd=hwnd)

    def enum(self):
        """Begin enumerating windows and generate windows objects."""
        win32gui.EnumWindows(self._cb, None)

    def grab(self, hwnd):
        self.enum()

        try:
            return self.windows[int(hwnd)]
        except KeyError:
            raise WindowNotFoundError()
        except ValueError:
            raise InvalidHwndValue()

    def filter(self, ignore_hidden=True, ignore_smaller=(480, 800)):
        """
        Filter the currently available windows to ones that contain the specified text.

        Hidden (ie: 0x0 sized windows are ignored by default).
        Smaller: (ie: Windows smaller than the specified amount).
        """
        dct = {hwnd: window for hwnd, window in self.windows.items() if window.find(self.filter_lst)}
        if ignore_hidden:
            dct = {hwnd: window for hwnd, window in dct.items() if window.width != 0 and window.height != 0}
        if ignore_smaller:
            dct = {hwnd: window for hwnd, window in dct.items() if window.width > 480 and window.height > 800}

        return dct
