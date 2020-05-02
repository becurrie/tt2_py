from django.conf import settings
from django.core.management import call_command

import PySimpleGUI as sg
import PySimpleGUIWx as sgw

import django
import ctypes
import webbrowser
import logging
import subprocess
import os
import sys


# Setting the django settings module in our environment so settings can be
# imported properly and used throughout the application.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "titanbot.settings")

# Get current working directory list.
cwd = os.getcwd().split("\\")

# Update path with appropriate values so that modules
# and associated imports are handled correctly during execution.
if cwd not in sys.path:
    sys.path.append("\\".join(cwd))
if cwd[:-1] not in sys.path:
    sys.path.append("\\".join(cwd[:-1]))

# Finally, ensure django has been "setup" to allow loading of apps and modules where needed.
django.setup()

logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s",
        datefmt="%m-%d %H:%M",
        filename=settings.LOCAL_DATA_LOG_FILE,
        filemode="w"
)

console_formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s")
console = logging.StreamHandler()

console.setFormatter(console_formatter)
console.setLevel(logging.INFO)

logging.getLogger("").addHandler(console)


class TitandashApplication(object):
    """
    Titandash Application Container.

    Encapsulating all functionality used to generate and open the titandash web application within a gui window.
    """
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    def __init__(self):
        """
        Initialize the core titandash application object.

        Setting up some basic variables and data used throughout app boot.
        """
        self.title = "Titandash %s" % settings.BOT_VERSION
        self.version = settings.BOT_VERSION

        # Images...
        self.logo = "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"

        # Flags...
        self.quiet = "--quiet"

        logging.info("=============================================================")
        logging.info("{title} Application Initialized...".format(title=self.title))
        logging.info("=============================================================")
        logging.info("STARTING APPLICATION NOW...")

    def inhibit(self):
        """
        Setup windows sleep inhibitor.

        While titandash is running, we do not want the windows machine to goto sleep... This will cause our
        bot instances to fail and would not allow for our bots run continuously over time.

        See: http://trialstravails.blogspot.com/2017/03/preventing-windows-os-from-sleeping.html
        """
        logging.debug("PREVENTING WINDOWS FROM GOING TO SLEEP...")
        ctypes.windll.kernel32.SetThreadExecutionState(
            self.ES_CONTINUOUS | self.ES_SYSTEM_REQUIRED)

    def uninhibit(self):
        """
        Setup windows sleep uninhibitor.

        When titandash is finished running, we should allow the os to goto sleep if needed.
        """
        logging.debug("ALLOWING WINDOWS TO GOTO SLEEP...")
        ctypes.windll.kernel32.SetThreadExecutionState(
            self.ES_CONTINUOUS)

    def loading(self):
        logging.debug("OPENING SPLASH.")
        sg.PopupAnimated(image_source=self.logo, background_color="white", transparent_color="white")

    @staticmethod
    def finalize():
        logging.debug("CLOSING SPLASH.")
        sg.PopupAnimated(None)

    @staticmethod
    def procs():
        """
        Retrieve the current procs related to the titandash web application.

        RUNNING: The server is running and currently up.
        DEAD: The server is currently not running at all.
        """
        try:
            netstat = subprocess.Popen(
                args=["netstat", "-a", "-n", "-o"],
                stdout=subprocess.PIPE,
                universal_newlines=True
            )
            netstat = subprocess.check_output(
                args=["findstr", ":%d" % settings.TITANDASH_PORT],
                stdin=netstat.stdout,
                universal_newlines=True
            )

        # If no output is returned from the server subprocess command,
        # it is safe to assume that the server is currently terminated.
        except subprocess.CalledProcessError:
            return []

        output = netstat.replace("\r", "").split("\n")

        # Parse output into readable list of processes.
        netstat = []
        for line in output:
            line = line.split(" ")
            line = [e for e in line if e != ""]
            line = [l.replace(" ", "") for l in line]

            try:
                if ":%d" % settings.TITANDASH_PORT in line[1] and len(line) == 5:
                    # [0] - Protocol
                    # [1] - Local Address
                    # [2] - Foreign Address
                    # [3] - State
                    # [4] - PID
                    netstat.append({
                        "protocol": line[0],
                        "local": line[1],
                        "foreign": line[2],
                        "state": line[3],
                        "pid": line[4]
                    })

            # IndexError may occur when some sort of trailing output is present
            # in the available lines and the check can not be done.
            except IndexError:
                continue

        if netstat:
            logging.debug("PROCS: {output}".format(output=netstat))
            return netstat

        # Netstat worked correctly, but no processes are present
        # that are listening on the titandash port...
        return []

    def stop_server(self):
        """
        Stop the titandash web application server.
        """
        try:
            processes = self.procs()

            # Sometimes, the output of our processes command may return
            # a pid of 0. This can not be killed by our subprocess. Returning true.
            if not processes:
                return True

            # If the server is currently running, we want to begin an indefinite loop that sends a task to kill
            # the server and only once no more processes are running, do we exit gracefully from the loop.
            logging.debug("ATTEMPTING TO KILL SERVER...")

            if processes[0]["pid"] == 0:
                return True

            # Kill server with kill command in subprocess...
            # If this does not, we'll just forget it. It's likely that this fails
            # because the server is in a weird state, we can fire and forget.
            subprocess.run(args=["taskkill", "/F", "/PID", processes[0]["pid"]])

            # Return true once we can safely assume the server is not running...
            return True

        # If the command can not be called for some reason, just exit early.
        except subprocess.CalledProcessError:
            return True

    def start_server(self):
        """
        Start the titandash web application server.

        If the server is already running, we can safely return without executing any commands.
        """
        if len(self.procs()) > 1:
            logging.debug("A Titandash server is already running... Assuming the server is already accessible.")
            return True

        # Execute an sub process to begin our web server process.
        # We use a subprocess command so that our application is not blocked
        # while the application is running.
        logging.debug("Starting Titandash Web Server Now...")
        subprocess.Popen(["python", "manage.py", "runserver", str(settings.TITANDASH_PORT), "--noreload"])

        # Wait while the server is starting... Just to ensure no multiple of the command are sent out.
        # This may cause weird issues with the web server.
        while len(self.procs()) == 0:
            logging.debug("WAITING FOR ACCESSIBLE SERVER...")
            continue

    def system_tray(self):
        """
        Build the system trap application and start the main event loop.

        Our event loop will allow a user to click on the icon to open a browser to the web application.
        """
        menu = [
            self.title,
            [
                self.title,
                "---",
                "Open Dashboard",
                "Open Github",
                "---",
                "Bootstrap",
                "---",
                "Generate Debug Report",
                "Exit"
            ]
        ]

        tray = sgw.SystemTray(
            menu=menu,
            tooltip=self.title,
            data_base64=self.logo
        )

        logging.debug("Beginning System Tray Event Loop...")
        # Begin the event loop for reading and waiting
        # for interaction between the system tray application.
        while True:
            event = tray.Read()

            # Check different cases for the event picked based on the
            # attributes specified in the menu.

            # Exit the application. We are also tearing down the server
            # before completing the event loop.
            if event == "Exit":
                tray.ShowMessage(title="Exiting", message="Exiting Application Now")
                self.uninhibit()
                self.stop_server()

                # Break to terminate event loop and stop python process.
                break

            # Open up the application in a new browser tab.
            # This is the main function of the tray application.
            if event in ["Open Dashboard", self.title, "__ACTIVATED__"]:
                webbrowser.open_new_tab(url=settings.TITANDASH_DASHBOARD_URL)

            if event == "Open Github":
                webbrowser.open_new_tab(url="https://github.com/becurrie/titandash")

            # Open up the application in a bootstrapping state.
            # Acts as a shortcut to open the page up if not starting
            # the program for the first time.
            if event in "Bootstrap":
                webbrowser.open_new_tab(url=settings.TITANDASH_LOADER_URL)

            # Generate a debug report based on the most current information.
            # Opening the directory once finished.
            if event == "Generate Debug Report":
                call_command("debug_report")


if __name__ == "__main__":
    # Create initial titandash application instance...
    app = TitandashApplication()
    args = sys.argv

    try:
        # Application is beginning initialize process.
        app.loading()
        app.stop_server()
        app.start_server()
        app.inhibit()

        # Web application is now accessible. Let's begin the window creation process.
        # We always open the bootstrapper on the initial start of our app.
        # --------------------------------------------------------------------------
        app.finalize()

        if app.quiet not in args:
            # Opening the application normally".
            # The quiet flag can be applied to skip this functionality.
            # Preventing a new tab being opened on startup.
            logging.debug("Opening Web Application...")
            webbrowser.open_new_tab(url=settings.TITANDASH_LOADER_URL)
        else:
            logging.debug("Opening Application Quietly...")

        app.system_tray()
        # We are now blocking forever on our main thread until the user closes the application...
        # All of our functionality should now just be handled by our web server...
        # ...
        # ...

    # Catch exceptions broadly and ensure we log information
    # to our logging setup.
    except Exception as exc:
        logging.error(exc, exc_info=True)

    # Use finally block to ensure the server is stopped before ending our application.
    finally:
        app.uninhibit()
        app.stop_server()
