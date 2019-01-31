# tt2-py (TT2 PY)
A bot written in Python that automates the process of playing Tap Titans 2.

# Features

- Configurable settings to gear the bot towards your build/play style.
- Activate specific skills on cooldown (or activate numerous skills once a main skill is ready).
- Automatically level the sword master, skills, and heroes in game.
- Automatic prestige after a specified period of time.
- Participate in tournaments when they are available.
- Hatch and collect eggs when they are available.
- Collect your daily reward in game when it is available.
- Participant in your clan battles with option to spend diamonds and fight again.
- Store all of your statistics in a single location, with the ability to view how much progress has been made during a session.

# Requirements

- Windows OS
- [Python 3.7](https://www.python.org/downloads/release/python-370/)
- [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract)
- Android Emulator (Currently Supported: [Nox](https://www.bignox.com/))

# Bot Usage
To use the Bot, you will need to ensure that your emulator is placed at the
top most left portion of your windows screen. Make sure Tap Titans 2 is open.

You can use the following command to start running the bot:

```python -m tt2.core.run```

*Note that you should run the command from the project's root directory.*

You can observe the informational logs that are outputted while the bot runs to get a better idea of what
exactly is happening and when it is happening.

Additionally, all your bot sessions are recorded in the `stats.json` file that is generated. You may use this to audit your
uses of the bot.

---

#### Exiting
Exiting the bot can be done by dragging your mouse to the top left portion of your desktop, a log message will
be outputted letting you know that the bot is shutting down, you can choose to perform a soft
shutdown at this point to perform you clean up before the bot is totally terminated. This currently
just performs a forced stats update that looks at your hero stats panels and does
some image recognition to record the values.

#### Note

This isn't a serious project and it is something that I work on in my free time. It's a bit of a hassle to even spin
up and have running, if you would like to lend a hand with development or think you have some great ideas in mind for additional features,
don't hesitate to throw up a pull request. You can also reach me at:

theycallmevotum@gmail.com