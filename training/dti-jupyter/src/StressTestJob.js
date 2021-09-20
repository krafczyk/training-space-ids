// StressTestJob.js

/**
 * 
 * @param {StressTestJob} job 
 * @param {StressTestJobOptions} options 
 */
 function doStart(job, options) {

    const chunk = (arr, size) => arr.reduce((acc, e, i) => (i % size ? acc[acc.length - 1].push(e) : acc.push([e]), acc), []);

    // Schedule a batch of jobs
    function scheduleBatch(batch) {
        var batchSpec = StressTestJobBatch.make({values: batch});
        job.scheduleBatch(batchSpec);
     }

    var jobs = [];
    // Make an array of Stress Tests
    for (var i = 0; i < options.numJobs; i++) {
        jobs.push(StressTest.make());
    }

    // Split the array into chunks and schedule each batch
    var batches = chunk(jobs, options.batchSize);
    batches.forEach(scheduleBatch);

 }

/**
 * @param {StressTestJobBatch} options  
 * @param {StressTestJob} job 
 * @param {StressTestJobOptions} options 
 * 
 */
 function processBatch(batch, job, options) {
    function runStressTest(stressTest){
        StressTest.compute_pi(options.computePi_n);
    }
    batch.values.forEach(runStressTest);
 }