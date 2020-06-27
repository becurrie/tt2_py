<p align="center">
  <img height="226px" width="151px" src="https://github.com/becurrie/titandash/blob/master/img/flame.png"/>
</p>
<h1 align="center">Titandash</h1>
<h3 align="center">TapTitans 2 Bot/Progression Application</h3>
<p align="center">
  <img src="https://badge.fury.io/gh/becurrie%2Ftitandash.svg">
  <a href="https://titandash.net"><img src="https://img.shields.io/badge/site-titanda.sh-lightgrey"></a>
  <a href="https://github.com/becurrie/titandash/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/becurrie/titandash"></a>
</p>

## Getting Started
Take a look at the [wiki](https://github.com/becurrie/titandash/wiki) for information about setting up and configuring the dependencies and requirements needed to start the dashboard and initiate a new bot instance.

You can also visit our homepage, [here](https://titandash.net) for more information!

## Features
### Bot
- Perform all functionality in the background, so you can do other things while the bot is running.
- Activate chosen in game skills on a specified cooldown, with the option to wait for a specific skill before activating others.
- Use/purchase chosen in game perks on a specified cooldown, or only when a tournament is joined.
- Equip headgear based on your current highest levelled hero (melee, spell, ranged).
- Use/purchase a specific in game perk whenever you prestige.
- Activate specific functions using keyboard shortcuts.
- Automatically tap on the screen, activating and collecting fairies.
- Automatically tap skill minigames on the screen (coordinated offensive, astral awakening, etc), activating and collecting fairies if they're triggered.
- Automatically level up the sword master, skills and heroes in game with specific intervals for the activation of each.
- Automatically level up skills to a specified level cap.
- Automatically prestige after a threshold has been reached (stage, percent of max stage, max stage, time limit).
- Automatically add random padding to prestige times to ensure they look less robotic.
- Automatically take breaks in game after random intervals of game time.
- Receive text notifications when your raid attacks timer has reset and the titan can be attacked.
- Upgrade or ignore specific artifacts or tiers after a prestige.
- Participate in tournaments when they are available (enter/collect rewards).
- Parse tournaments before collecting rewards to keep track of your placements and rewards earned.
- Hatch and collect any eggs when they become available.
- Collect in game ads if VIP is unlocked in game.
- Collect daily achievements when they are completed.
- Collect milestones in game when they are completed.
- Collect daily rewards when they are available.
- Update and use newest configuration variables in real time as you modify for your configurations.

### Bootstrapper
- Perform automatic updates as they are released directly from this page within the web application.
- Automate the following processes through the bootstrapper:
  - Updating titandash to the newest version.
  - Install python requirements taken from the `requirements.txt` file.
  - Install all node packages from the `package.json` file.
  - Perform the database caching command to ensure it's setup properly.
  - Collect static files into the static directory.
  - Perform dependency checks (`tesseract`, `redis`, `node`).
- Display helpful error messages when any of the above processes fail.

### Dashboard
- Main dashboard screen providing real-time updates and the ability to start, pause or stop the bot and view information about the current session.
- Choose a specific window (emulator) to target when initializing a bot.
- Generate multiple instances of a bot and start bots for multiple emulator sessions.
- View a real time view of the current in game screen.
- View all log records associated with the current bot session and filter on specific log levels.
- Countdowns until specific functionality takes place.
- View all sessions that have taken place and review logs/duration/prestiges that happened while a session was active.
- Create multiple configurations that can be swapped out quickly when needed (farming, tournaments, push).
- Import/export your configurations in a small, shareable string with other users.
- View and edit globally available settings that are used by every bot session.
- Review all current statistics taken from the game, as well as statistics related to the bot.
- View all prestiges and review additional information (average stage, average duration).
- View all artifact statistics and whether or not you currently own each one. (Toggle owned status).
- Choose different themes for the dashboard (including dark theme).

### System Tray
- Open Dashboard.
- Open Bootstrapper.
- Open Github Repository.
- Generate Debug Report.
- Exit Application.

### Quickstart
- Ensure you've installed and configured dependencies present in the [wiki](https://github.com/becurrie/titandash/wiki/Dependencies).
- Run the `setup.bat` file to setup your virtual environment, python requirements, database migrations and static files.
- Run `titandash.bat` to start the server and application.

## Requirements
- Windows 10
- [Python 3.7](https://www.python.org/downloads/release/python-370/)
- [Node/NPM](https://nodejs.org/en/)
- [MEmu Emulator 7.0.1](https://drive.google.com/open?id=19WVZleJjRAcoKK4s-2pSnhiv8pKO_t1g) or [Nox Emulator](https://www.bignox.com/en/download/fullPackage)

## Development
Thanks for taking the time to check out this project. If you have any suggestions, 
you can create a new issue about it or create a pull request with your changes!

## Discord
You can also join our discord channel, [here](https://discord.gg/XJqfVEx) to stay up to date with all the newest features being worked on and make
feature requests here if you want.
