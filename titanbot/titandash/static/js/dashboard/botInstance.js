/**
 * botInstance.js
 *
 * Control all functionality related to the main BotInstance model in Django.
 */
let BotInstanceConsumer = function() {
    /* Base Variables */
    let initialAjaxUrl = "/ajax/bot_instance/get";
    let signalsAjaxUrl = "/ajax/signal";

    /* Consts */
    const PLAY = "PLAY";
    const PAUSE = "PAUSE";
    const STOP  = "STOP";
    const RUNNING = "RUNNING";
    const PAUSED = "PAUSED";
    const STOPPED = "STOPPED";
    const NA = "N/A";

    /* Stopwatch */
    let instanceStartedStopwatch = null;
    let lastPrestigeStopwatch = null;

    /* Active Instance */
    let activeInstance = getActiveInstance();

    /**
     * Main success function.
     *
     * Control all functionality related to the dynamic updating of the dashboard when a BotInstance
     * is modified (start, pause, stop).
     */
    this.success = function(data) {
        // Begin by checking what state the BotInstance is currently in...
        // A RUNNING/PAUSED State is representative of an "active" state.
        // While a STOPPED State is representative of an "inactive" state.
        let active = data["state"] === RUNNING || data["state"] === PAUSED;

        // All of our configuration functions will make use of our active boolean...
        // As well as the date provided by the BotInstance.

        // Instance Success.
        this.setupInstanceIcon(data);
        this.setupInstance(active, data);
        this.setupConfigChoice(active, data);
        this.setupWindowChoice(active, data);
        this.setupPrestige(active);
        this.setupQueued(active);
        this.setupCurrentFunction(active, data);
        // Last Prestige Success.
        this.setupLastPrestige(active, data);
        // Variables Success.
        this.setupInstanceLogVar(active, data);
        this.setupInstanceConfigVar(active, data);
        this.setupInstanceWindowVar(active, data);
        this.setupInstanceNextArtifactVar(active, data);
        this.setupInstanceCurrentStageVar(active, data);
        this.setupInstanceCountdownVars(active, data);
        this.setupInstanceGenericVars(active);
        // Actions Success.
        this.setupActions(data);
        // GameScreen Success.
        this.setupGameScreen(active);
    }.bind(this);

    /**
     * Configure and allocate all dashboard elements (jQuery).
     */
    this.configureDashboardElements = function() {
        return {
            /* Alerts */
            alertContainer: $("#alert-container"),

            /* Settings */
            dashboardSettingsHeader: $("#dashboardSettings"),
            dashboardSettingsBody: $("#dashboardSettingsBody"),
            dashboardSettingsLoader: $("#dashboardSettingsLoader"),
            dashboardSettingsContent: $("#dashboardSettingsContent"),

            /* BotInstance */
            instanceLoader: $("#dashboardBotLoader"),
            instanceStatusIcon: $("#dashboardBotStatusIcon"),
            instanceContent: $("#dashboardBotContent"),
            instanceName: $("#dashboardBotNameValue"),
            instanceState: $("#dashboardBotStateValue"),
            instanceSession: $("#dashboardBotSessionValue"),
            instanceStarted: $("#dashboardBotStartedValue"),
            instanceTimeRunningTd: $("#dashboardBotTimeRunningTd"),
            instanceTimeRunning: $("#dashboardBotTimeRunningValue"),
            instanceCurrentFunction: $("#dashboardBotCurrentFunctionValue"),

            /* Last Prestige */
            instanceLastPrestigeTimestamp: $("#dashboardBotLastPrestigeTimestampValue"),
            instanceLastPrestigeStage: $("#dashboardBotLastPrestigeStageValue"),
            instanceLastPrestigeDuration: $("#dashboardBotLastPrestigeDurationValue"),
            instanceLastPrestigeArtifact: $("#dashboardBotLastPrestigeArtifactValue"),

            /* BotInstance Variables */
            instanceVariablesTable: $("#dashboardBotCurrentVariablesTable"),
            instanceVariablesErrors: $("#dashboardBotErrorsValue"),
            instanceVariablesConfiguration: $("#dashboardBotConfigurationValue"),
            instanceVariablesWindow: $("#dashboardBotWindowValue"),
            instanceVariablesLogFile: $("#dashboardBotLogFileValue"),
            instanceVariablesCurrentStage: $("#dashboardBotCurrentStageValue"),
            instanceVariablesRaidAttackReset: $("#dashboardBotRaidAttackResetValue"),
            instanceVariablesNextBreak: $("#dashboardBotNextBreakValue"),
            instanceVariablesBreakResume: $("#dashboardBotBreakResumeValue"),
            instanceVariablesNextArtifactUpgrade: $("#dashboardBotNextArtifactUpgradeValue"),
            instanceVariablesNextMasterLevel: $("#dashboardBotNextMasterLevelValue"),
            instanceVariablesNextHeroesLevel: $("#dashboardBotNextHeroesLevelValue"),
            instanceVariablesNextSkillsLevel: $("#dashboardBotNextSkillsLevelValue"),
            instanceVariablesNextSkillsActivation: $("#dashboardBotNextSkillsActivationValue"),
            instanceVariablesNextMiscellaneousActions: $("#dashboardBotNextMiscellaneousActionsValue"),
            instanceVariablesNextPrestige: $("#dashboardBotNextPrestigeValue"),
            instanceVariablesNextRandomizedPrestige: $("#dashboardBotNextRandomizedPrestigeValue"),
            instanceVariablesNextStatsUpdate: $("#dashboardBotNextStatsUpdateValue"),
            instanceVariablesNextDailyAchievementCheck: $("#dashboardBotNextDailyAchievementCheckValue"),
            instanceVariablesNextMilestoneCheck: $("#dashboardBotNextMilestoneCheckValue"),
            instanceVariablesNextRaidNotificationsCheck: $("#dashboardBotNextRaidNotificationsCheckValue"),
            instanceVariablesNextClanResultsParse: $("#dashboardBotNextClanResultsParseValue"),
            instanceVariablesNextHeavenlyStrike: $("#dashboardBotNextHeavenlyStrikeValue"),
            instanceVariablesNextDeadlyStrike: $("#dashboardBotNextDeadlyStrikeValue"),
            instanceVariablesNextHandOfMidas: $("#dashboardBotNextHandOfMidasValue"),
            instanceVariablesNextFireSword: $("#dashboardBotNextFireSwordValue"),
            instanceVariablesNextWarCry: $("#dashboardBotNextWarCryValue"),
            instanceVariablesNextShadowClone: $("#dashboardBotNextShadowCloneValue"),

            /* Actions */
            actionsLoader: $("#dashboardActionsLoader"),
            actionsContent: $("#dashboardActionsContent"),
            actionsPlay: $("#dashboardActionsPlay"),
            actionsPause: $("#dashboardActionsPause"),
            actionsStop: $("#dashboardActionsStop"),

            /* Configuration */
            chooseConfig: $("#dashboardBotConfigurationSelect"),
            chooseWindow: $("#dashboardBotWindowSelect"),

            /* QueuedFunctions */
            queueInitial: $("#dashboardQueueInitial"),
            queueAccordion: $("#dashboardQueueAccordion"),
            queueHeaderBtn: $("#dashboardQueueHeaderBtn"),
            queueContent: $("#dashboardQueueContent"),
            queueFunctionsContainer: $("#dashboardQueueFunctionContainer"),
            queueCurrentTableBody: $("#dashboardQueueCurrentTableBody"),

            /* Prestiges */
            prestigeTableBody: $("#dashboardPrestigeTableBody"),
            prestigeAvgDuration: $("#dashboardPrestigeAvgDurationValue"),
            prestigeAvgStage: $("#dashboardPrestigeAvgStageValue"),
            prestigeThisSession: $("#dashboardPrestigeThisSessionValue"),
            prestigeLastArtifactValue: $("#dashboardPrestigeLastArtifactValue"),

            /* Game Screen */
            screenStop: $("#dashboardScreenStop"),
            screenStart: $("#dashboardScreenStart")
        }
    };
    /**
     * Configure and allocate the countdowns present when a BotInstance is active.
     */
    this.configureCountdowns = function() {
        return {
            raidAttackReset: [null, elements.instanceVariablesRaidAttackReset, "next_raid_attack_reset"],
            nextBreakCountdown: [null, elements.instanceVariablesNextBreak, "next_break"],
            breakResumeCountdown: [null, elements.instanceVariablesBreakResume, "resume_from_break"],
            nextMasterLevelCountdown: [null, elements.instanceVariablesNextMasterLevel, "next_master_level"],
            nextHeroesLevelCountdown: [null, elements.instanceVariablesNextHeroesLevel, "next_heroes_level"],
            nextSkillsLevelCountdown: [null, elements.instanceVariablesNextSkillsLevel, "next_skills_level"],
            nextSkillsActivationCountdown: [null, elements.instanceVariablesNextSkillsActivation, "next_skills_activation"],
            nextMiscellaneousActionsCountdown: [null, elements.instanceVariablesNextMiscellaneousActions, "next_miscellaneous_actions"],
            nextPrestigeCountdown: [null, elements.instanceVariablesNextPrestige, "next_prestige"],
            nextRandomizedPrestigeCountdown: [null, elements.instanceVariablesNextRandomizedPrestige, "next_randomized_prestige"],
            nextStatsUpdateCountdown: [null, elements.instanceVariablesNextStatsUpdate, "next_stats_update"],
            nextDailyAchievementCheckCountdown: [null, elements.instanceVariablesNextDailyAchievementCheck, "next_daily_achievement_check"],
            nextMilestoneCheckCountdown: [null, elements.instanceVariablesNextMilestoneCheck, "next_milestone_check"],
            nextRaidNotificationsCheckCountdown: [null, elements.instanceVariablesNextRaidNotificationsCheck, "next_raid_notifications_check"],
            nextClanResultsParseCountdown: [null, elements.instanceVariablesNextClanResultsParse, "next_clan_results_parse"],
            nextHeavenlyStrikeCountdown: [null, elements.instanceVariablesNextHeavenlyStrike, "next_heavenly_strike"],
            nextDeadlyStrikeCountdown: [null, elements.instanceVariablesNextDeadlyStrike, "next_deadly_strike"],
            nextHandOfMidasCountdown: [null, elements.instanceVariablesNextHandOfMidas, "next_hand_of_midas"],
            nextFireSwordCountdown: [null, elements.instanceVariablesNextFireSword, "next_fire_sword"],
            nextWarCryCountdown: [null, elements.instanceVariablesNextWarCry, "next_war_cry"],
            nextShadowCloneCountdown: [null, elements.instanceVariablesNextShadowClone, "next_shadow_clone"]
        }
    };

    /**
     * Configure an individual countdown, starting it if one does not already exist, or generating a new one
     * if a new datetime has been specified.
     */
    this.configureCountdown = function(key, countdownObj, data) {
        if (data["datetime"] !== null) {
            if (countdownObj[0] === null)
                countdownObj[0] = new Countdown(data["datetime"], null, countdownObj[1], "0");
            else {
                if (countdownObj[0].dateOrig !== data["datetime"]) {
                    countdownObj[0].destroy(); countdownObj[0] = null;
                    countdownObj[0] = new Countdown(data["datetime"], null, countdownObj[1], "0");
                }
            }
        } else {
            // Destroying null datetimes sent from web socket...
            // This will happen once a datetime is reset and is not expected
            // to be set again for a while.
            countdownObj[1].text("------");
            if (countdownObj[0] !== null) {
                countdownObj[0].destroy();
                countdownObj[0] = null;
            }
        }
    };

    /**
     * Modify the specified action element (play, pause, stop).
     *
     * We can either enable/disable it, which will modify the element and
     * disable it if it is needed.
     */
    this.modifyAction = function(action, enabled) {
        let cls = null;
        let elem = null;
        let color = null;

        switch (action) {
            case PLAY:
                cls = "fa-play";
                color = "text-success";
                elem = elements.actionsPlay;
                break;
            case PAUSE:
                cls = "fa-pause";
                color = "text-warning";
                elem = elements.actionsPause;
                break;
            case STOP:
                cls = "fa-stop";
                color = "text-danger";
                elem = elements.actionsStop;
                break;
        }

        cls = `fa fa-3x ${cls}`;
        if (enabled) {
            cls += ` ${color}`;
            elem.attr("class", cls).hover(function() {
                $(this).css("filter", "brightness(125%)");
            }, function() {
                $(this).css("filter", "brightness(100%)");
            }).off("click").click(function() {
                this.sendSignal(action);
                sendAlert(`${action} SIGNAL HAS BEEN SUCCESSFULLY SENT...`, elements.alertContainer);
            }.bind(this));
        } else {
            elem.off("hover");
            cls += " text-light";
            elem.attr("class", cls).off("click");
        }
    };

    /**
     * Setup Bot Settings to either allow modifying values or disabled when one is running.
     */
    this.setupWindowChoice = function(active, data) {
        elements.chooseWindow.attr("disabled", !!active);
        if (active)
            elements.chooseWindow.val(data["window"]["hwnd"]);
    };

    /* Active / Inactive Modification Functions */
    this.setupInstanceIcon = function(data) {
        switch (data["state"]) {
            case RUNNING:
                elements.instanceStatusIcon.attr("class", "float-right fa fa-check text-success");
                break;
            case PAUSED:
                elements.instanceStatusIcon.attr("class", "float-right fa fa-pause text-warning");
                break;
            case STOPPED:
                elements.instanceStatusIcon.attr("class", "float-right fa fa-times text-danger");
                break;
        }

        // Fading the icon in if it is currently hidden.
        if (elements.instanceStatusIcon.is(":hidden")) {
            elements.instanceStatusIcon.fadeIn(250);
        }
    };
    /**
     * Enable/Disable the configuration choice based on the active state.
     */
    this.setupConfigChoice = function(active, data) {
        elements.chooseConfig.attr("disabled", !!active);
        if (active)
            elements.chooseConfig.val(data["configuration"]["id"]);
    };
    /**
     * Resetting the prestige values if the active state is false.
     */
    this.setupPrestige = function(active) {
        if (!active) {
            elements.prestigeAvgDuration.fadeOut(100, function() {
                $(this).text("00:00:00").fadeIn(100);
            });
            elements.prestigeAvgStage.fadeOut(100, function() {
                $(this).text("0").fadeIn(100);
            });
            elements.prestigeThisSession.fadeOut(100, function() {
                $(this).text("0").fadeIn(100);
            });
            elements.prestigeLastArtifactValue.fadeOut(100, function() {
                $(this).text("------").fadeIn(100);
            });

            // Empty the table with all session prestiges.
            elements.prestigeTableBody.empty();
        }
    };
    /**
     * Displaying all queued functions at this point if the bot instance is active.
     * Otherwise, we will empty the queued functions tables and show the initial text.
     */
    this.setupQueued = function(active) {
        if (active) {
            elements.queueInitial.fadeOut(250, function() {
                let wait = 40;
                elements.queueContent.fadeIn(150);
                elements.queueFunctionsContainer.fadeIn(150).find("button").each(function() {
                    let btn = $(this);
                    wait += 20;
                    setTimeout(function() {
                        btn.prop("disabled", false).fadeIn(150);
                    }, wait)
                });
            });
        } else {
            elements.queueCurrentTableBody.empty();
            elements.queueContent.fadeOut(50);
            elements.queueFunctionsContainer.fadeOut(150).find("button").each(function() {
                $(this).prop("disabled", true).fadeOut(50);
            });
            elements.queueInitial.fadeIn(150);
        }
    };
    /**
     * Setup the instance data. This includes the generic instance variables.
     */
    this.setupInstance = function(active, data) {
        if (active) {
            if (elements.instanceName.text() !== data["name"])
                elements.instanceName.text(data["name"]);
            if (elements.instanceState.text() !== data["state"])
                elements.instanceState.text(data["state"]);
            if (elements.instanceSession.text() !== data["session"]["uuid"])
                elements.instanceSession.attr("href", data["session"]["url"]).text(data["session"]["uuid"]);
            if (elements.instanceStarted.data("datetime") !== data["started"]["datetime"]) {
                if (instanceStartedStopwatch !== null) {
                    if (instanceStartedStopwatch.dateOrig !== data["started"]["datetime"]) {
                        instanceStartedStopwatch.destroy();
                        instanceStartedStopwatch = null;
                        instanceStartedStopwatch = new Stopwatch(
                            data["started"]["datetime"],
                            data["started"]["formatted"],
                            elements.instanceStarted,
                            "0"
                        );
                    }
                } else {
                    instanceStartedStopwatch = new Stopwatch(
                        data["started"]["datetime"],
                        data["started"]["formatted"],
                        elements.instanceStarted,
                        "0"
                    );
                }
            } else {
                if (instanceStartedStopwatch === null)
                    instanceStartedStopwatch = new Stopwatch(
                        data["started"]["datetime"],
                        data["started"]["formatted"],
                        elements.instanceStarted,
                        "0"
                    );
            }
            if (elements.instanceContent.is(":visible"))
                elements.instanceContent.fadeIn(250);
        }
        else {
            elements.instanceName.text(NA);
            elements.instanceState.text(NA);
            elements.instanceStarted.text(NA);
            elements.instanceSession.attr("href", "#").text(NA);

            // BotInstance Stopwatch.
            if (instanceStartedStopwatch !== null)
                instanceStartedStopwatch.destroy();
        }
        // Always display the content once grabbed...
        if (!elements.instanceContent.is(":visible"))
            elements.instanceContent.fadeIn(250);
    };
    /**
     * Setup the current function displayed data.
     */
    this.setupCurrentFunction = function(active, data) {
        if (active) {
            if (data["current_function"]["function"] !== null) {
                elements.instanceCurrentFunction.closest("tr").animate({opacity: 1}, 200);
                if (elements.instanceCurrentFunction.text() !== data["current_function"]["title"])
                    elements.instanceCurrentFunction.text(data["current_function"]["title"]);
            } else
                elements.instanceCurrentFunction.closest("tr").animate({opacity: 0.4}, 200);
        }
        else {
            elements.instanceCurrentFunction.text(NA);
        }
    };

    /**
     * Setup the last prestige information.
     */
    this.setupLastPrestige = function(active, data) {
        if (active) {
            if (data["last_prestige"] === NA) {
                if (lastPrestigeStopwatch !== null) {
                    lastPrestigeStopwatch.destroy();
                    lastPrestigeStopwatch = null;
                    elements.instanceLastPrestigeTimestamp.text("N/A");
                }
                elements.instanceLastPrestigeStage.text("N/A");
                elements.instanceLastPrestigeDuration.text("N/A");
                elements.instanceLastPrestigeArtifact.text("N/A");
            } else {
                if (elements.instanceLastPrestigeTimestamp.data("datetime") !== data["last_prestige"]["timestamp"]["datetime"]) {
                    if (lastPrestigeStopwatch !== null) {
                        if (lastPrestigeStopwatch.dateOrig !== data["last_prestige"]["timestamp"]["datetime"]) {
                            lastPrestigeStopwatch.destroy();
                            lastPrestigeStopwatch = null;
                            lastPrestigeStopwatch = new Stopwatch(
                                data["last_prestige"]["timestamp"]["datetime"],
                                data["last_prestige"]["timestamp"]["formatted"],
                                elements.instanceLastPrestigeTimestamp,
                                "0"
                            );
                        }
                    } else {
                        lastPrestigeStopwatch = new Stopwatch(
                            data["last_prestige"]["timestamp"]["datetime"],
                            data["last_prestige"]["timestamp"]["formatted"],
                            elements.instanceLastPrestigeTimestamp,
                            "0"
                        );
                    }
                } else {
                    if (lastPrestigeStopwatch === null)
                        lastPrestigeStopwatch = new Stopwatch(
                            data["last_prestige"]["timestamp"]["datetime"],
                            data["last_prestige"]["timestamp"]["formatted"],
                            elements.instanceLastPrestigeTimestamp,
                            "0"
                        );
                }

                if (elements.instanceLastPrestigeStage.text() !== data["last_prestige"]["stage"])
                    elements.instanceLastPrestigeStage.text(data["last_prestige"]["stage"]);
                if (elements.instanceLastPrestigeDuration.text() !== data["last_prestige"]["duration"]["formatted"])
                    elements.instanceLastPrestigeDuration.text(data["last_prestige"]["duration"]["formatted"]);
                if (elements.instanceLastPrestigeArtifact.data("title") !== data["last_prestige"]["artifact"]["title"]) {
                    elements.instanceLastPrestigeArtifact
                        .data("title", data["last_prestige"]["artifact"]["title"])
                        .html(`
                            <strong>${data["last_prestige"]["artifact"]["title"]}</strong>
                            <img height="25" width="25" src="${data["last_prestige"]["artifact"]["path"]}" alt="${data["last_prestige"]["artifact"]["image"]}">
                        `)
                }
            }
        } else {
            if (lastPrestigeStopwatch !== null) {
                lastPrestigeStopwatch.destroy();
                lastPrestigeStopwatch = null;
                elements.instanceLastPrestigeTimestamp.text("N/A");
            }
            elements.instanceLastPrestigeStage.text("N/A");
            elements.instanceLastPrestigeDuration.text("N/A");
            elements.instanceLastPrestigeArtifact.text("N/A");
        }
    };

    /**
     * Setup the current log file displayed data.
     */
    this.setupInstanceLogVar = function(active, data) {
        if (active) {
            if (data["log_file"] === NA) {
                elements.instanceVariablesLogFile.attr("href", "#").text("------");
            } else {
                if (elements.instanceVariablesLogFile.attr("href") !== data["log_file"]) {
                    elements.instanceVariablesLogFile.attr("href", data["log_file"]).text("Link");
                }
            }
        }
    };
    /**
     * Setup the current config chosen displayed data.
     */
    this.setupInstanceConfigVar = function(active, data) {
        if (active) {
            if (elements.instanceVariablesConfiguration.text() !== data["configuration"]) {
                elements.instanceVariablesConfiguration.attr("href", data["configuration"]["url"])
                    .text(data["configuration"]["name"]);
                elements.chooseConfig.find("option").each(function() {
                    if ($(this).text() === elements.instanceVariablesConfiguration.text())
                        $(this).attr("selected", true);
                });
            }
        }
    };
    this.setupInstanceWindowVar = function(active, data) {
        if (active) {
            if (elements.instanceVariablesWindow.text() !== data["window"]["formatted"])
                elements.instanceVariablesWindow.text(data["window"]["formatted"]);
            elements.chooseWindow.find("option").each(function () {
                if ($(this).text() === elements.instanceVariablesWindow.text())
                    $(this).attr("selected", true);
            });
        }
    };
    /**
     * Setup the next artifact upgrade displayed data.
     */
    this.setupInstanceNextArtifactVar = function(active, data) {
        if (active) {
            if (data["next_artifact_upgrade"]["title"] !== null) {
                elements.instanceVariablesNextArtifactUpgrade.closest("tr").animate({opacity: 1}, 200);
                if (elements.instanceVariablesNextArtifactUpgrade.data("title") !== data["next_artifact_upgrade"]["title"]) {
                    elements.instanceVariablesNextArtifactUpgrade.fadeOut(150)
                        .data("title", data["next_artifact_upgrade"]["title"])
                        .html(`
                            <strong>${data["next_artifact_upgrade"]["title"]}</strong>
                            <img height="25" width="25" src="${data["next_artifact_upgrade"]["image"]}" alt="${data["next_artifact_upgrade"]["image"]}">
                        `)
                        .fadeIn(150);
                }
            } else {
                if (elements.instanceVariablesNextArtifactUpgrade.text() === "------")
                    elements.instanceVariablesNextArtifactUpgrade.closest("tr").animate({opacity: 0.4}, 200);
            }
        }
    };
    /**
     * Setup the current stage displayed data. Changing the color based on the difference
     * from the current max stage... As well as displaying the percent.
     */
    this.setupInstanceCurrentStageVar = function(active, data) {
        if (active) {
            if (data["current_stage"]["stage"] !== null) {
                elements.instanceVariablesCurrentStage.closest("tr").animate({opacity: 1}, 200);
                if (elements.instanceVariablesCurrentStage.data("stage") !== data["current_stage"]["stage"]) {
                    let diff = parseInt(data["current_stage"]["diff_from_max"]);
                    let stage = parseInt(data["current_stage"]["stage"]);
                    let pcnt = data["current_stage"]["percent_from_max"];

                    let cls = null;
                    let color = null;

                    if (diff > 0) {
                        color = "text-danger";
                        cls = "fa fa-minus fa-instance";
                    } else {
                        color = "text-success";
                        cls = "fa fa-plus fa-instance";
                    }

                    if (diff === 0) {
                        color = "text-dark";
                        cls = "";
                    }
                    if (diff < 0)
                        diff = -diff;

                    elements.instanceVariablesCurrentStage.data("stage", data["current_stage"]["stage"])
                        .fadeOut(250, function() {
                            if (cls === "") {
                                elements.instanceVariablesCurrentStage.html(`
                                    ${stage}
                                    (<small class="${color}"><strong>${diff}</strong></small>)
                                    (<small class="${color}">${pcnt}</small>)
                                `).fadeIn(150);
                            } else {
                                elements.instanceVariablesCurrentStage.html(`
                                    ${stage}
                                    (<span class="${color} ${cls}"></span>
                                    <small class="${color}"><strong>${diff}</strong></small>)
                                    (<small class="${color}">${pcnt}</small>)
                                `).fadeIn(150);
                            }
                        })
                }
            } else {
                if (elements.instanceVariablesCurrentStage.text() === "------")
                    elements.instanceVariablesCurrentStage.closest("tr").animate({opacity: 0.4}, 200);
            }
        }
    };
    /**
     * Setup all countdowns present on the bot instance variables.
     */
    this.setupInstanceCountdownVars = function(active, data) {
        if (active) {
            for (let cd in countdowns) {
                let obj = countdowns[cd];
                this.configureCountdown(
                    cd,
                    obj,
                    data[obj[2]]
                );

                if (obj[0] === null)
                    obj[1].closest("tr").animate({opacity: 0.4}, 200);
                else
                    obj[1].closest("tr").animate({opacity: 1.0}, 200);
            }
        }
    };
    /**
     * Showing variables content if it is hidden, and resetting fields if required.
     */
    this.setupInstanceGenericVars = function(active) {
        if (active) {
            if (!elements.instanceVariablesTable.is(":visible"))
                elements.instanceVariablesTable.fadeIn(250);
        } else {
            elements.instanceVariablesTable.find(".varsItem").each(function() {
                $(this).text("------");
            });
            elements.instanceVariablesTable.fadeOut(250);
        }
    };

    /**
     * Setup and modify action elements based on current data state.
     */
    this.setupActions = function(data) {
        elements.actionsLoader.fadeOut(250, function() {
            $(this).remove();
        });

        switch (data["state"]) {
            case RUNNING:
                this.modifyAction(PLAY, false);
                this.modifyAction(PAUSE, true);
                this.modifyAction(STOP, true);
                break;
            case PAUSED:
                this.modifyAction(PLAY, true);
                this.modifyAction(PAUSE, false);
                this.modifyAction(STOP, false);
                break;
            case STOPPED:
                this.modifyAction(PLAY, true);
                this.modifyAction(PAUSE, false);
                this.modifyAction(STOP, false);
                break;
        }

        if (!elements.actionsContent.is(":visible"))
            elements.actionsContent.fadeIn(250);
    };

    /**
     * Setup the game screen to be enabled or disabled based on current BotInstance status.
     */
    this.setupGameScreen = function(active) {
        if (active) {
            elements.screenStart.prop("disabled", false);
            elements.screenStop.prop("disabled", false);
        } else {
            elements.screenStart.prop("disabled", true);
            elements.screenStop.prop("disabled", true);
        }
    };

    /**
     * Sending a signal to the BotInstance. One of either ("start", "pause", "stop").
     */
    this.sendSignal = function(signal) {
        let data = {signal: signal, instance: getActiveInstance()};
        if (signal === PLAY) {
            data["config"] = elements.chooseConfig.find(":selected").val();
            data["window"] = elements.chooseWindow.find(":selected").val();
        }

        $.ajax({
            url: signalsAjaxUrl,
            dataType: "json",
            data: data
        });
    };

    /**
     * Generate a WebSocket that will be used to update the BotInstance in the dashboard in real time.
     */
    this.generateWebSocket = function() {
        let socket = new WebSocket(`ws://${window.location.host}/ws/instance/`);
        socket.onmessage = function(e) {
            let message = JSON.parse(e.data);
            if (message["instance"]["instance_id"] === getActiveInstance()) {
                this.success(message["instance"]["instance"])
            }
        }.bind(this);
        socket.onclose = function() {
            console.warn("BotInstance WebSocket Closed...")
        };
        console.log("BotInstance WebSocket Started Now...");
    };

    /* Consumer Elements */
    let elements = this.configureDashboardElements();
    /* BotInstance Variable Countdowns */
    let countdowns = this.configureCountdowns();

    // Setting a timeout to retrieve the initial BotInstance...
    setTimeout(function() {
        $.ajax({
            url: initialAjaxUrl,
            dataType: "json",
            data: {instance: getActiveInstance()},
            success: this.success,
            complete: function() {
                elements.instanceLoader.fadeOut(250, function() {
                    $(this).remove();
                });
                this.generateWebSocket();
            }.bind(this)
        });
    }.bind(this), 400);

    // When the active bot instance is changed, we should perform another bot instance
    // successful function so that the information is updated.
    setInterval(function() {
        if (getActiveInstance() !== activeInstance) {
            activeInstance = getActiveInstance();
            $.ajax({
                url: initialAjaxUrl,
                dataType: "json",
                data: {instance: activeInstance},
                success: this.success,
            });
        }
    }.bind(this), 100);
};