from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.management import call_command
from django.http.response import JsonResponse

from titanbootstrap.utils import DependencyChecker, VersionChecker, purge_dir, launch_process

import zipfile
import redis
import subprocess
import traceback
import dirsync
import datetime
import os
import io


class DependencyError(Exception):
    """
    Base Dependency Error.
    """
    pass


class TesseractCheckError(DependencyError):
    """
    Tesseract Dependency Error.
    """
    pass


class NodeCheckError(DependencyError):
    """
    NodeJS Dependency Error.
    """
    pass


def _exception_response(title, exception, as_json=False, extra=None):
    """
    Given a title and exception, create  response that represents our exception.

    We can optionally decide to return the data as a json dictionary instead of
    returning a valid JsonResponse object.

    Use the extra parameter to include some text below the traceback.
    """
    data = {
        "status": "ERROR",
        "title": title,
        "traceback": traceback.format_exc().replace("\n", "<br/>"),
        "type": exception.__class__.__name__
    }

    if extra:
        data["traceback"] += "<br/><br/>{extra}".format(extra=extra)
    if as_json:
        return data

    # By default, we return the data as a JsonResponse object.
    # We can specify to return as pure data for use with dependencies.
    return JsonResponse(data=data)


def bootstrap(request):
    """
    Render the bootstrapping page with a unique filename for our bootstrap javascript file.
    """
    return render(request, "bootstrap/bootstrap.html", context={
        "bootstrap_js": mark_safe("js/bootstrap/bootstrap.js?{uniq}".format(
            uniq=str(datetime.datetime.utcnow().timestamp()).split(".")[0]))
    })


def check_update(request):
    """
    Check for an available update for the titandash program.
    """
    # Note that this can't fail so no need for try: except here.
    # If a new version can't be obtained, falling back to an error status.
    version = VersionChecker()

    return JsonResponse(data={
        "status": version.perform_check(),
        "current": version.current,
        "newest": version.newest
    })


def perform_update(request):
    """
    Perform an update on the titandash program.

    This is a potentially dangerous command and as such, certain things are put
    in place to ensure errors are handled gracefully.

    The following functionality is handled here:

    1. Download the most recent titandash release.
    2. Create a backup of the users current code base.
    3. Synchronize newest release with current code base.
    4. If no exceptions occur, return json response with data about finished process.
    5. If exceptions occur, attempt to synchronize the backup into the users code base.
    6. If exceptions occurs here, return helpful error message.
    """
    version = VersionChecker()
    try:
        # Downloading the source package containing all the newest source code.
        directory = version.download_newest()
        # Remove the most recent backup from our local data directory.
        purge_dir(path=settings.LOCAL_DATA_BACKUP_DIR)

        # Create a backup of the current code directory by syncing the current
        # directory into our local backups directory.
        dirsync.sync(
            sourcedir=settings.ROOT_DIR,
            targetdir=settings.LOCAL_DATA_BACKUP_DIR,
            action="sync",
            exclude=(
                "node_modules", "titanbot/static", "titanbot/logs", ".git",
                ".github", ".idea", ".gitattributes", ".gitignore"
            )
        )

        # Let's go ahead and attempt to synchronize our newly downloaded
        # version package into our current code.
        try:
            dirsync.sync(
                sourcedir=directory,
                targetdir=settings.ROOT_DIR,
                action="sync",
                purge=True
            )
        except Exception as exc:
            # An exception has occurred while attempting to update the code base,
            # our best bet here is to recover our backup so that the code goes back
            # to what it was before the update.
            dirsync.sync(
                sourcedir=settings.LOCAL_DATA_BACKUP_DIR,
                targetdir=settings.ROOT_DIR,
                action="sync"
            )

            # Returning a recovered status to the javascript...
            # Since we're restoring our backup directory, our code
            # should not have changed, we can continue with bootstrapping and
            # display a message at the end about what happened.
            return JsonResponse(data={
                "status": "RECOVERED",
                "exception": _exception_response(
                    title="Perform Update",
                    exception=exc,
                    as_json=True,
                    extra="The exception above occurred while attempting to update titandash to the newest version, "
                          "a backup of all your application files was safely recovered and the program has not been "
                          "updated.<br/><br/>You can attempt to auto update again by refreshing the page, or, download "
                          "the newest release manually."
                )
            })

        # After an update is successful, we perform both the node install,
        # and the static files collection process. Since cache busting can break
        # after an update is complete, since all files are purged.
        perform_node_packages(request)
        perform_static(request)

        # We were able to successfully synchronize the newest codebase into our main directory.
        # We should now return some useful information to the bootstrapping javascript
        # to let the user know that it has been updated successfully, and that they should
        # restart their application to see the newest changes.
        return JsonResponse(data={
            "status": "DONE"
        })

    # Very unrecoverable error has occurred, This means the code base is not reliable.
    # The user may need to manually download the latest release themselves at this point.
    # The users database and logs will remain.
    except Exception as exc:
        return _exception_response(
            title="Perform Update",
            exception=exc,
            extra="<br/>This error could not be recovered from and your code base is now in an inconsistent state. "
                  "Don't worry though! You can go and download the newest release manually still. Check out "
                  "<a href='https://titandash.net'>this</a> link to do that now.<br/>You're data has <strong>not</strong> been "
                  "lost due to this error."
        )


