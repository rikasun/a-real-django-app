const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const { getUserByCredentials } = require('../services/users');

const SECRET_KEY = process.env.JWT_SECRET || 'your-secret-key';

class AuthService {
  static async login(username, password) {
    try {
      // Get user from database
      const user = await getUserByCredentials(username);
      if (!user) {
        throw new Error('User not found');
      }

      // Verify password
      const isValid = await bcrypt.compare(password, user.password);
      if (!isValid) {
        throw new Error('Invalid password');
      }

      // Generate JWT token
      const token = jwt.sign(
        { 
          userId: user.id, 
          username: user.username,
          role: user.role 
        },
        SECRET_KEY,
        { expiresIn: '24h' }
      );

      return { token, user: { id: user.id, username: user.username, role: user.role } };
    } catch (error) {
      throw new Error(`Authentication failed: ${error.message}`);
    }
  }

  static async verifyToken(token) {
    try {
      return jwt.verify(token, SECRET_KEY);
    } catch (error) {
      throw new Error('Invalid token');
    }
  }
}

module.exports = AuthService; 