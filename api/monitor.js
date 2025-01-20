const express = require('express');
const router = express.Router();
const { checkHealth, checkDiskSpace } = require('../services/cleanup');
const logger = require('../utils/logger');

// Get scheduler status and statistics
router.get('/stats', async (req, res) => {
  try {
    const metrics = await checkHealth();
    const diskUsage = await checkDiskSpace();
    const schedulerStats = {
      uptime: process.uptime(),
      lastCleanup: global.lastCleanupTime || null,
      recordsArchived: global.totalRecordsArchived || 0,
      nextScheduledRun: getNextScheduledRun(),
      metrics,
      diskUsage
    };
    
    res.json(schedulerStats);
  } catch (error) {
    logger.error('Failed to get scheduler stats:', error);
    res.status(500).json({ error: 'Failed to get scheduler statistics' });
  }
});

// Get recent cleanup history
router.get('/history', async (req, res) => {
  try {
    const history = await getCleanupHistory();
    res.json(history);
  } catch (error) {
    logger.error('Failed to get cleanup history:', error);
    res.status(500).json({ error: 'Failed to get cleanup history' });
  }
});

module.exports = router; 