# TitanBot
Progression Bot/Tool Kit.

TitanBot is a bot written in python that enables the mobile tap game Tap Titans 2 to play and progress with numerous configuration options.

---

**Table of Contents**
- [TitanBot](#titanbot)
- [Current Features](#current-features)
  - [Tools](#tools)
    - [Artifact Parsing](#artifact-parsing)
- [Requirements](#requirements)
- [Setting Up / Running Bot](#setting-up--running-bot)
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
    - [Recovery Options](#recovery-options)
    - [Logging Options](#logging-options)
- [Development](#development)

# Current Features
- Fully configurable settings to gear the bot's functionality to match your playstyle/build.
- Activate chosen in game skills on a specified cooldown, with the option to wait for one specific skill before activating others.
- Automatically level up the sword master, skills and heroes in game with a specified amount of intensity (clicks).
- Automatically prestige after a specified amount of minutes spent in a run or once a certain stage has been reached.
    - Choose a percent of your max stage to prestige at (99, 99.7, 100.1, etc).
- Upgrade a specific artifact after a prestige takes place.
    - Upgrade a specified tier(s) of artifacts (one per prestige).
    - Shuffle list to upgrade different ones each session.
- Participate in tournaments when they become available (enter/collect rewards).
- Hatch and collect any eggs when they become available.
- Automatically collect daily achievements every X amount of hours.
- Collect clan crates in game.
- Store all game/bot/session statistics in a single location to provide some insight into progress made.
- Console/file logging capabilities to provide debugging and bug tracking.
- Recovery system in place to restart the emulator and game if unrecoverable errors occur.

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
| POST_ACTION_MIN_WAIT_TIME | Minimum amount of seconds to sleep for after a bot function is finished. | 1 | 1, 4, 10 |
| POST_ACTION_MAX_WAIT_TIME | Maximum amount of seconds to sleep for after a bot function is finished. | 3 | 3, 8, 20 |

### Device Options
| config | Description | Default | Examples |
|----------|--------------------------------------------------|---------|----------|
| EMULATOR | Specify the emulator service that is being used. | nox | nox |

### Generic Options
| config | Description | Default | Examples |
|---------------------------|----------------------------------------------------------------------------------------------|---------|----------|
| ENABLE_PREMIUM_AD_COLLECT | Enable premium ad collection, the ability to skip watching ads and collect reward instantly. | on | on, off |
| ENABLE_EGG_COLLECT | Collect eggs in game if they are available and hatch them. | on | on, off |
| ENABLE_TAPPING | Enable tapping on titans / game screen (this also enables clicking on fairies on screen). | on | on, off |
| ENABLE_TOURNAMENTS | Enable entering and collecting rewards from tournaments in game. | on | on, off |

### Daily Achievements
| config | Description | Default | Examples |
|----------------------------------------|----------------------------------------------------------------------------|---------|----------|
| ENABLE_DAILY_ACHIEVEMENTS | Enable daily achievements checks in game. | on | on, off |
| RUN_DAILY_ACHIEVEMENT_CHECK_ON_START | Should a daily achievement check take place as soon as the bot is started? | on | on, off |
| CHECK_DAILY_ACHIEVEMENTS_EVERY_X_HOURS | How often should the daily achievement checks take place? | 4 | 2, 4, 8 |

### General Action Options
| config | Description | Default | Examples |
|-----------------------------|-------------------------------------------------------------------------------------|---------|-------------|
| RUN_ACTIONS_EVERY_X_SECONDS | The action of running all three actions (if enabled) should happen every x seconds. | 40 | 40, 80, 500 |
| RUN_ACTIONS_ON_START | Run actions on initial bot startup (skip interval times initially). | on | on, off |
| ORDER_LEVEL_HEROES | Determine the order of the level heroes action. | 1 | 1, 2, 3 |
| ORDER_LEVEL_MASTER | Determine the order of the level sword master action. | 2 | 1, 2, 3 |
| ORDER_LEVEL_SKILLS | Determine the order of the level skills action. | 3 | 1, 2, 3 |

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
| MAX_SKILL_IF_POSSIBLE | Determine if your skills should be upgraded to their max available level. | on | on, off |
| SKILL_LEVEL_INTENSITY | Determine the amount of clicks performed on each skill during the level up process. | 10 | 10, 20, 50 |

### Prestige Action Options
| config | Description | Default | Examples |
|--------------------------|-------------------------------------------------------------|---------|-------------|
| ENABLE_AUTO_PRESTIGE | Enable the auto prestige functionality in game. | on | on, off |
| PRESTIGE_AFTER_X_MINUTES | Determine the amount of minutes between each auto prestige. Note that will be used to set a hard limit on prestiges that take place relating to the stage prestige options (if they are enabled). | 90 | 30, 90, 200 |
| PRESTIGE_AT_STAGE | Set this to something other than 0 to automatically initiate a prestige once you reach a certain stage. | 0 | 0, 1000, 10000, 55000 |
| PRESTIGE_AT_MAX_STAGE | Turn this setting on to enable the auto prestige once you reach you current highest stage (max prestige). | off | off, on |
| PRESTIGE_AT_MAX_STAGE_PERCENT | Specify a percentage that will be used to perform an auto prestige once your current stage reaches the percent chosen of your highest stage. | 0 | 0, 80, 90, 110 | 

### Artifacts Action Options
| config | Description | Default | Examples |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------|-----------------|-----------------------------------------------------------|
| ENABLE_ARTIFACT_PURCHASE | Enable artifact purchases. | on | on, off |
| UPGRADE_ARTIFACT | Specify the name of the artifact that will be upgraded (Take the name of the artifact, replace spaces with underscored, all lowercase. | book_of_shadows | stryfes_peace, ward_of_the_darkness, flute_of_the_soloist |
| UPGRADE_OWNED_ARTIFACTS | Enable ability to iterate through all owned artifacts and upgrade a different one each prestige. | on | on, off |
| UPGRADE_OWNED_TIER | Specify a specific artifact tier that will be upgraded instead of all artifacts owned. This may also be a comma separated list to combine tiers. | S | S, A, B, C, "S,A" |
| SHUFFLE_OWNED_ARTIFACTS | Turn this on to shuffle the list of specified artifacts before upgrading any. This is useful if you start/stop the bot often and don't want the same artifacts being upgraded all the time. | off | off, on |
| IGNORE_SPECIFIC_ARTIFACTS | Specify a single artifact, or multiple artifacts (comma separated) that will be ignored completely when an upgrade takes place. (off to disable). | off | off, book_of_shadows, "book_of_shadows,heroic_shield" |

### Stats Options
| config | Description | Default | Examples |
|-------------------------------|-----------------------------------------------------------------|---------|------------|
| ENABLE_STATS | Enable statistic updates. | on | on, off |
| UPDATE_STATS_ON_START | Should a statistics update take place when the bot first starts? | on | on, off |
| STATS_UPDATE_INTERVAL_MINUTES | How many minutes between each stat update while bot is running. | 30 | 30, 60, 90 |

### Artifact Parsing Options
| config | Description | Default | Examples |
|-----------------|--------------------------------------------------------------------------------|----------------------|------------------------------------------------------|
| BOTTOM_ARTIFACT | Specify which artifact is located at the bottom of your artifact list in game. | ward_of_the_darkness | ward_of_the_darkness, aram_spear, the_masters_sword  |

### Recovery Options
| config | Description | Default | Examples |
|---------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|-------------|
| RECOVERY_CHECK_INTERVAL_MINUTES | How long between resets for the errors counter. If the amount of errors in the amount of minutes specified exceeds the specified allowed failures, a recovery takes place. | 5 | 5, 10, 60 |
| RECOVERY_ALLOWED_FAILURES | How many failures are allowed within the specified interval before a game recovery takes place? | 45 | 45, 70, 100 |

### Logging Options
| config | Description | Default | Examples |
|----------------|------------------------------------------------------------------|---------|---------------------------------------|
| ENABLE_LOGGING | Enable logging information during bot runtime. | off | off, on |
| LOGGING_LEVEL | Specify the level at which the logger should show messages from. | DEBUG | INFO, DEBUG, WARNING, ERROR, CRITICAL |

# Development
Thanks for taking the time to check this project out! Any ideas of requests are ideal and can be done directly through GitHub, feel free to leave feedback or ideas in the issues section of the project!
