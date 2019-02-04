# TapTitans2 Py
Tap Titans 2 Progression Bot/Tools

TapTitans2 Py is bot written in python that enables the mobile tap game Tap Titans 2 to play and progress all on its own.

---

**Table of Contents**
- [TapTitans2 Py](#taptitans2-py)
- [Current Features](#current-features)
  - [Tools](#tools)
    - [Artifact Parsing](#artifact-parsing)
- [Requirements](#requirements)
- [Setting Up / Running Bot](#setting-up-running-bot)
  - [Exiting/Terminating Bot](#exitingterminating-bot)
- [Configuration](#configuration)
    - [Runtime Options](#runtime-options)
    - [Device Options](#device-options)
    - [Generic Options](#generic-options)
    - [General Action Options](#general-action-options)
    - [Clan Quest Action Options](#clan-quest-action-options)
    - [Master Action Options](#master-action-options)
    - [Heroes Action Options](#heroes-action-options)
    - [Skills Action Options](#skills-action-options)
    - [Prestige Action Options](#prestige-action-options)
    - [Artifacts Action Options](#artifacts-action-options)
    - [Stats Options](#stats-options)
    - [Artifact Parsing Options](#artifact-parsing-options)
    - [Logging Options](#logging-options)
- [Development](#development)

# Current Features
- Fully configurable settings to gear the bot's functionality to match your playstyle/build.
- Activate chosen in game skills on a specified cooldown, with the option to wait for one specific skill before activating others.
- Automatically level up the sword master, skills and heroes in game with a specified amount of intensity (clicks).
- Automatically prestige after a specified amount of minutes spent in a run.
- Upgrade your bos artifact after a prestige has been completed.
- Participate in tournaments when they become available (enter/collect rewards).
- Hatch and collect any eggs when they become available.
- Participate in clan battles with the option to enable an additional fight after the first one (diamonds).
- Store all game/bot/session statistics in a single location to provide some insight into progress made.
- Console/file logging capabilities to provide debugging and bug tracking.

## Tools
Some tools are provided with the bot, these give some added external functionality that isn't included or initiated at any point during a main bot game loop, either because they take too long, or make more sense as a callable tool rather than part of the bot.

### Artifact Parsing
Parse all of your artifacts in game, categorizing artifacts in their particular tier (S, A, B, C), and whether or not you currently own an artifact, a count of discovered artifacts is also available.

# Requirements
- Windows Operating System
- [Python 3.7](https://www.python.org/downloads/release/python-370/)
- [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract)
- Android Emulator (Currently Supported: [Nox](https://www.bignox.com/))

# Setting Up / Running Bot
Before you can run the bot, you'll need to ensure that a couple of steps have been taken before things will work properly.

1. Install all requirements into your Python (It may be worth setting up a virtual environment to do this if you use Python to develop, otherwise, just install everything into your system Python).
`pip install -r requirements.txt`

2. Create a copy of the `config_example.ini` in the same directory and name it `config.ini`. This is the file you will use to specify all of your playstyle/build specific settings.

You can find more information below on the configuration settings and what some of the expected or recommended values are, for now, we can just focus on getting the bot running.

3. Open a command prompt and change your directory to the `core` module. Try running the bot with the following command:
`python run.py -start`

From here, the bot should begin running. Your command prompt will log information about what is currently happening. Note that while the bot is running, you will not be able to use the computer for anything else, it may be worth setting this up within a virtual machine, or using it to farm for you when you are away from the computer.

4. Maybe you want to run one of the included tools instead of running the bot directly. You can do that easily as well by running the following commands:
 - Artifact Parsing: `python run.py -parse_artifacts`

## Exiting/Terminating Bot
To terminate the bot, you will need to drag your mouse up to the top-left most portion (0, 0) of you desktop. When that point is successfully reached, you will be presented with the following log message:
```[2019-02-04 11:42:47,245] INFO [bot.py:762 - run() ] bot is shutting down now, please press the space key to perform a soft shutdown in 5 second(s).```

You may decide to initiate a soft shutdown at this point by clicking the button (space by default) specified in your configuration file.

Otherwise, don't click anything and the bot will successfully terminate after the specified time given (5 by default) to wait for a soft shutdown signal.

# Configuration
The configuration values all have some comments that describe the option slightly, that some additional information will be provided here for each config option.

### Runtime Options
| Config | Description | Default | Examples |
|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|---------------------|
| SOFT_SHUTDOWN_KEY | Key used when the bot has a shutdown initiated to go from a hard shutdown, to a soft shutdown. A soft shutdown will initiate some cleanup/additional features before fully exiting. | space | space, esc, ctrl, q |
| SHUTDOWN_SECONDS | How long the bot will wait for the soft shutdown key signal before terminating. | 5 | 5, 10, 20 |
| SOFT_SHUTDOWN_CRITICAL_ERROR | Should a soft shutdown be automatically initiated if a critical error is encountered. | on | on, off |
| UPDATE_STATS_ON_SOFT_SHUTDOWN | Perform a statistics update when a soft shutdown is initiated. | on | on, off |

### Device Options
| config | Description | Default | Examples |
|----------|--------------------------------------------------|---------|----------|
| WIDTH | Specify the width of the game screen. | 480 | 480 |
| HEIGHT | Specify the height of the game screen. | 800 | 800 |
| EMULATOR | Specify the emulator service that is being used. | nox | nox |

### Generic Options
| config | Description | Default | Examples |
|---------------------------|----------------------------------------------------------------------------------------------|---------|----------|
| ENABLE_PREMIUM_AD_COLLECT | Enable premium ad collection, the ability to skip watching ads and collect reward instantly. | on | on, off |
| ENABLE_EGG_COLLECT | Collect eggs in game if they are available and hatch them. | on | on, off |
| ENABLE_TAPPING | Enable tapping on titans / game screen (this also enables clicking on fairies on screen). | on | on, off |
| ENABLE_TOURNAMENTS | Enable entering and collecting rewards from tournaments in game. | on | on, off |

### General Action Options
| config | Description | Default | Examples |
|-----------------------------|-------------------------------------------------------------------------------------|---------|-------------|
| RUN_ACTIONS_EVERY_X_SECONDS | The action of running all three actions (if enabled) should happen every x seconds. | 40 | 40, 80, 500 |
| RUN_ACTIONS_ON_START | Run actions on initial bot startup (skip interval times initially). | on | on, off |
| ORDER_LEVEL_HEROES | Determine the order of the level heroes action. | 1 | 1, 2, 3 |
| ORDER_LEVEL_MASTER | Determine the order of the level sword master action. | 2 | 1, 2, 3 |
| ORDER_LEVEL_SKILLS | Determine the order of the level skills action. | 3 | 1, 2, 3 |

### Clan Quest Action Options
| config | Description | Default | Examples |
|--------------------|------------------------------------------------------------------------------------------------------------------------------|---------|----------|
| ENABLE_CLAN_QUEST | Enable the clicking/checking and fighting of the clan quest in game if ones available. | on | on, off |
| ENABLE_EXTRA_FIGHT | Enable the ability to perform an additional fight when battling in clan quest (only if second fight of battle (5 diamonds)). | on | on, off |

### Master Action Options
| config | Description | Default | Examples |
|------------------------|---------------------------------------------------------------|---------|----------|
| ENABLE_MASTER | Enable the leveling of the sword master. | on | on, off |
| MASTER_LEVEL_INTENSITY | Determine the amount of clicks performed on the sword master. | 3 | 3, 5, 20 |

### Heroes Action Options
| config | Description | Default | Examples |
|----------------------|-----------------------------------------------------------------------------------|---------|----------|
| ENABLE_HEROES | Enable the leveling of heroes in game. | on | on, off |
| HERO_LEVEL_INTENSITY | Determine the amount of clicks performed on each hero during the level up process | 3 | 3, 5, 20 |

### Skills Action Options
| config | Description | Default | Examples |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------|---------|------------|
| ENABLE_SKILLS | Enable interactions with the sword masters skills in game. | on | on, off |
| ACTIVATE_SKILLS_ON_START | Should all skills specified below be activated on start once without taking into account intervals. | on | on, off |
| INTERVAL_HEAVENLY_STRIKE | Activate heavenly strike every x seconds. (0 = do not activate). | 0 | 0, 10, 200 |
| INTERVAL_DEADLY_STRIKE | Activate deadly strike every x seconds. (0 = do not activate). | 0 | 0, 10, 200 |
| INTERVAL_HAND_OF_MIDAS | Activate hand of midas every x seconds. (0 = do not activate). | 0 | 0, 10, 200 |
| INTERVAL_FIRE_SWORD | Activate fire sword every x seconds. (0 = do not activate). | 130 | 0, 10, 200 |
| INTERVAL_WAR_CRY | Activate war cry every x seconds. (0 = do not activate). | 0 | 0, 10, 200 |
| INTERVAL_SHADOW_CLONE | Activate shadow clone every x seconds. (0 = do not activate). | 200 | 0, 10, 200 |
| FORCE_ENABLED_SKILLS_WAIT | Given the intervals specified above, determine if skills should only be activated once the biggest interval is reached. | on | on, off |
| SKILL_LEVEL_INTENSITY | Determine the amount of clicks performed on each skill during the level up process. | 10 | 10, 20, 50 |

### Prestige Action Options
| config | Description | Default | Examples |
|--------------------------|-------------------------------------------------------------|---------|-------------|
| ENABLE_AUTO_PRESTIGE | Enable the auto prestige functionality in game. | on | on, off |
| PRESTIGE_AFTER_X_MINUTES | Determine the amount of minutes between each auto prestige. | 90 | 30, 90, 200 |

### Artifacts Action Options
| config | Description | Default | Examples |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------|-----------------|-----------------------------------------------------------|
| ENABLE_ARTIFACT_PURCHASE | Enable artifact purchases. | on | on, off |
| UPGRADE_ARTIFACT | Specify the name of the artifact that will be upgraded (Take the name of the artifact, replace spaces with underscored, all lowercase. | book_of_shadows | stryfes_peace, ward_of_the_darkness, flute_of_the_soloist |

### Stats Options
| config | Description | Default | Examples |
|-------------------------------|-----------------------------------------------------------------|---------|------------|
| ENABLE_STATS | Enable statistic updates. | on | on, off |
| STATS_UPDATE_INTERVAL_MINUTES | How many minutes between each stat update while bot is running. | 30 | 30, 60, 90 |

### Artifact Parsing Options
| config | Description | Default | Examples |
|-----------------|--------------------------------------------------------------------------------|----------------------|------------------------------------------------------|
| BOTTOM_ARTIFACT | Specify which artifact is located at the bottom of your artifact list in game. | ward_of_the_darkness | ward_of_the_darkness, aram_spear, the_masters_sword  |

### Logging Options
| config | Description | Default | Examples |
|----------------|------------------------------------------------------------------|---------|---------------------------------------|
| ENABLE_LOGGING | Enable logging information during bot runtime. | off | off, on |
| LOGGING_LEVEL | Specify the level at which the logger should show messages from. | DEBUG | INFO, DEBUG, WARNING, ERROR, CRITICAL |

# Development
Thanks for taking the time to check this project out! Any ideas of requests are ideal and can be done directly through GitHub, feel free to leave feedback or ideas in the issues section of the project!
