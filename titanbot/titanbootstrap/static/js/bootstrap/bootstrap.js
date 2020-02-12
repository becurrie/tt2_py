/**
 * bootstrap.js
 *
 * Control the titandash bootstrapping functionality.
 *
 * We handle this through our web application with javascript that interacts with the django web server
 * so that the following processes can be handled directly by the server.
 *
 * 1. Titandash Updates.
 *      - Is a newer version available that can be downloaded and extracted into the main source directory.
 *      - We are using a local django web server here, so now real compilation ever has to take place, ideally,
 *        we can simply replace the source python that's been packaged into an exe after the code has been synced.
 *
 * 2. Titandash Database Migrations.
 *      - Begin by making migrations.
 *      - Finish by applying migrations.
 *
 * 3. Titandash Staticfiles Collection.
 *      - Call the collectstatic files command to ensure all needed static files are available.
 *      - This is mostly only needed to ensure our node modules are included and available for local use.
 */
$(document).ready(function() {
    // Initialize the titandash bootstrapper.
    return new TitandashBootstrapper();
});

/**
 * Place all functionality into an encapsulated javascript function.
 */
let TitandashBootstrapper = function() {
    // Set null version of iterator, turned on when instance is
    // created, used to stop the iterator if needed.
    let _messageIterator = null;
    // Set empty an error container that will be used once the bootstrapper
    // has finished all processes. If errors are present, we can display them,
    // and allow the user manually head to the homepage, instead of redirecting them there.
    let _errorContainer = [];

    // Expecting json when sending ajax requests.
    let ajaxDataType = "JSON";

    // Specifying our ajax urls used throughout the bootstrap
    // process. Most of these are idempotent other than the update checker.
    let ajaxUrls = {
        checkUpdates: "/bootstrap/ajax/check_update",
        performUpdate: "/bootstrap/ajax/perform_update",
        performRequirements: "/bootstrap/ajax/perform_requirements",
        performNodePackages: "/bootstrap/ajax/perform_node_packages",
        performMigration: "/bootstrap/ajax/perform_migration",
        performCache: "/bootstrap/ajax/perform_cache",
        performStatic: "/bootstrap/ajax/perform_static",
        performDependency: "/bootstrap/ajax/perform_dependency"
    };

    // Grab all elements used by the bootstrapper.
    // Most functionality is handled within the ajax
    // views, so not many elements are needed.
    let elements = {
        // Update Modals.
        bootstrapUpdateModal: $("#bootstrapUpdateModal"),
        bootstrapUpdateBody: $("#bootstrapUpdateBody"),
        bootstrapUpdateYesButton: $("#bootstrapUpdateYesButton"),
        bootstrapUpdateNoButton: $("#bootstrapUpdateNoButton"),

        // Bootstrapper.
        bootstrapProgressBar: $("#bootstrapProgressBar"),
        bootstrapStepMessage: $("#bootstrapStepMessage"),
        bootstrapTable: $("#bootstrapTable"),

        // Messages
        bootstrapMessages: $("#bootstrapMessages"),
        // Exceptions.
        bootstrapExceptionContainer: $("#bootstrapExceptionContainer"),
        // Updated.
        bootstrapUpdatedContainer: $("#bootstrapUpdatedContainer"),
        // Continue.
        bootstrapContinue: $("#bootstrapContinue")
    };

    /**
     * Update the bootstrapper progress bar. Only five processes are even possible.
     *
     * If an update is available and the user is selecting an option and then waiting for
     * the update to complete, we can go use progress 1-3. Otherwise, we should start at 3-5.
     */
    let updateProgressBar = function(progress) {
        if (progress !== 0)
            progress = `${progress}%`;

        elements.bootstrapProgressBar.css({
            width: progress
        });

        if (progress === "100%") {
            elements.bootstrapProgressBar.removeClass("progress-bar-animated");
            elements.bootstrapProgressBar.removeClass("bg-info");
            if (_errorContainer.length > 0)
                elements.bootstrapProgressBar.addClass("bg-danger");
            else
                elements.bootstrapProgressBar.addClass("bg-success");
        }
    };

    /**
     * Update the message iterator element to display a new message.
     */
    let updateMessageIterator = function(message) {
        elements.bootstrapStepMessage.fadeOut(100, function() {
            elements.bootstrapStepMessage.text(message).fadeIn();
        });
    };

    /**
     * Generate the interval that handles our simple "loading" animation
     * present on our bootstrapping status message element.
     */
    let statusMessageIterator = function(dots, interval) {
        // Setting the backing message iterator object
        // that is used to store reference to the interval.
        _messageIterator = setInterval(function() {
            let lastChars = elements.bootstrapStepMessage.text().trim().slice(0 - dots);
            let currentCount = lastChars.match(/\./g);
            let messageNoDots = elements.bootstrapStepMessage.text().trim().replace(/\./g, "");

            if (currentCount)
                currentCount = currentCount.length;
            else
                currentCount = 0;

            if (currentCount === dots)
                elements.bootstrapStepMessage.text(messageNoDots);
            else
                elements.bootstrapStepMessage.text(elements.bootstrapStepMessage.text().trim() + ".");
        }, interval);
    };

    /**
     * Destroy the interval that is currently handling the "loading" animation
     * present on the bootstrapping status message element.
     */
    let killMessageIterator = function() {
        // Clearing the global message iterator object.
        clearInterval(_messageIterator);

        // Removing any dots from the bootstrap status message element.
        elements.bootstrapStepMessage.text(elements.bootstrapStepMessage.text().replace(".", ""));
        elements.bootstrapStepMessage.text("").fadeOut(function() {
            elements.bootstrapStepMessage.remove();
        });
    };

    /**
     * Display the modal updater modal.
     */
    let showUpdateModal = function(current, newest) {
        elements.bootstrapUpdateModal.modal({backdrop: "static", keyboard: false});
        elements.bootstrapUpdateBody.html("").html(
            `
            <h5>Titandash ${newest} Available.</h5>
            <p>Would you like to update to the newest version now?</p>
            <p>You will be going from version <strong>${current}</strong> to <strong>${newest}</strong></p>
            <hr/>
            <div class="alert alert-warning" role="alert">
                <h4>Note</h4>
                <p>
                    Please note that, after an update is successful, you will need to reboot the titandash
                    application to see the changes present in the newest release.
                </p>
                <hr/>
                <p>
                    If you have any issues with the automated update process, you can always download the newest
                    release directly and extract it somewhere instead of using the auto updater.
                </p>
            </div>
            `
        );

        // Show the modal and ask for input...
        elements.bootstrapUpdateModal.modal("show");

        // Additionally, our modal blocks the user from doing anything until
        // they choose an option (yes, no).
        // Update the message that displays.
        updateMessageIterator("Waiting For User Input");
    };

    /**
     * Setup the update buttons available on the update modal.
     *
     * A user can choose to either update their titandash program, which initiates it's own set of processes.
     * Or they can choose to not update a continue on with the bootstrap process.
     */
    let setupUpdateButtons = function() {
        // Yes button.
        elements.bootstrapUpdateYesButton.off("click").click(function() {
            // The user would like to update their titandash first.
            // Perform this functionality and update the table and progress bar.
            updateProgressBar(25);
            addStatusTableRow("Begin Update Process", "IN PROGRESS", "warning");

            // Begin titandash update process.
            performUpdate();
        });

        // No button.
        elements.bootstrapUpdateNoButton.off("click").click(function() {
            // The user does not wish to update their titandash, we can
            // safely update their status table and the progress bar before beginning
            // the database migration process.
            updateProgressBar(18);
            addStatusTableRow("Begin Update Process", "SKIPPED", "success");

            // Begin python requirements process.
            performRequirements();
        });
    };

    /**
     * Perform the check for available updates.
     *
     * If a new update is available, we can present the user with an modal
     * to either update the program, or continue with using their current version.
     */
    let checkUpdates = function() {
        updateMessageIterator("Checking For Updates");
        $.ajax({
            url: ajaxUrls.checkUpdates,
            dataType: ajaxDataType,
            success: function(data) {
                // An update is available and we should allow the
                // user to choose if they want to update.
                if (data["status"] === "UPDATE_AVAILABLE") {
                    showUpdateModal(data["current"], data["newest"]);
                    updateProgressBar(10);

                    // Add a table element with information about the fact
                    // that an update is going to now take place.
                    addStatusTableRow("Updates", "AVAILABLE", "warning");
                }

                // The titandash program is up to date, or the version checker failed, in which case,
                // just move forward onto next processes with bootstrapping right away.
                if (data["status"] === "UP_TO_DATE" || data["status"] === "VERSION_ERROR") {
                    // Add a table element with information about the successful
                    // update check that took place.
                    addStatusTableRow("Updates", "GOOD", "success");
                    updateProgressBar(20);

                    // Updater process is finished at this point, move on to the python
                    // requirements process.
                    performRequirements();
                }
            }
        });
    };

    /**
     * Perform the titandash program update process.
     *
     * Take a look at the view present that this function accesses for
     * more in depth information about how an update is actually handled.
     *
     * The real problem here is that after an update, the server could potentially break
     * due to an issue with the live change reloader present in django.
     *
     * This shouldn't affect our javascript functionality.
     */
    let performUpdate = function() {
        updateMessageIterator("Updating Titandash");
        $.ajax({
            url: ajaxUrls.performUpdate,
            dataType: ajaxDataType,
            success: function(data) {
                if (data["status"] === "DONE") {
                    addStatusTableRow("Update Titandash", "GOOD", "success");
                    updateProgressBar(100);

                    // Updater has finished, moving onto our restart process.
                    performApplicationRestart();
                }

                // Maybe an error occurred while syncing our code directory with the newest release,
                // in that case, the backup should be synced back into the root directory and we can
                // ensure that the exception is shown.
                if (data["status"] === "RECOVERED") {
                    // Pushing error into list...
                    _errorContainer.push(data["exception"]);

                    // Update the status table to reflect this issue.
                    addStatusTableRow("Update Titandash", "RECOVERED", "danger");

                    // We will continue on with our bootstrapper process after a recovery.
                    performRequirements();
                }

                // A broad exception occurred while attempting to update. We're gonna push that into our
                // errors and update the status table.
                if (data["status"] === "ERROR") {
                    // Pushing the error into list.
                    _errorContainer.push(data);

                    // Update the status table to contain our errored out update.
                    // The error is not displayed here, but stored and ready for use later.
                    addStatusTableRow("Update Titandash", "ERROR", "danger");
                    updateProgressBar(100);

                    // We also do not need to continue with our bootstrapping since unrecoverable
                    // errors that occur while updating may need manual intervention anyways.
                    errorCheck();
                }

                // Whether or not the update failed. We want to stop bootstrapping.
                // If the update is successful, we want to tear down the application.
                // If the update is not successful, we want
            }
        });
    };

    /**
     * Use this function when an update has been completed successfully.
     *
     * We will let the user know that the update has been completed successfully, and that they
     * should go ahead and completely restart the program.
     *
     * They could decide to continue using the bot at this point, but none of the updates will be live yet.
     */
    let performApplicationRestart = function() {
        killMessageIterator();

        // Display the hidden successful update message to the user.
        elements.bootstrapUpdatedContainer.fadeIn(500);
    };

    /**
     * Perform the python requirements process for the current titandash program.
     *
     * This ensures that the virtual environment being used also contains all the most up to
     * date module requirements present in the requirements.txt file.
     */
    let performRequirements = function() {
        updateMessageIterator("Python Requirements");
        $.ajax({
            url: ajaxUrls.performRequirements,
            dataType: ajaxDataType,
            success: function(data) {
                // The python requirements process was successful, no errors have occurred.
                // Again, this doesn't mean any new requirements were installed though.
                if (data["status"] === "DONE") {
                    addStatusTableRow("Python Requirements", "GOOD", "success")
                }

                // A broad exception occurred while attempting to install requirements. Push error
                // to list of exceptions and continue.
                if (data["status"] === "ERROR") {
                    // Push the error into our error container.
                    _errorContainer.push(data);

                    // Update the status to contain the errored out requirements.
                    addStatusTableRow("Python Requirements", "ERROR", "danger");
                }

                // Regardless of our status, update the progress bar and move on to the next process.
                updateProgressBar(32);

                // Requirements process is finished, move on to the database migrations.
                performNodePackages();
            }
        });
    };

    /**
     * Perform the node package manager install functionality to install node modules into our project.
     *
     * Not to be confused with the dependency check that also does a node check.
     *
     * This function only attempts to perform an npm install, whereas the dependency check actually
     * looks to see if node is installed, and returns a helpful message if it is not available.
     */
    let performNodePackages = function() {
        updateMessageIterator("Installing Node Packages");
        $.ajax({
            url: ajaxUrls.performNodePackages,
            dataType: ajaxDataType,
            success: function(data) {
                // The node package install was successful, meaning no error occurred. This does not
                // mean that packages were installed, since new ones may not be needed.
                if (data["status"] === "DONE") {
                    addStatusTableRow("Node Packages", "GOOD", "success");
                }

                // A broad exception occurred while attempting to install node packages.
                // This could mean that node just isn't installed, which is handled in more
                // detail by the dependency check below.
                if (data["status"] === "ERROR") {
                    // Push the error that occurred into our error container.
                    _errorContainer.push(data);

                    // Update the status table to contain our errored out migrations.
                    addStatusTableRow("Node Packages", "ERROR", "danger");
                }

                // Regardless of status, updating progress bar.
                updateProgressBar(40);

                // Node packages has finished, move on to the database migrations.
                performDatabaseMigrations();
            }
        });
    };

    /**
     * Perform the database migrations for the current titandash program.
     *
     * Migrations are made first, to ensure they are up to date, and then a database
     * migration is actually ran on the live server.
     *
     * The user only needs to see that the migrations are taking place. We do not need
     * to provide specific information about migrations made and migrate status.
     */
    let performDatabaseMigrations = function() {
        updateMessageIterator("Database Migrations");
        $.ajax({
            url: ajaxUrls.performMigration,
            dataType: ajaxDataType,
            success: function(data) {
                // The database migration was successful, meaning no error occurred. This does
                // not mean that migrations were applied, since new ones may not exist.
                if (data["status"] === "DONE") {
                    addStatusTableRow("Migrations", "GOOD", "success");
                }

                // A broad exception occurred while attempting to migrate. We're gonna push that
                // into our errors and update the status table...
                if (data["status"] === "ERROR") {
                    // Push the error that occurred into our error container.
                    _errorContainer.push(data);

                    // Update the status table to contain our errored out migrations.
                    // The error is not displayed here, but stored and ready for use later.
                    addStatusTableRow("Migrations", "ERROR", "danger");
                }

                // Regardless of status, updating the progress bar now.
                updateProgressBar(54);

                // Migrations process has finished, move on to the
                // database caching process.
                performDatabaseCache();
            }
        });
    };

    /**
     * Perform the database cache migration command for the current titandash program.
     *
     * This only ever needs to be done once on the database being used... We can simply
     * display whether or not the command succeeded (if the command was not needed, this is still a success).
     */
    let performDatabaseCache = function() {
        updateMessageIterator("Database Caching");
        $.ajax({
            url: ajaxUrls.performCache,
            dataType: ajaxDataType,
            success: function(data) {
                // The database caching command was successful, no errors occurred while it was
                // being done. This does not necessarily mean the table was created.
                if (data["status"] === "DONE") {
                    addStatusTableRow("Database Cache", "GOOD", "success");
                }

                // A broad exception occurred while attempting to run the command. We can push
                // the error into our errors and update the status table.
                if (data["status"] === "ERROR") {
                    // Push the error into the error container.
                    _errorContainer.push(data);
                }

                // Regardless of status, updating progress bar.
                updateProgressBar(66);

                // Database caching process has finished, move on to the
                // static files collection process.
                performStaticFiles();
            }
        });
    };

    /**
     * Perform the static files collection for the current tiandash program.
     *
     * Collecting all required static files into the static directory.
     *
     * Similar to database migrations, we do not need to display additional information.
     * just that the command is taking place and whether or not it worked or not.
     */
    let performStaticFiles = function() {
        updateMessageIterator("Collecting Staticfiles");
        $.ajax({
            url: ajaxUrls.performStatic,
            dataType: ajaxDataType,
            success: function(data) {
                // The static file collection was successful. This does not mean that any
                // files were collected, but rather the command worked.
                if (data["status"] === "DONE") {
                    addStatusTableRow("Staticfiles", "GOOD", "success");
                }

                // A broad exception occurred while attempting to collect static files. We're gonna push
                // that into our errors and update the status table.
                if (data["status"] === "ERROR") {
                    _errorContainer.push(data);

                    // Update the status table to contain errored out static files.
                    // Error not displayed here, but stored and ready for use later.
                    addStatusTableRow("Staticfiles", "ERROR", "danger");
                }

                // Regardless of status, updating progress bar now.
                updateProgressBar(82);

                // Static files collection has finished, move on to the
                // dependency checking process.
                performDependencyCheck();
            }
        });
    };

    /**
     * Perform the dependency check process for the current titandash program.
     *
     * This handles any checks we can do for our dependencies to determine if
     * they're working or not.
     *
     * Many dependencies could be checked here, so our data should actually contain
     * a list of exceptions (if an error did occur).
     */
    let performDependencyCheck = function() {
        updateMessageIterator("Checking Dependencies");
        $.ajax({
            url: ajaxUrls.performDependency,
            dataType: ajaxDataType,
            success: function(data) {
                // The dependency check was successful (no errors).
                if (data["status"] === "DONE") {
                    addStatusTableRow("Dependencies", "GOOD", "success");
                }

                // Errors occurred while validating the dependencies, lets loop through
                // and add some exceptions from each to the container.
                if (data["status"] === "ERROR") {
                    // This error process is treated differently because there's a possibility
                    // that multiple exceptions could occur while checking out dependencies
                    $.each(data["exceptions"], function(index, value) {
                        _errorContainer.push(value);
                    });

                    // Update the status table to include a generic error text for
                    // some dependencies failing. The actual errors will be shown below.
                    addStatusTableRow("Dependencies", "ERROR", "danger");
                }

                updateProgressBar(100);
                killMessageIterator();
                errorCheck();
            }
        });
    };

    /**
     * Let's check to see if we have any errors that should be displayed.
     *
     * If we do, we will display them, and let users audit them, a button should be presented
     * that will let them continue to the dashboard.
     */
    let errorCheck = function() {
        setTimeout(function() {
            if (_errorContainer.length > 0) {
                $.each(_errorContainer, function(index, value) {
                    addExceptionToContainer(index, value);
                });

            // Otherwise, sending the user to the dashboard explicitly. If the user has
            // not signed in yet, the authentication middleware will handle our redirect.
            } else {
                setTimeout(function() {
                    $("body").fadeOut(1000, function () {
                        $(this).remove();
                        // SEND.s
                        window.location = "/";
                    });
                }, 1000);
            }
        }, 300);
    };

    /**
     * Add a row to the bootstrap table with the information provided.
     */
    let addStatusTableRow = function(title, status, cls) {
        let tableRow = $(`
            <tr style="display: none; border-bottom: 1px solid rgba(0, 0, 0, 0.1)">
                <td>${title}</td>
                <td style="text-align: right;" class="text-${cls}">${status}</td>
            </tr>
        `);

        // Add the new status row to the bootstrapping table.
        tableRow.appendTo(elements.bootstrapTable).fadeIn();
    };

    /**
     * Add an exception object to the exception container element.
     */
    let addExceptionToContainer = function(index, exception) {
        let error = $(`
            <div class="card text-white bg-danger mb-3" style="display: none;">
                <div class="card-header">${exception["title"]}</div>
                <div class="card-body">
                    <h5 class="card-title">${exception["type"]}</h5>
                    <p class="card-text">${exception["traceback"]}</p>
                </div>
            </div>
        `);

        // Add the exception to the bootstrap exception container.
        error.appendTo(elements.bootstrapExceptionContainer).fadeIn(index * 250);
        // Fade in the entire exceptions container once the last error is appended.
        if (_errorContainer.length === index + 1)
            elements.bootstrapExceptionContainer.fadeIn(200);
            elements.bootstrapContinue.fadeIn(300);
    };

    /**
     * Main entry point into bootstrapper.
     *
     * We use this main function to allow for the many different bootstrap
     * processes to take place sequentially. Many of them use a ajax call
     * to the web server, which means we must wait for the request to finish
     * before attempting to move onto the next bootstrap function.
     */
    let bootstrap = function() {
        // Enter into the update checker.
        // Moving onwards as needed (see function).
        setupUpdateButtons();
        checkUpdates();
    };

    // Begin the status message iterator. Loading for the
    // entire bootstrapping process.
    statusMessageIterator(3, 250);

    // ENTRY.
    bootstrap();
};