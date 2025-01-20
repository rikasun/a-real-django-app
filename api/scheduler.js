const express = require('express');
const router = express.Router();
const authMiddleware = require('../auth/authMiddleware');
const { cleanupOldRecords, checkDiskSpace } = require('../services/cleanup');
const logger = require('../utils/logger');
const { requirePermission } = require('../auth/roleMiddleware');
const { PERMISSIONS } = require('../config/roles');

// Protect all routes
router.use(authMiddleware);

// Get scheduler status (requires VIEW_SCHEDULER permission)
router.get('/status', 
  requirePermission(PERMISSIONS.VIEW_SCHEDULER),
  async (req, res) => {
    try {
      const metrics = await checkHealth();
      const diskUsage = await checkDiskSpace();
      res.json({ metrics, diskUsage });
    } catch (error) {
      logger.error('Failed to get status:', error);
      res.status(500).json({ error: 'Failed to get scheduler status' });
    }
  });

// Trigger manual cleanup (requires TRIGGER_CLEANUP permission)
router.post('/cleanup',
  requirePermission(PERMISSIONS.TRIGGER_CLEANUP),
  async (req, res) => {
    try {
      if (req.user.role !== 'admin') {
        return res.status(403).json({ error: 'Admin access required' });
      }

      const { days = 30, optimize = false } = req.body;
      const result = await cleanupOldRecords(days, { optimize });
      res.json({ success: true, archivedCount: result });
    } catch (error) {
      logger.error('Manual cleanup failed:', error);
      res.status(500).json({ error: 'Cleanup failed' });
    }
  });

module.exports = router; 