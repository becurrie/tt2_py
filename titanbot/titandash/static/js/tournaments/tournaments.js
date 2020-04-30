/**
 * tournaments.js
 */
$(document).ready(function() {
    let ajaxTournamentsUrl = "/tournaments";
    let instanceSelector = $("#tournamentsInstanceSelect");
    let tournamentsCardBody = $("#tournamentsCardBody");
    let loaderClass = ".loader-template";
    let tournamentsJsonBtn = $("#exportTournamentsJson");

    function reloadDataTable() {
        $("#tournamentsTable").DataTable({
            responsive: true,
            order: [[1, "desc"]],
        });
    }

    // Perform ajax request whenever the instance selector has the current
    // instance modified. Grabbing all tournaments for the selected instance.
    instanceSelector.off("change").change(function() {
        $.ajax({
            url: ajaxTournamentsUrl,
            dataType: "json",
            data: {
                instance: $(this).val(),  // Instance PK.
                context: true             // Contextual Flag.
            },
            beforeSend: function() {
                tournamentsCardBody.empty().append(loaderTemplate);
                $(loaderClass).fadeIn();
            },
            success: function(data) {
                tournamentsCardBody.find(loaderClass).fadeOut(100, function() {
                    $(this).remove();
                    tournamentsCardBody.empty().append(data["table"]);
                    reloadDataTable();
                });
            }
        });
    });

    // Generate the initial data table that should be present
    // before any instance changes take place.
    reloadDataTable();

    // Setup the exporting of tournaments data through our generic
    // json exporter utility.
    tournamentsJsonBtn.off("click").click(function() {
        exportToJsonFile($("#jsonData").data("json"), "tournaments");
    });
});