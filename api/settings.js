const express = require('express');
const router = express.Router();
const { requirePermission } = require('../auth/roleMiddleware');
const { PERMISSIONS } = require('../config/roles');
const logger = require('../utils/logger');
const fs = require('fs').promises;
const path = require('path');

const CONFIG_FILE = path.join(__dirname, '../config/scheduler-config.json');

// Get current scheduler settings
router.get('/', 
  requirePermission(PERMISSIONS.SYSTEM_CONFIG),
  async (req, res) => {
    try {
      const settings = await loadSettings();
      res.json(settings);
    } catch (error) {
      logger.error('Failed to get settings:', error);
      res.status(500).json({ error: 'Failed to load settings' });
    }
});

// Update scheduler settings
router.put('/',
  requirePermission(PERMISSIONS.SYSTEM_CONFIG),
  async (req, res) => {
    try {
      const newSettings = req.body;
      
      // Validate settings
      validateSettings(newSettings);
      
      // Backup current settings
      await backupSettings();
      
      // Save new settings
      await saveSettings(newSettings);
      
      // Apply new settings to running scheduler
      await applySettings(newSettings);
      
      logger.info('Settings updated successfully', { user: req.user.username });
      res.json({ message: 'Settings updated successfully' });
    } catch (error) {
      logger.error('Failed to update settings:', error);
      res.status(400).json({ error: error.message });
    }
});

// Get settings history
router.get('/history',
  requirePermission(PERMISSIONS.SYSTEM_CONFIG),
  async (req, res) => {
    try {
      const history = await getSettingsHistory();
      res.json(history);
    } catch (error) {
      logger.error('Failed to get settings history:', error);
      res.status(500).json({ error: 'Failed to load settings history' });
    }
});

// Restore settings from backup
router.post('/restore/:timestamp',
  requirePermission(PERMISSIONS.SYSTEM_CONFIG),
  async (req, res) => {
    try {
      const { timestamp } = req.params;
      await restoreSettings(timestamp);
      res.json({ message: 'Settings restored successfully' });
    } catch (error) {
      logger.error('Failed to restore settings:', error);
      res.status(500).json({ error: 'Failed to restore settings' });
    }
});

async function loadSettings() {
  const data = await fs.readFile(CONFIG_FILE, 'utf8');
  return JSON.parse(data);
}

async function saveSettings(settings) {
  await fs.writeFile(CONFIG_FILE, JSON.stringify(settings, null, 2));
}

function validateSettings(settings) {
  const requiredFields = [
    'cleanupSchedule',
    'retentionDays',
    'batchSize',
    'diskThreshold',
    'emailNotifications'
  ];

  for (const field of requiredFields) {
    if (!(field in settings)) {
      throw new Error(`Missing required field: ${field}`);
    }
  }

  if (settings.retentionDays < 1) {
    throw new Error('Retention days must be at least 1');
  }

  if (settings.batchSize < 100 || settings.batchSize > 10000) {
    throw new Error('Batch size must be between 100 and 10000');
  }

  if (settings.diskThreshold < 50 || settings.diskThreshold > 95) {
    throw new Error('Disk threshold must be between 50 and 95');
  }
}

module.exports = router; 