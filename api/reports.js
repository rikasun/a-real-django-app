const express = require('express');
const router = express.Router();
const { requirePermission } = require('../auth/roleMiddleware');
const { PERMISSIONS } = require('../config/roles');
const logger = require('../utils/logger');
const ExcelJS = require('exceljs');
const PDFDocument = require('pdfkit');

// Get performance report
router.get('/performance', 
  requirePermission(PERMISSIONS.VIEW_LOGS),
  async (req, res) => {
    try {
      const { startDate, endDate, format = 'json' } = req.query;
      const report = await generatePerformanceReport(startDate, endDate);

      if (format === 'excel') {
        const buffer = await generateExcelReport(report);
        res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        res.setHeader('Content-Disposition', 'attachment; filename=performance-report.xlsx');
        return res.send(buffer);
      } else if (format === 'pdf') {
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', 'attachment; filename=performance-report.pdf');
        return generatePDFReport(report, res);
      }

      res.json(report);
    } catch (error) {
      logger.error('Failed to generate performance report:', error);
      res.status(500).json({ error: 'Failed to generate report' });
    }
});

// Get cleanup statistics
router.get('/cleanup-stats',
  requirePermission(PERMISSIONS.VIEW_LOGS),
  async (req, res) => {
    try {
      const { period = '30d' } = req.query;
      const stats = await getCleanupStats(period);
      res.json(stats);
    } catch (error) {
      logger.error('Failed to get cleanup stats:', error);
      res.status(500).json({ error: 'Failed to get cleanup statistics' });
    }
});

// Schedule report generation
router.post('/schedule',
  requirePermission(PERMISSIONS.SYSTEM_CONFIG),
  async (req, res) => {
    try {
      const { 
        reportType,
        schedule,
        recipients,
        format = 'pdf'
      } = req.body;

      const job = await scheduleReport({
        reportType,
        schedule,
        recipients,
        format
      });

      res.json({ 
        message: 'Report scheduled successfully',
        jobId: job.id
      });
    } catch (error) {
      logger.error('Failed to schedule report:', error);
      res.status(400).json({ error: error.message });
    }
});

async function generatePerformanceReport(startDate, endDate) {
  const metrics = await getPerformanceMetrics(startDate, endDate);
  const cleanupStats = await getCleanupStats(startDate, endDate);
  const diskUsage = await getDiskUsageHistory(startDate, endDate);

  return {
    period: {
      start: startDate,
      end: endDate
    },
    summary: {
      totalCleanups: cleanupStats.totalJobs,
      successRate: cleanupStats.successRate,
      totalRecordsArchived: cleanupStats.totalRecords,
      averageDuration: cleanupStats.averageDuration
    },
    performance: {
      averageCPU: metrics.averageCPU,
      peakCPU: metrics.peakCPU,
      averageMemory: metrics.averageMemory,
      peakMemory: metrics.peakMemory
    },
    storage: {
      averageDiskUsage: diskUsage.average,
      peakDiskUsage: diskUsage.peak,
      spaceReclaimed: diskUsage.reclaimed
    },
    trends: {
      dailyStats: metrics.dailyStats,
      weeklyStats: metrics.weeklyStats
    }
  };
}

async function generateExcelReport(data) {
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet('Performance Report');

  // Add summary section
  worksheet.addRow(['Performance Report Summary']);
  worksheet.addRow(['Period', `${data.period.start} to ${data.period.end}`]);
  worksheet.addRow(['Total Cleanups', data.summary.totalCleanups]);
  worksheet.addRow(['Success Rate', `${data.summary.successRate}%`]);
  worksheet.addRow(['Records Archived', data.summary.totalRecordsArchived]);

  // Add performance metrics
  worksheet.addRow([]);
  worksheet.addRow(['Performance Metrics']);
  worksheet.addRow(['Average CPU', `${data.performance.averageCPU}%`]);
  worksheet.addRow(['Peak CPU', `${data.performance.peakCPU}%`]);
  worksheet.addRow(['Average Memory', `${data.performance.averageMemory}MB`]);
  worksheet.addRow(['Peak Memory', `${data.performance.peakMemory}MB`]);

  // Add daily stats
  worksheet.addRow([]);
  worksheet.addRow(['Daily Statistics']);
  worksheet.addRow(['Date', 'Jobs Run', 'Success Rate', 'Records Processed']);
  data.trends.dailyStats.forEach(stat => {
    worksheet.addRow([
      stat.date,
      stat.jobsRun,
      `${stat.successRate}%`,
      stat.recordsProcessed
    ]);
  });

  return await workbook.xlsx.writeBuffer();
}

async function generatePDFReport(data, res) {
  const doc = new PDFDocument();
  doc.pipe(res);

  // Add title
  doc.fontSize(20).text('Performance Report', { align: 'center' });
  doc.moveDown();

  // Add summary section
  doc.fontSize(16).text('Summary');
  doc.fontSize(12)
    .text(`Period: ${data.period.start} to ${data.period.end}`)
    .text(`Total Cleanups: ${data.summary.totalCleanups}`)
    .text(`Success Rate: ${data.summary.successRate}%`)
    .text(`Records Archived: ${data.summary.totalRecordsArchived}`);
  doc.moveDown();

  // Add performance section
  doc.fontSize(16).text('Performance Metrics');
  doc.fontSize(12)
    .text(`Average CPU: ${data.performance.averageCPU}%`)
    .text(`Peak CPU: ${data.performance.peakCPU}%`)
    .text(`Average Memory: ${data.performance.averageMemory}MB`)
    .text(`Peak Memory: ${data.performance.peakMemory}MB`);

  // Add charts and graphs
  // ... Add visualization logic here

  doc.end();
}

module.exports = router; 