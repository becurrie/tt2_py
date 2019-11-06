"""
grabber.py

Encapsulate the functional class used by the bot to take screenshots of the game screen and search
for specific images present on the screen.
"""
from titandash.bot.external.imagesearch import *


class Grabber:
    """
    Grabber class provides functionality to capture a portion of the screen, based on the height
    and width that the emulator should be set to.
    """
    def __init__(self, window, logger):
        # Base height and width, resolution of game.
        self.window = window
        self.logger = logger

        # Padding provided by emulator, x1, y1.
        self.x = window.x
        self.y = window.y + window.y_padding
        self.width = window.width
        self.height = window.height - window.y_padding

        # x2, y2, represent the width and height of the emulator.
        self.x2 = self.width + self.x
        self.y2 = self.height + self.y

        # Screen is updated and set to the result of an image grab as needed through the snapshot method.
        self.current = None

    def snapshot(self, region=None, downsize=None):
        """
        Take a snapshot of the current game session, based on the width and height of the grabber unless
        an explicit region is specified to use to take a screen-shot with.
        """
        if not region:
            self.logger.debug("taking snapshot of game screen (X1: {x}, Y1: {x}, X2: {x2}, Y2: {y2})".format(
                x=self.x, y=self.y, x2=self.x2, y2=self.y2))
            self.current = region_grabber((self.x, self.y, self.x2, self.y2))
        else:
            self.logger.debug("taking snapshot of region in game screen (X1: {x}, Y1: {y}, X2: {x2}, Y2: {y2}".format(
                x=region[0], y=region[1], x2=region[2], y2=region[3]))

            padded = self.window.y + self.window.y_padding
            region = (
                region[0] + self.window.x, region[1] + padded,
                region[2] + self.window.x, region[3] + padded
            )
            self.current = region_grabber(region)

            if downsize:
                self.current.thumbnail((
                    self.current.width / downsize,
                    self.current.height / downsize
                ))

    def search(self, image, region=None, precision=0.8, bool_only=False, testing=False, im=None):
        """
        Search the specified image for another image with a specified amount of precision.

        Specifying bool_only as True will only return whether or not the image is found.

        The testing boolean is used to aid the unit tests to use mock images as a snapshot instead
        of the actual screen.
        """
        if not testing:
            self.logger.debug("searching for {image} in game and returning {bool_or_both}".format(
                image=image, bool_or_both="bool only" if bool_only else "bool and position"))
            self.snapshot()

        found = False
        position = -1, -1
        padded = self.window.y + self.window.y_padding
        try:
            if region:
                region = (
                    region[0] + self.window.x, region[1] + padded,
                    region[2] + self.window.x, region[3] + padded
                )

                search_kwargs = {
                    "x1": region[0],
                    "y1": region[1],
                    "x2": region[2],
                    "y2": region[3],
                    "precision": precision,
                    "im": im
                }
            else:
                search_kwargs = {
                    "x1": self.x,
                    "y1": self.y,
                    "x2": self.x2,
                    "y2": self.y2,
                    "precision": precision,
                    "im": self.current if not im else im
                }

            # If a list of images to be searched for is being used, loop through and search.
            # The first image specified that is found breaks the loop.
            if isinstance(image, list):
                for _image in image:
                    position = imagesearcharea(image=_image, **search_kwargs)
                    if position[0] != -1:
                        break
            else:
                position = imagesearcharea(image=image, **search_kwargs)

        # Catch any errors relating the cv2 functionality. Most commonly appears if the
        # file could not be found. But additional errors could crop up.
        except cv2.error:
            self.logger.error("error occurred during image search, does the file: {file} exist?".format(file=image), exc_info=True)
            raise

        if position[0] != -1:
            found = True
        if bool_only:
            return found

        # Modify the position to reflect the current window location.
        if position[0] != -1:
            position = (position[0] + self.window.x, position[1] + padded)

        return found, position

    def point_is_color(self, point, color):
        """
        Given a specified point, determine if that point is currently a specific color.
        """
        self.snapshot()

        # No padding or modification is required for our color check.
        # Since we are using the snapshot functionality, which takes into
        # account our emulator position and title bar height. The point being used
        # is in relation to the "current" image which already is padded properly.
        return self.current.getpixel(point) == color
