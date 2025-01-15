const cron = require('node-cron');
const { cleanupOldRecords, sendSummaryReport } = require('./services/cleanup');

// Run cleanup job every day at midnight
cron.schedule('0 0 * * *', async () => {
  console.log(`Starting daily cleanup job at ${new Date().toISOString()}`);
  
  try {
    // Archive records older than 30 days
    const archivedCount = await cleanupOldRecords(30);
    
    // Send summary report to admin
    await sendSummaryReport({
      jobType: 'Daily Cleanup',
      archivedRecords: archivedCount,
      timestamp: new Date()
    });

    console.log(`Cleanup job completed. Archived ${archivedCount} records.`);
  } catch (error) {
    console.error('Cleanup job failed:', error);
  }
}); 