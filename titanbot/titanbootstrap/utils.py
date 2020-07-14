from django.conf import settings

from titanauth.models.user_reference import ExternalAuthReference

from pathlib import Path

import subprocess
import requests
import zipfile
import logging
import time
import io
import os
import shutil

logger = logging.getLogger(__name__)


def launch_process(command, shell=True, sleep=None):
    """
    Helper utility to launch a new subprocess for the specified command.
    """
    subprocess.Popen('"%s"' % command, shell=shell)

    if sleep:
        time.sleep(sleep)


def purge_dir(path):
    """
    Purge the specified directory path to remove all files and links recursively.
    """
    for p in Path(path).glob("**/*"):
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)


def copy_tree(src, dest, symlinks=False, ignore=None, remove_src=False):
    """
    Copy the specified source directory over to the specified destination directory.
    """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)

        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

    if remove_src:
        shutil.rmtree(src)


class VersionChecker(object):
    """
    Create an encapsulated object that may be used to check versions of titandash and perform required steps to update.
    """
    def __init__(self):
        self._VERSION_ERROR = "VERSION_ERROR"
        self._VERSION_GOOD = "UP_TO_DATE"
        self._VERSION_BAD = "UPDATE_AVAILABLE"

        self.check_url = "https://titanauth.herokuapp.com/api/version"
        self.download_url = "https://titanauth.herokuapp.com/api/download_url"
        self.current = settings.BOT_VERSION
        self.newest = self.newest_version()

    def _check(self):
        """
        Perform check of current and newest versions, returning one of three possible flags present above.
        """
        # Either the newest/current version are missing or not set to
        # a truthy type value. Return a simple status string to define that.
        if not self.newest or not self.current:
            return self._VERSION_ERROR
        # The current version is up to date with the newest version.
        if self.current == self.newest:
            return self._VERSION_GOOD

        # Otherwise, the version must be out of date.
        # Return status string allowing for update.
        return self._VERSION_BAD

    def perform_check(self):
        """
        Perform the actual version check here. Beginning functionality to update the bot if possible.
        """
        return self._check()

    def newest_version(self):
        """
        Attempt to send a request to the titanauth front facing website to determine the newest version.
        """
        try:
            response = requests.get(url=self.check_url).json()

        # Catch all on any exception to ensure the newest version is set to None.
        except Exception:
            logger.error("Error occurred while grabbing newest version from authentication backend.", exc_info=True)

            # Return None as a substitute for being unable to grab
            # the most latest version over the web.
            return None

        return response.get("version", None)

    def download_newest(self):
        """
        Retrieve the latest release download url and download the file directly from our github archive.
        """
        # Remove any data present in the update directory before downloading
        # any new files.
        purge_dir(path=settings.LOCAL_DATA_UPDATE_DIR)

        try:
            response = requests.get(url=self.download_url).json()

        # Catch all on any exception and re raise after log. We can catch in calling function
        # to ensure we have the cause of the exception.
        except Exception:
            logger.error("Error occurred while grabbing newest version download url from authentication backend.", exc_info=True)
            raise

        url = response.get("url", None)

        try:
            # Download and extract the newest versions zip archive
            # into our local data directory temporarily.
            req = requests.get(url=url)
            file = zipfile.ZipFile(file=io.BytesIO(req.content))

            file.extractall(path=settings.LOCAL_DATA_UPDATE_DIR)

            # Get some information about the extracted data. Grabbing the first file available
            # and getting the filename, which is really the directory it's within.
            source = os.path.join(settings.LOCAL_DATA_UPDATE_DIR, file.filelist[0].filename)

            copy_tree(
                src=source,
                dest=settings.LOCAL_DATA_UPDATE_DIR,
                remove_src=True
            )

            # Retuning the directory containing the newly extracted information, as well as the
            # result from the file extract function.
            return settings.LOCAL_DATA_UPDATE_DIR

        # Catch all on any exception here as well and re raise.
        except Exception:
            logger.error("Error occurred while downloading and extracting newest version package.", exc_info=True)
            raise


class DependencyChecker(object):
    """
    Create an encapsulated object that may be used to check titandash dependencies and download them if needed.
    """
    def __init__(self):
        self.tesseract_url = 'https://titanauth.herokuapp.com/dependencies/tesseract'
        self.redis_url = 'https://titanauth.herokuapp.com/dependencies/redis'

    @staticmethod
    def _credentials():
        """
        Return a dictionary with the current external auth reference email and token.
        """
        reference = ExternalAuthReference.objects.first()

        return {
            'email': reference.email,
            'token': reference.token
        }

    def retrieve_tesseract(self):
        """
        Attempt to grab and download the tesseract dependency zip file from the external backend.
        """
        return requests.post(
            url=self.tesseract_url,
            data=self._credentials()
        )

    def retrieve_redis(self):
        """
        Attempt to grab and download the redis dependency zip file from the external backend.
        """
        return requests.post(
            url=self.redis_url,
            data=self._credentials()
        )
