from .constants import MEMU_WINDOW_FILTER
from .utilities import globals

from PIL import Image
from threading import Lock
from ctypes import windll

import win32gui
import win32ui
import win32api
import win32con

import time

# Making use of a screenshot lock, instantiated at the module level of our window.py file.
# We do this so that any additional bot instances that are started, always use this lock.
# Only a SINGLE screenshot should be taken at any given time, otherwise we run into issues
# with our DC retrieval (GetCompatibleDC) and DC deletion.
_SCREENSHOT_LOCK = Lock()
_CLICK_LOCK = Lock()
_DRAG_LOCK = Lock()


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
        return win32gui.GetWindowRect(self.hwnd)

    @property
    def x(self):
        return self.rect[0]

    @property
    def y(self):
        return self.rect[1]

    @property
    def width(self):
        return self.rect[2] - self.x

    @property
    def height(self):
        return self.rect[3] - self.y

    @property
    def y_padding(self):
        return self.height - self.EMULATOR_HEIGHT

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
        with _CLICK_LOCK:
            globals.failsafe()
            evt_d = self.SUPPORTED_CLICK_EVENTS[button][0]
            evt_u = self.SUPPORTED_CLICK_EVENTS[button][1]

            param = win32api.MAKELONG(
                point[0],
                point[1] + self.y_padding
            )

            # Loop through all clicks that should take place.
            for x in range(clicks):
                globals.failsafe()
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
        with _DRAG_LOCK:
            globals.failsafe()
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
        Takes a screenshot of the current window.

        A region can be provided to also only pick out a certain bounding box of image
        data from the final image.
        """
        # Ensure only one screenshot is ever being taken at a single
        # time. We may run into windows api issues if this isn't done.
        with _SCREENSHOT_LOCK:
            # Retrieve the required handles and DC objects
            # through the windows API.
            hwnd_dc = win32gui.GetWindowDC(self.hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, self.width, self.height)
            save_dc.SelectObject(save_bitmap)

            # Perform the actual printing functionality to retrieve
            # the content within our specified hwnd.
            windll.user32.PrintWindow(self.hwnd, save_dc.GetSafeHdc(), 0)

            bmp_info = save_bitmap.GetInfo()
            bmp_str = save_bitmap.GetBitmapBits(True)

            # Create the actual image object from our bitmap buffer
            # generated above.
            image = Image.frombuffer(
                "RGB",
                (bmp_info["bmWidth"], bmp_info["bmHeight"]),
                bmp_str,
                "raw",
                "BGRX",
                0,
                1
            )

            # Cleanup windows api objects for use in repeated
            # screenshots and functionality.
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwnd_dc)
            win32gui.DeleteObject(save_bitmap.GetHandle())

            # Before our actual region cropping takes place, we also want to
            # make sure that the window itself is already cropped to only be displaying
            # the proper emulator content.
            image = image.crop(
                box=(
                    0,
                    self.y_padding,
                    self.EMULATOR_WIDTH,
                    self.EMULATOR_HEIGHT + self.y_padding
                )
            )

            # If a region is present, we can ensure our image is cropped to the
            # bounding box specified. The region should already take into account
            # our expected y padding (ie: (110, 440) -> (110, 410). Give or take a couple of pixels.
            if region:
                image = image.crop(
                    box=region
                )

            return image

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
        self.filter_lst = MEMU_WINDOW_FILTER
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

    def filter(self, filter_titles=True, ignore_hidden=True, ignore_smaller=(400, 720)):
        """
        Filter the currently available windows to ones that contain the specified text.

        Titles: (ie: Windows that contain the hard coded title filters).
        Hidden (ie: 0x0 sized windows are ignored by default).
        Smaller: (ie: Windows smaller than the specified amount).
        """
        if filter_titles:
            dct = {hwnd: window for hwnd, window in self.windows.items() if window.find(self.filter_lst)}
        else:
            dct = self.windows

        if ignore_hidden:
            dct = {hwnd: window for hwnd, window in dct.items() if window.width != 0 and window.height != 0}
        if ignore_smaller:
            dct = {hwnd: window for hwnd, window in dct.items() if window.width > ignore_smaller[0] and window.height > ignore_smaller[1]}

        return dct
