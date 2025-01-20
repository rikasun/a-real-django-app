const express = require('express');
const router = express.Router();
const { requirePermission } = require('../auth/roleMiddleware');
const { PERMISSIONS } = require('../config/roles');
const logger = require('../utils/logger');
const fs = require('fs').promises;
const path = require('path');

const LOG_DIR = path.join(__dirname, '../logs');
const MAX_LOG_SIZE = 10 * 1024 * 1024; // 10MB

// Get logs with filtering and pagination
router.get('/', 
  requirePermission(PERMISSIONS.VIEW_LOGS),
  async (req, res) => {
    try {
      const { 
        level = 'info',
        startDate,
        endDate,
        search,
        page = 1,
        limit = 100
      } = req.query;

      const logs = await getLogs({
        level,
        startDate: startDate ? new Date(startDate) : undefined,
        endDate: endDate ? new Date(endDate) : undefined,
        search,
        page: parseInt(page),
        limit: parseInt(limit)
      });

      res.json(logs);
    } catch (error) {
      logger.error('Failed to get logs:', error);
      res.status(500).json({ error: 'Failed to retrieve logs' });
    }
});

// Get log summary/statistics
router.get('/summary', 
  requirePermission(PERMISSIONS.VIEW_LOGS),
  async (req, res) => {
    try {
      const summary = await getLogSummary();
      res.json(summary);
    } catch (error) {
      logger.error('Failed to get log summary:', error);
      res.status(500).json({ error: 'Failed to get log summary' });
    }
});

// Download logs
router.get('/download/:filename',
  requirePermission(PERMISSIONS.VIEW_LOGS),
  async (req, res) => {
    try {
      const { filename } = req.params;
      const filePath = path.join(LOG_DIR, filename);
      
      // Validate filename to prevent directory traversal
      if (!filename.match(/^[\w.-]+$/)) {
        throw new Error('Invalid filename');
      }

      res.download(filePath);
    } catch (error) {
      logger.error('Failed to download log:', error);
      res.status(400).json({ error: 'Failed to download log file' });
    }
});

// Clear old logs
router.delete('/cleanup',
  requirePermission(PERMISSIONS.SYSTEM_CONFIG),
  async (req, res) => {
    try {
      const { daysToKeep = 30 } = req.body;
      const deletedCount = await cleanupOldLogs(daysToKeep);
      res.json({ 
        message: 'Logs cleaned up successfully',
        deletedCount 
      });
    } catch (error) {
      logger.error('Failed to cleanup logs:', error);
      res.status(500).json({ error: 'Failed to cleanup logs' });
    }
});

async function getLogs({ level, startDate, endDate, search, page, limit }) {
  const logFiles = await fs.readdir(LOG_DIR);
  let allLogs = [];

  for (const file of logFiles) {
    if (!file.endsWith('.log')) continue;

    const content = await fs.readFile(path.join(LOG_DIR, file), 'utf8');
    const logs = content.split('\n')
      .filter(line => line.trim())
      .map(line => JSON.parse(line))
      .filter(log => {
        const timestamp = new Date(log.timestamp);
        return (
          (!level || log.level === level) &&
          (!startDate || timestamp >= startDate) &&
          (!endDate || timestamp <= endDate) &&
          (!search || JSON.stringify(log).toLowerCase().includes(search.toLowerCase()))
        );
      });

    allLogs = allLogs.concat(logs);
  }

  // Sort by timestamp descending
  allLogs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

  // Paginate results
  const start = (page - 1) * limit;
  const paginatedLogs = allLogs.slice(start, start + limit);

  return {
    logs: paginatedLogs,
    total: allLogs.length,
    page,
    totalPages: Math.ceil(allLogs.length / limit)
  };
}

async function getLogSummary() {
  const logFiles = await fs.readdir(LOG_DIR);
  let summary = {
    totalSize: 0,
    errorCount: 0,
    warningCount: 0,
    oldestLog: null,
    newestLog: null,
    logsByLevel: {}
  };

  for (const file of logFiles) {
    if (!file.endsWith('.log')) continue;

    const filePath = path.join(LOG_DIR, file);
    const stats = await fs.stat(filePath);
    summary.totalSize += stats.size;

    const content = await fs.readFile(filePath, 'utf8');
    const logs = content.split('\n')
      .filter(line => line.trim())
      .map(line => JSON.parse(line));

    logs.forEach(log => {
      summary.logsByLevel[log.level] = (summary.logsByLevel[log.level] || 0) + 1;
      if (log.level === 'error') summary.errorCount++;
      if (log.level === 'warn') summary.warningCount++;

      const timestamp = new Date(log.timestamp);
      if (!summary.oldestLog || timestamp < new Date(summary.oldestLog)) {
        summary.oldestLog = log.timestamp;
      }
      if (!summary.newestLog || timestamp > new Date(summary.newestLog)) {
        summary.newestLog = log.timestamp;
      }
    });
  }

  return summary;
}

async function cleanupOldLogs(daysToKeep) {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

  const logFiles = await fs.readdir(LOG_DIR);
  let deletedCount = 0;

  for (const file of logFiles) {
    if (!file.endsWith('.log')) continue;

    const filePath = path.join(LOG_DIR, file);
    const stats = await fs.stat(filePath);

    if (stats.mtime < cutoffDate) {
      await fs.unlink(filePath);
      deletedCount++;
    }
  }

  return deletedCount;
}

module.exports = router; 