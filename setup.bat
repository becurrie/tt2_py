:: Create Virtualenv.
:: Expecting virtualenvwrapper-win
call cd "%~dp0%"
call mkvirtualenv titandash
call "%WORKON_HOME%/titandash/Scripts/python.exe" -m pip install -U --force-reinstall pip
call "%WORKON_HOME%/titandash/Scripts/pip" install -r "%~dp0%requirements.txt" --no-cache-dir

:: Using new virtual environment, make and migrate.
call "%WORKON_HOME%/titandash/Scripts/python" "%~dp0%titanbot/manage.py" createcachetable
call "%WORKON_HOME%/titandash/Scripts/python" "%~dp0%titanbot/manage.py" makemigrations
call "%WORKON_HOME%/titandash/Scripts/python" "%~dp0%titanbot/manage.py" migrate

:: Install node modules.
call npm install

:: Collect static files.
call "%WORKON_HOME%/titandash/Scripts/python" "%~dp0%titanbot/manage.py" collectstatic --noinput

PAUSE
