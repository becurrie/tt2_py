"""
run.py

Main entry point into bot script. Ensuring that the directory is
manually added to the system path so all modules are able to be imported.
"""
from os import sys, getcwd
sys.path.append("\\".join(getcwd().split("\\")[:-2]))

if __name__ == '__main__':
    from tt2.core.bot import Bot

    # Initialize bot directly here and begin game loop.
    Bot().run()
