/**
 * SimulationEnsemble.js
 * Removes all seeded data for this project.
 */
function removeAllSeededData() {
    SimulationEnsemble.removeAll();
    SimulationSample.removeAll();
    SimulationModelParameters.removeAll();
    SimulationOutputFile.removeAll();
    SimulationModelOutput.removeAll();
    SimulationModelOutputSeries.removeAll();

    return 0;
}