"""
base.py

Encapsulate initial functionality used by tests... Mostly just instantiating the Bot here so that we
can properly test functions within.
"""
from django.test import TestCase

from titandash.models.bot import BotInstance
from titandash.models.configuration import Configuration
from titandash.bot.core.bot import Bot
from titandash.bot.core.window import Window
from titandash.bot.core.maps import IMAGES as BOT_IMAGES
from titandash.tests.bot.maps import IMAGES as TEST_IMAGES

from PIL import Image

import logging


class BaseBotTest(TestCase):
    """BaseBotTest sets up initial data to ensure a 'bot' object is available and generated."""
    @classmethod
    def setUpTestData(cls):
        super(BaseBotTest, cls).setUpTestData()

        # Grabbing a simple logger that will be used during tests
        # when the Bot instance performs and functions.
        cls.logger = logging.getLogger(__name__)

        # Configuration is handled by our migration signals...
        # A DEFAULT Configuration is generated that may be used here.
        cls.config = Configuration.objects.get(name="DEFAULT")
        cls.window = Window(hwnd=1, text="Test Emulator", rectangle=(0, 0, 480, 800))
        cls.bot = Bot(
            configuration=cls.config,
            window=cls.window,
            enable_shortcuts=False,
            instance=BotInstance.objects.grab(),
            logger=cls.logger,
            debug=True
        )

        # All required/needed Bot/Test Images are built here.
        cls.BOT_IMAGES = BOT_IMAGES
        cls.TEST_IMAGES = TEST_IMAGES

    def tearDown(self):
        """Perform small teardown to ensure BotInstance data is gracefully terminated."""
        super(BaseBotTest, self).tearDown()

        # Gracefully stop and exit the BaseBotTest BotInstance.
        self.bot.instance.stop()

    def _visible(self, game_image, find_image, reverse=False):
        """Generic visibility function. Reverse will assert false."""
        # Set current Bot (game) image to the specified image.
        self.bot.grabber.current = Image.open(game_image)

        # Calculate specified assertion to determine image present/not present.
        assertion = self.assertFalse if reverse else self.assertTrue
        assertion(self.bot.grabber.search(
            image=find_image,
            bool_only=True,
            testing=True
        ))

    def is_image_visible(self, game_image, find_image):
        """Encapsulate functionality to determine if an image can be found within another image."""
        self._visible(game_image=game_image, find_image=find_image, reverse=False)

    def is_image_not_visible(self, game_image, find_image):
        """Encapsulate functionality to determine if an image is not found within another image."""
        self._visible(game_image=game_image, find_image=find_image, reverse=True)
