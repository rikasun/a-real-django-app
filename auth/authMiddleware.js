const AuthService = require('./auth');
const logger = require('../utils/logger');

async function authMiddleware(req, res, next) {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
      throw new Error('No token provided');
    }

    const decoded = await AuthService.verifyToken(token);
    req.user = decoded;
    next();
  } catch (error) {
    logger.error('Authentication failed:', error);
    res.status(401).json({ error: 'Authentication required' });
  }
}

module.exports = authMiddleware; 