def perform_requirements(request):
    """
    Perform the pip install on our requirements file.

    Ensuring tht any new requirements or needed functionality is present in our application and available.
    """
    try:
        # As long as this command executes without raising an exception,
        # we can safely assume the requirements are now uo to date.
        return JsonResponse(data={
            "status": "DONE",
            "output": str(subprocess.check_output(["pip", "install", "-r", os.path.join(settings.ROOT_DIR, "requirements.txt")]))
        })

    # Catching a broad exception clause to ensure that we can move forward
    # with execution no matter what error occurs.
    except Exception as exc:
        return _exception_response(
            title="Python Requirements",
            exception=exc,
        )


def perform_node_packages(request):
    """
    Perform the node package manager install process to install all of our required modules.

    This command will fail if node is not installed by the user. But we can broads catch and
    catch the more detailed exception below with our dependency check.
    """
    try:
        # Again, as long as our subprocess command completes, we can assume the modules were all installed.
        # Also setting our working directory explicitly to ensure the install command uses proper package file.
        return JsonResponse(data={
            "status": "DONE",
            "output": str(subprocess.check_output("npm install", shell=True, cwd=settings.ROOT_DIR))
        })

    # Catching a broad exception again to ensure processes move forward on errors.
    except Exception as exc:
        return _exception_response(
            title="Node Package Install",
            exception=exc
        )


def perform_migration(request):
    """
    Perform the database migration functionality.
    """
    try:
        call_command("makemigrations")
        call_command("migrate")

        # After both commands have ran successfully, migrations
        # are guaranteed to be up to date.
        return JsonResponse(data={
            "status": "DONE"
        })

    # Broad exception clause here in case an odd error occurs
    # while attempting to migrate...
    except Exception as exc:
        return _exception_response(
            title="Database Migrations",
            exception=exc
        )


def perform_cache(request):
    """
    Perform the database caching migration command functionality.
    """
    try:
        call_command("createcachetable")

        # After command is complete, cache table is created successfully.
        return JsonResponse(data={
            "status": "DONE"
        })

    # Similar to other process exception clauses... See above.
    except Exception as exc:
        return _exception_response(title="Database Caching", exception=exc)


def perform_static(request):
    """
    Perform the static files collection functionality.
    """
    try:
        call_command("collectstatic", interactive=False)

        # After command is complete, static files have been created successfully.
        return JsonResponse(data={
            "status": "DONE"
        })

    # Another broad exception catch here. See perform_migration comment stub
    # for more information about this.
    except Exception as exc:
        return _exception_response(title="Collect Staticfiles", exception=exc)


def _check_tesseract():
    """
    Perform our tesseract checking functionality here, making sure our compressed dependency is present
    and extracted within the users application directory.

    - If tesseract is not currently extracted and present, we do that here once.
    - If tesseract is already extracted and present, we do nothing and move forward with our checks.
    """
    extracted = os.path.exists(path=settings.LOCAL_DATA_TESSERACT_DEPENDENCY_DIR)

    if not extracted:
        try:
            # This should only take place once (unless dir is removed).
            with zipfile.ZipFile(io.BytesIO(DependencyChecker().retrieve_tesseract().content)) as zip_file:
                zip_file.extractall(path=settings.LOCAL_DATA_TESSERACT_DEPENDENCY_DIR)
        except Exception as exc:
            # Error occurred, provide somewhat useful message.
            return _exception_response(
                title="Dependencies - Tesseract",
                exception=exc,
                as_json=True,
                extra="An error occurred while attempting to extract tesseract into your local application data directory."
            )


