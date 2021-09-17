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
        var batchSpec = StressTestBatch.make({values: batch});
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
        stressTest.compute_pi(options.computePi_n);
    }
    batch.values.foreach(runStressTest);
 }