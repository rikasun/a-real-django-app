const cron = require('node-cron');
const { cleanupOldRecords, sendSummaryReport } = require('./services/cleanup');
const winston = require('winston');
const { format } = require('date-fns');
const nodemailer = require('nodemailer');
const fs = require('fs').promises;
const diskusage = require('disk-space');

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

// Add after the health check function
const DISK_THRESHOLD = 85; // Trigger emergency cleanup when disk usage > 85%

async function checkDiskSpace() {
  try {
    const disk = await new Promise((resolve, reject) => {
      diskusage.check('/', (err, info) => {
        if (err) reject(err);
        else resolve(info);
      });
    });

    const usagePercent = (disk.used / disk.total) * 100;
    logger.info(`Current disk usage: ${usagePercent.toFixed(2)}%`);

    if (usagePercent > DISK_THRESHOLD) {
      logger.warn(`Disk usage critical (${usagePercent.toFixed(2)}%), initiating emergency cleanup`);
      
      // Perform aggressive cleanup
      await emergencyCleanup();
    }
  } catch (error) {
    logger.error('Disk space check failed:', error);
  }
}

async function emergencyCleanup() {
  try {
    // Cleanup temporary files first
    await cleanupTempFiles();
    
    // Aggressive database cleanup - shorter retention period
    const archivedCount = await cleanupOldRecords(7, { 
      aggressive: true,
      skipBackup: true 
    });

    // Clear logs older than 2 days
    const logsPath = './logs';
    const files = await fs.readdir(logsPath);
    const twoDaysAgo = Date.now() - (2 * 24 * 60 * 60 * 1000);

    for (const file of files) {
      const filePath = `${logsPath}/${file}`;
      const stats = await fs.stat(filePath);
      if (stats.mtime.getTime() < twoDaysAgo) {
        await fs.unlink(filePath);
        logger.info(`Removed old log file: ${file}`);
      }
    }

    // Send emergency notification
    await mailer.sendMail({
      from: process.env.ALERT_FROM,
      to: process.env.ALERT_TO,
      subject: 'Emergency Cleanup Performed',
      text: `Emergency cleanup completed:\n` +
            `- Archived ${archivedCount} records\n` +
            `- Cleaned up temporary files\n` +
            `- Removed old log files\n` +
            `Current disk usage: ${(await checkDiskSpace()).usagePercent.toFixed(2)}%`
    });

  } catch (error) {
    logger.error('Emergency cleanup failed:', error);
  }
}

// Add disk space monitoring (every 15 minutes)
cron.schedule('*/15 * * * *', checkDiskSpace); 