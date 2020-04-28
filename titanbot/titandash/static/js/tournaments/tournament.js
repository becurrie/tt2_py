/**
 * tournament.js
 */
$(document).ready(function() {
    // Initialize elements used here on the main tournament view.
    let tournamentJsonBtn = $("#exportTournamentJson");
    let tournamentIdentifier = $("#tournamentIdentifierValue");

    // Setup the exporting of tournament data through our generic
    // json exporter utility.
    tournamentJsonBtn.off("click").click(function() {
        exportToJsonFile($("#jsonData").data("json"), tournamentIdentifier.text());
    });
});
