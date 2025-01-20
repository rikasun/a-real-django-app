const cron = require('node-cron');
const { cleanupOldRecords, sendSummaryReport } = require('./services/cleanup');
const winston = require('winston');
const { format } = require('date-fns');
const nodemailer = require('nodemailer');

// Configure logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// Configure email
const mailer = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: process.env.SMTP_PORT,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS
  }
});

// Health check function
const checkHealth = async () => {
  const metrics = {
    timestamp: new Date(),
    memory: process.memoryUsage(),
    uptime: process.uptime()
  };
  logger.info('Health check', metrics);
  return metrics;
};

// Daily cleanup at 2 AM
cron.schedule('0 2 * * *', async () => {
  logger.info(`Starting daily cleanup job at ${format(new Date(), 'yyyy-MM-dd HH:mm:ss')}`);
  
  try {
    // Archive records older than 30 days
    const archivedCount = await cleanupOldRecords(30);
    
    // Send summary report to admin
    await sendSummaryReport({
      jobType: 'Daily Cleanup',
      archivedCount,
      timestamp: new Date(),
      metrics: await checkHealth()
    });

    logger.info(`Cleanup job completed. Archived ${archivedCount} records.`);
  } catch (error) {
    logger.error('Cleanup job failed:', error);
    
    // Send alert email
    await mailer.sendMail({
      from: process.env.ALERT_FROM,
      to: process.env.ALERT_TO,
      subject: 'Cleanup Job Failed',
      text: `Error: ${error.message}\n\nStack: ${error.stack}`
    });
  }
});

// Weekly deep cleanup on Sundays at 3 AM
cron.schedule('0 3 * * 0', async () => {
  logger.info('Starting weekly deep cleanup');
  try {
    // Perform database optimization
    await cleanupOldRecords(90, { optimize: true });
    
    // Clean up temporary files
    await cleanupTempFiles();
    
    // Generate weekly statistics
    const stats = await generateWeeklyStats();
    await sendSummaryReport({
      jobType: 'Weekly Deep Cleanup',
      stats,
      timestamp: new Date()
    });
  } catch (error) {
    logger.error('Weekly cleanup failed:', error);
  }
});

// Health check every hour
cron.schedule('0 * * * *', checkHealth); 