def _check_redis():
    """
    Perform our redis checking functionality here, making sure our compressed dependency is present
    and extracted within the users application directory.

    - If redis is not currently extracted and present, we do that here once.
    - If redis is already extracted and present, we do not need to download any data.
    - If redis is not currently running, we boot it up here.
    - If redis is already running, we do nothing and move forward with our checks.
    """
    extracted = os.path.exists(path=settings.LOCAL_DATA_REDIS_DEPENDENCY_DIR)

    if not extracted:
        try:
            # This should only take place once (unless dir is removed).
            with zipfile.ZipFile(io.BytesIO(DependencyChecker().retrieve_redis().content)) as zip_file:
                zip_file.extractall(path=settings.LOCAL_DATA_REDIS_DEPENDENCY_DIR)
        except Exception as exc:
            # Error occurred, provide somewhat useful message.
            return _exception_response(
                title="Dependencies - Redis",
                exception=exc,
                as_json=True,
                extra="An error occurred while attempting to extract redis into your local application data directory."
            )

    # We now definitely have a directory that contains our redis data.
    # Check if it's running, and start it if not.
    try:
        redis.Redis("localhost").client_list()

        # Getting past the call above means redis is running
        # on our localhost properly, no need to perform anything additional.
        return True

    except redis.ConnectionError:
        # Connection refused, let's just try to start the server
        # wait very briefly, and attempt to grab the client list again.
        launch_process(command=settings.REDIS_COMMAND, sleep=2)

        try:
            redis.Redis("localhost").client_list()

            # Similar to above, getting here means redis is running.
            return True
        except Exception as exc:
            return _exception_response(
                title="Dependencies - Redis",
                exception=exc,
                as_json=True,
                extra="An error occurred while attempting to check the current status of redis."
            )
    except Exception as exc:
        return _exception_response(
            title="Dependencies - Redis",
            exception=exc,
            as_json=True,
            extra="An error occurred while attempting to check the current status of redis."
        )


def _check_node():
    """
    Test that node has been installed on the users machine.

    We can return a helpful message to users if it turns out that node is missing.

    Once a user installs node, no additional configuration is needed by us. Node is automatically
    included on the users system path so that it can be used from anywhere.
    """
    exception = NodeCheckError("It looks like node is not installed on your system. Node is used to download "
                               "numerous dependencies that are used by the web application. The dashboard may not "
                               "work correctly until you've installed node and ran the npm install command.")

    try:
        check = subprocess.run("npm --version", shell=True, universal_newlines=True)

        # Do we have a proper return code for the subprocess called?
        if check.returncode == 0:
            return True
        else:
            raise exception

    # Check for a file not found error which may occur when npm is not installed at all
    # on the users system.
    except subprocess.CalledProcessError:
        return _exception_response(
            title="Dependencies - Node",
            exception=exception,
            as_json=True
        )
    # Catch broadly for errors that occur when trying to check status of node.
    except Exception as exc:
        return _exception_response(
            title="Dependencies - Node",
            exception=exc,
            as_json=True)


def perform_dependency(request):
    """
    Perform dependency checks here.

    After a user installs the required dependencies, some steps may need to be taken
    to ensure they are all configured correctly. We can at least test for some of them
    here and return some helpful errors if it turns out that something is mis configured.
    """
    exceptions = []

    # Loop through every available dependency check.
    # A failed check should return a JsonResponse object.
    # Successful ones will just return a bool that can be ignored.
    for check in [_check_tesseract, _check_redis, _check_node]:
        res = check()
        if isinstance(res, dict):
            exceptions.append(res)

    if len(exceptions) > 0:
        return JsonResponse(data={
            "status": "ERROR",
            "exceptions": exceptions,
        })

    return JsonResponse(data={
        "status": "DONE"
    })
