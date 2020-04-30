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

        # Screen is updated and set to the result of an image
        # grab as needed through the snapshot method.
        self.current = None

    def snapshot(self, region=None, downsize=None):
        """
        Take a snapshot of the current game session, based on the width and height of the grabber unless
        an explicit region is specified to use to take a screen-shot with.
        """
        if not region:
            self.current = self.window.screenshot()
        else:
            self.current = self.window.screenshot(region=region)

        # Optionally, we can downsize the image grabbed, may improve performance
        # if we are grabbing or parsing many images and want them to be smaller sizes.
        if downsize:
            self.current.thumbnail((
                self.current.width / downsize,
                self.current.height / downsize
            ))

        return self.current

    def search(self, image, region=None, precision=0.8, bool_only=False, testing=False, im=None, return_image=False):
        """
        Search the specified image for another image with a specified amount of precision.

        Specifying bool_only as True will only return whether or not the image is found.

        The testing boolean is used to aid the unit tests to use mock images as a snapshot instead
        of the actual screen.
        """
        if not testing:
            self.snapshot()

        found = False
        position = -1, -1

        search_kwargs = {
            "x1": region[0] if region else self.window.x,
            "y1": region[1] if region else self.window.y,
            "x2": region[2] if region else self.window.width,
            "y2": region[3] if region else self.window.height,
            "precision": precision,
            "im": im if region else self.current if not im else im,
            "logger": self.logger
        }

        # If a list of images to be searched for is being used, loop through and search.
        # The first image specified that is found breaks the loop.
        if isinstance(image, list):
            for _image in image:
                position = imagesearcharea(window=self.window, image=_image, **search_kwargs)
                if position[0] != -1:
                    image = _image  # Set inline var to main for logging purposes.
                    break
        else:
            position = imagesearcharea(window=self.window, image=image, **search_kwargs)

        if position[0] != -1:
            self.logger.debug("{image_name} was successfully found on the screen...".format(image_name=image.split("/")[-1]))
            found = True
        if bool_only:
            return found

        # Modify the position to reflect the current window location.
        if position[0] != -1:
            position = (position[0], position[1])

        # Include the image that was found if specified to do so.
        # May prove useful when searching for a list of images.
        if return_image:
            return found, position, image

        return found, position

    def point_is_color(self, point, color=None, color_range=None):
        """
        Given a specified point, determine if that point is currently a specific color.
        """
        if color and color_range:
            raise ValueError("Only one of color or color_range may be present, but not both.")

        self.snapshot()

        pt = self.current.getpixel(point)

        # No padding or modification is required for our color check.
        # Since we are using the snapshot functionality, which takes into
        # account our emulator position and title bar height. The point being used
        # is in relation to the "current" image which already is padded properly.
        if color:
            return pt == color

        # Checking for a color range allows for a bit of irregularity in the colors present
        # at a certain location, this is mostly done to check for very different colors,
        # for example, when perks are active, they are greyed out, and blue when available.
        if color_range:
            return color_range[0][0] <= pt[0] <= color_range[0][1] and color_range[1][0] <= pt[1] <= color_range[1][1] and color_range[2][0] <= pt[2] <= color_range[2][1]
