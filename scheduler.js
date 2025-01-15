const cron = require('node-cron');
const { cleanupOldRecords, sendSummaryReport } = require('./services/cleanup');

// Daily cleanup at 2 AM
cron.schedule('0 2 * * *', async () => {
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

// Weekly deep cleanup on Sundays at 3 AM
cron.schedule('0 3 * * 0', async () => {
  // ... deep cleanup logic ...
}); 