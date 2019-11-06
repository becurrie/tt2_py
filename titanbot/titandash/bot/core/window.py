from .constants import (
    MEMU_WINDOW_FILTER, NOX_WINDOW_FILTER
)

from pyautogui import _failSafeCheck

import win32gui
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

    def __init__(self, hwnd, text, rectangle):
        self.hwnd = hwnd
        self.text = text
        self.x = rectangle[0]
        self.y = rectangle[1]
        self.width = rectangle[2] - self.x
        self.height = rectangle[3] - self.y

        # Depending on the type of emulator being used (and support), some
        # differences in the way their window object is defined.
        # Nox: X Axis is not included in window rectangle.
        # MEmu: X Axis is included.
        # Based on these differences, we should modify appropriately
        # the width and height values before calculating padding.
        if self.text.lower() in MEMU_WINDOW_FILTER:
            self.width -= 38

        # Additionally, based on the size of the emulator, we want
        # to ensure we can pad the x, y value so the title bar is taken
        # into account when things are clicked or searched for...
        # We expect the emulator size to be 480x800, so we can get
        # the padding from this value.
        self.x_padding = self.width - 480
        self.y_padding = self.height - 800

    def __str__(self):
        return "{text} ({x}, {y}, {w}, {h})".format(
            text=self.text, x=self.x, y=self.y, w=self.width, h=self.height)

    def __repr__(self):
        return "<Window: {window}>".format(window=self)

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

    def click(self, point, clicks=1, interval=0.0, button="left", pause=0.0, disable_padding=False):
        """
        Perform a click on the given window in the background.

        Sending a message to the specified window so the click takes place
        whether the window is visible or not.
        """
        _failSafeCheck()
        evt_d = self.SUPPORTED_CLICK_EVENTS[button][0]
        evt_u = self.SUPPORTED_CLICK_EVENTS[button][1]

        # Padding should be disabled in the cases where our point is derived
        # through an image search, which returns a relative coord that
        # does not need any modification.
        if disable_padding:
            param = win32api.MAKELONG(
                point[0],
                point[1]
            )
        else:
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

        window = Window(
            hwnd=hwnd,
            text=win32gui.GetWindowText(hwnd),
            rectangle=win32gui.GetWindowRect(hwnd))

        self.windows[hwnd] = window

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
