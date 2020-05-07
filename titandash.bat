@echo off
call workon titandash
call cd "%~dp0%titanbot"
call "%WORKON_HOME%/titandash/Scripts/python" titandash.py %1
