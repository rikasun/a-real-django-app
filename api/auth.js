const express = require('express');
const router = express.Router();
const AuthService = require('../auth/auth');
const logger = require('../utils/logger');
const { body, validationResult } = require('express-validator');

// Validation middleware
const validateSignup = [
  body('username')
    .isLength({ min: 3 })
    .withMessage('Username must be at least 3 characters long')
    .matches(/^[a-zA-Z0-9_]+$/)
    .withMessage('Username can only contain letters, numbers and underscores'),
  body('email')
    .isEmail()
    .withMessage('Must be a valid email address'),
  body('password')
    .isLength({ min: 8 })
    .withMessage('Password must be at least 8 characters long')
];

// Signup route
router.post('/signup', validateSignup, async (req, res) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { username, password, email } = req.body;
    const result = await AuthService.signup(username, password, email);
    
    logger.info(`New user registered: ${username}`);
    res.status(201).json(result);
  } catch (error) {
    logger.error('Signup failed:', error);
    res.status(400).json({ error: error.message });
  }
});

// Login route
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const result = await AuthService.login(username, password);
    
    logger.info(`User logged in: ${username}`);
    res.json(result);
  } catch (error) {
    logger.error('Login failed:', error);
    res.status(401).json({ error: error.message });
  }
});

module.exports = router; 