/**
 * configuration.js
 *
 * Control all functionality related to the addition of new, and modification of existing
 * configurations by initializing our data tables where needed. As well as controlling the
 * validation that's performed.
 *
 * We use the same javascript file for saving/adding new configurations.
 *
 * Saving will use it's own button which sends a post with all the ids and their
 * associated values, while adding a new configuration does the same but creates a new configuration.
 */
$(document).ready(function() {
    return new ConfigurationController();
});

/**
 * Main configuration controller to provide functionality to the configuration page.
 */
let ConfigurationController = function() {
    let ajaxUrls = {
        save: "/configurations/save/"
    };
    let ajaxDataType = "json";

    /**
     * Configure and allocate all configuration elements needed (jQuery).
     */
    let configureConfigurationElements = function() {
        return {
            /* Collapse/Expand */
            collapseAll: $("#collapseAll"),
            expandAll: $("#expandAll"),
            /* Alert Container */
            alertContainer: $("#alert-container"),
            /* Form */
            form: $("#configurationForm"),
            /* Artifact Action Settings */
            upgrade_owned_tier: $("#upgrade_owned_tier"),
            upgrade_artifacts: $("#upgrade_artifacts"),
            ignore_artifacts: $("#ignore_artifacts"),
            /* Select Elements */
            emulator: $("#emulator"),
            use_perk_on_prestige: $("#use_perk_on_prestige"),
            /* Action Level Caps */
            level_heavenly_strike_cap: $("#level_heavenly_strike_cap"),
            level_deadly_strike_cap: $("#level_deadly_strike_cap"),
            level_hand_of_midas_cap: $("#level_hand_of_midas_cap"),
            level_fire_sword_cap: $("#level_fire_sword_cap"),
            level_war_cry_cap: $("#level_war_cry_cap"),
            level_shadow_clone_cap: $("#level_shadow_clone_cap"),
        }
    };

    /**
     * Configure and allocate all required configuration form elements (jQuery).
     */
    let configurationRequiredElements = function() {
        return {
            /* Generic */
            name: $("#name"),
            /* Runtime */
            post_action_min_wait_time: $("#post_action_min_wait_time"),
            post_action_max_wait_time: $("#post_action_max_wait_time"),
            /* Generic Settings */
            tapping_repeat: $("#tapping_repeat"),
            /* Minigames */
            minigames_repeat: $("#minigames_repeat"),
            /* Breaks */
            breaks_jitter: $("#breaks_jitter"),
            breaks_minutes_required: $("#breaks_minutes_required"),
            breaks_minutes_max: $("#breaks_minutes_max"),
            breaks_minutes_min: $("#breaks_minutes_min"),
            /* Daily Achievements */
            daily_achievement_check_every_x_hours: $("#daily_achievements_check_every_x_hours"),
            /* Milestones */
            milestones_check_every_x_hours: $("#milestones_check_every_x_hours"),
            /* Raid Notifications */
            raid_notifications_check_every_x_minutes: $("#raid_notifications_check_every_x_minutes"),
            /* Master */
            master_level_every_x_seconds: $("#master_level_every_x_seconds"),
            master_level_intensity: $("#master_level_intensity"),
            /* Heroes */
            hero_level_every_x_seconds: $("#hero_level_every_x_seconds"),
            hero_level_intensity: $("#hero_level_intensity"),
            /* Level Skills */
            level_skills_every_x_seconds: $("#level_skills_every_x_seconds"),
            /* Activate Skills */
            activate_skills_every_x_seconds: $("#activate_skills_every_x_seconds"),
            interval_heavenly_strike: $("#interval_heavenly_strike"),
            interval_deadly_strike: $("#interval_deadly_strike"),
            interval_hand_of_midas: $("#interval_hand_of_midas"),
            interval_fire_sword: $("#interval_fire_sword"),
            interval_war_cry: $("#interval_war_cry"),
            interval_shadow_clone: $("#interval_shadow_clone"),
            /* Perks */
            use_perks_every_x_hours: $("#use_perks_every_x_hours"),
            /* Prestige */
            prestige_x_minutes: $("#prestige_x_minutes"),
            prestige_at_stage: $("#prestige_at_stage"),
            prestige_at_max_stage_percent: $("#prestige_at_max_stage_percent"),
            /* Stats */
            update_stats_every_x_minutes: $("#update_stats_every_x_minutes"),
        }
    };

    /* Derive Save/Add Button */
    let saveButton = $("#saveConfigurationButton");

    /* Controller elements */
    let elements = configureConfigurationElements();
    let tables = {};
    let required = configurationRequiredElements();


    /**
     * Overriding original serialize functionality to include checkboxes unchecked so that true/false
     * is sent into our views.
     */
    let originalSerializeArray = $.fn.serializeArray;
    $.fn.extend({
        serializeArray: function() {
            let brokenSerialization = originalSerializeArray.apply(this);
            let checkboxValues = $(this).find("input[type=checkbox]").map(function() {
                return {name: this.name, value: this.checked};
            }).get();

            let checkboxKeys = $.map(checkboxValues, function(element) {
                return element.name;
            });
            let withoutCheckboxes = $.grep(brokenSerialization, function(element) {
                return $.inArray(element.name, checkboxKeys) === -1;
            });

            return $.merge(withoutCheckboxes, checkboxValues)
        }
    });

    /**
     * Serialize the configuration form to retrieve all of our required values.
     *
     * 1. Base form values with a "name" attribute.
     * 2. Datatables selected values from checkboxes.
     * 3. Select box values without a "name" attribute (some of them need different values in database).
     */
    let serializeConfigurationForm = function() {
        // Regardless of save/add, we are using the same form...
        // Grabbing all elements used.
        let serialized = elements.form.serializeArray();

        // Removing some of the serialized elements that come from our
        // datatables.
        serialized = $.grep(serialized, function(e) {
            return ["upgrade_owned_tier_length", "upgrade_artifacts_length", "ignore_artifacts_length"].indexOf(e.name) === -1
        });

        // Some of our custom elements need to be grabbed to retrieve the active elements.
        // Datatables are one of these, as well as some of our select elements that use
        // specific data-value attributes for the db.
        let m2m = {
            upgrade_owned_tier: [],
            upgrade_artifacts: [],
            ignore_artifacts: []
        };

        $.each(tables, function(index, value) {
            value.rows().every(function() {
                if ($(this.node()).find("input").is(":checked")) {
                    m2m[index].push($(this.node()).data("key"))
                }
            });
        });

        // Grabbing the select box values.
        serialized.push({name: "emulator", value: elements.emulator.find(":selected").data("value")});
        serialized.push({name: "use_perk_on_prestige", value: elements.use_perk_on_prestige.find(":selected").data("value")});
        // Action level caps.
        serialized.push({name: "level_heavenly_strike_cap", value: elements.level_heavenly_strike_cap.find(":selected").data("value")});
        serialized.push({name: "level_deadly_strike_cap", value: elements.level_deadly_strike_cap.find(":selected").data("value")});
        serialized.push({name: "level_hand_of_midas_cap", value: elements.level_hand_of_midas_cap.find(":selected").data("value")});
        serialized.push({name: "level_fire_sword_cap", value: elements.level_fire_sword_cap.find(":selected").data("value")});
        serialized.push({name: "level_war_cry_cap", value: elements.level_war_cry_cap.find(":selected").data("value")});
        serialized.push({name: "level_shadow_clone_cap", value: elements.level_shadow_clone_cap.find(":selected").data("value")});

        serialized.push({name: "upgrade_owned_tier", value: m2m.upgrade_owned_tier});
        serialized.push({name: "upgrade_artifacts", value: m2m.upgrade_artifacts});
        serialized.push({name: "ignore_artifacts", value: m2m.ignore_artifacts});

        // Flag to determine if we are saving, or adding a new configuration.
        serialized.push({name: "key", value: saveButton.data("pk")});

        return serialized;
    };

    /**
     * Setting Up The Configuration Save Listener.
     *
     * If we are adding a new configuration, a flag is set to determine that, and our ajax function
     * will not send over a primary key, this created a new configuration instance.
     */
    saveButton.off("click").on("click", function() {
        let valid = true;
        // Final validation check in case user hasn't filled out a required field.
        $.each(required, function (index, value) {
            if (value.val() === "" || !value.val()) {
                // INVALID.
                generateInvalidAlert(value);
                valid = false;
            } else {
                // VALID.
                removeInvalidAlert(value);
            }
        });

        if (valid) {
            // Send AJAX request to save the current configuration.
            $.ajax({
                url: ajaxUrls.save,
                dataType: ajaxDataType,
                type: "post",
                data: serializeConfigurationForm(),
                beforeSend: function () {
                    saveButton.prop("disabled", true);
                },
                complete: function () {
                    saveButton.prop("disabled", false);
                },
                success: function (data) {
                    if (data["status"] === "success") {
                        window.location = "/configurations";
                    }
                    if (data["status"] === "error") {
                        sendAlert(data["message"], elements.alertContainer);
                    }
                }
            });
        } else {
            sendAlert("Some errors are present on the configuration, please fix them before saving.", elements.alertContainer, null, "danger");
        }
    });

    /**
     * Generate An Invalid Alert.
     *
     * The specified jQuery value is used to generate it in the correct location.
     */
    let generateInvalidAlert = function(value) {
        if ($(value).closest("div.form-group").find(".configFormError").length > 0)
            return;

        // No alert is present, let's add one and display it.
        let alert = $(`
            <div style="display: none;" class="alert alert-danger configFormError" role="alert">
                This value is required.
            </div>
        `);

        $(value).closest("div.form-group").find(".text-muted").css({"margin-bottom": 0});
        alert.appendTo($(value).closest("div.form-group")).fadeIn(200);

        if (elements.form.find(".configFormError").length > 0)
            saveButton.prop("disabled", true);
        else
            saveButton.prop("disabled", false);
    };

    let removeInvalidAlert = function(value) {
        $(value).closest("div.form-group").find(".configFormError").data("removing", true).fadeOut(200, function() {
            $(this).remove();
            $(value).closest("div.form-group").find(".text-muted").css({"margin-bottom": "1rem"});

            if (elements.form.find(".configFormError").length > 0)
                saveButton.prop("disabled", true);
            else
                saveButton.prop("disabled", false);
        })
    };

    /**
     * Perform Validation Of Form Elements...
     *
     * Most values can actually be left as is. But some of our values must be set to a value.
     * Otherwise, we should prevent the user from saving.
     *
     * The easiest way to handle this at the moment is to use the keyup functionality on our char fields.
     *
     * These are the only ones that could have invalid values in them. If that's the case, we'll check
     * the value being keyed up on... And validating that the user has set it to a value other than "".
     */
    $.each(required, function(index, value) {
        // Setup Keyup.
        value.off("focusout").on("focusout", function() {
            // Is the value valid currently?
            if (value.val() === "" || !value.val()) {
                // INVALID.
                generateInvalidAlert(value);
            } else {
                // VALID.
                removeInvalidAlert(value);
            }
        });
    });

    /**
     * Configure specific datatables with the given settings.
     *
     * We are also appending the table to our list of datatable elements.
     */
    let setupDatatables = function(elements, checkboxSelector, tableSettings) {
        $.each(elements, function(index, value) {
            // Grab table container element.
            let table = $(`#${value}`);

            // Append initialized datatable to our array
            // of datatables, this is done so we can access it later on.
            tables[value] = table.DataTable(tableSettings);

            // Setup checkbox listeners.
            table.off("click", "tr").on("click", "tr", function(e) {
                if ($(e.target).attr("id") !== checkboxSelector)
                    $(this).find("input[type=checkbox]").prop("checked", !$(this).find("input[type=checkbox]").prop("checked"));
            });
        });
    };

    let collapseSetup = function(collapse) {
        $.each($("[id^=collapse].collapse"), function(index, value) {
            if (collapse) {
                if ($(value).hasClass("show")) {
                    // Perform click on header.
                    $(value).parent().parent().find("button").click()
                }
            } else {
                if (!$(value).hasClass("show")) {
                    // Perform click on header.
                    $(value).parent().parent().find("button").click()
                }
            }
        });
    };

    /**
     * Setup Expand/Collapse All Functionality.
     */
    elements.expandAll.off("click").on("click", function() {
        collapseSetup(false);
    });
    elements.collapseAll.off("click").on("click", function() {
        collapseSetup(true);
    });

    /**
     * Include custom sorting for use with checkboxes.
     */
    $.fn.dataTable.ext.order['dom-checkbox'] = function (settings, col) {
        return this.api().column(col, {order:'index'}).nodes().map(function (td) {
            return $('input', td).prop('checked') ? '1' : '0';
        });
    };

    /* Setup Tier Datatable Elements */
    setupDatatables(["upgrade_owned_tier"], "tierSelect", {
        columnDefs: [
            {targets: [0], orderDataType: "dom-checkbox"},
        ],
        responsive: true,
        pageLength: 10,
        order: [[0, "desc"]]
    });

    /* Setup Artifact Datatable Elements */
    setupDatatables(["upgrade_artifacts", "ignore_artifacts"], "artifactSelect", {
        columnDefs: [
            {targets: [0], orderDataType: "dom-checkbox"},
            {orderable: false, targets: 1}
        ],
        responsive: true,
        pageLength: 10,
        order: [[0, "desc"]]
    });
    required.name.focus();
};