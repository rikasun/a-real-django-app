const express = require('express');
const router = express.Router();
const { checkHealth, checkDiskSpace } = require('../services/cleanup');
const { requirePermission } = require('../auth/roleMiddleware');
const { PERMISSIONS } = require('../config/roles');
const logger = require('../utils/logger');

// Get dashboard overview data
router.get('/overview', 
  requirePermission(PERMISSIONS.VIEW_SCHEDULER),
  async (req, res) => {
    try {
      const metrics = await checkHealth();
      const diskUsage = await checkDiskSpace();
      const cleanupHistory = await getCleanupHistory();
      
      // Calculate success rate
      const recentCleanups = cleanupHistory.slice(-10);
      const successRate = (recentCleanups.filter(c => c.success).length / recentCleanups.length) * 100;

      const overview = {
        systemHealth: {
          status: metrics.cpu_percent < 80 ? 'healthy' : 'stressed',
          metrics,
          diskUsage
        },
        cleanupStats: {
          totalRecords: global.totalRecordsArchived || 0,
          lastRunStatus: recentCleanups[0]?.success ? 'success' : 'failed',
          successRate,
          nextScheduledRun: getNextScheduledRun()
        },
        alerts: await getActiveAlerts(),
        recentActivity: recentCleanups
      };

      res.json(overview);
    } catch (error) {
      logger.error('Failed to get dashboard overview:', error);
      res.status(500).json({ error: 'Failed to get dashboard data' });
    }
});

// Get performance metrics
router.get('/performance', 
  requirePermission(PERMISSIONS.VIEW_LOGS),
  async (req, res) => {
    try {
      const timeRange = req.query.range || '24h';
      const metrics = await getPerformanceMetrics(timeRange);
      res.json(metrics);
    } catch (error) {
      logger.error('Failed to get performance metrics:', error);
      res.status(500).json({ error: 'Failed to get performance data' });
    }
});

// Get active alerts
router.get('/alerts',
  requirePermission(PERMISSIONS.VIEW_LOGS),
  async (req, res) => {
    try {
      const alerts = await getActiveAlerts();
      res.json(alerts);
    } catch (error) {
      logger.error('Failed to get alerts:', error);
      res.status(500).json({ error: 'Failed to get alerts' });
    }
});

module.exports = router; 