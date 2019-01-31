"""
run.py

Main entry point into bot script.
"""
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath("tt2"))))

if __name__ == '__main__':
    from tt2.core.bot import Bot

    # Initialize bot directly here and begin game loop.
    Bot().run()
