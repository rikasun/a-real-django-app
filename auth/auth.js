const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const { getUserByCredentials, createUser, getUserByUsername } = require('../services/users');

const SECRET_KEY = process.env.JWT_SECRET || 'your-secret-key';
const SALT_ROUNDS = 10;

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

  static async signup(username, password, email) {
    try {
      // Check if username already exists
      const existingUser = await getUserByUsername(username);
      if (existingUser) {
        throw new Error('Username already exists');
      }

      // Validate password strength
      if (!this.isPasswordStrong(password)) {
        throw new Error('Password must be at least 8 characters long and contain letters, numbers, and special characters');
      }

      // Hash password
      const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);

      // Create new user
      const user = await createUser({
        username,
        password: hashedPassword,
        email,
        role: 'user',
        created_at: new Date()
      });

      // Generate token
      const token = jwt.sign(
        { 
          userId: user.id, 
          username: user.username,
          role: user.role 
        },
        SECRET_KEY,
        { expiresIn: '24h' }
      );

      return { 
        token, 
        user: { 
          id: user.id, 
          username: user.username, 
          email: user.email,
          role: user.role 
        } 
      };
    } catch (error) {
      throw new Error(`Signup failed: ${error.message}`);
    }
  }

  static isPasswordStrong(password) {
    const minLength = 8;
    const hasLetter = /[a-zA-Z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    
    return password.length >= minLength && hasLetter && hasNumber && hasSpecialChar;
  }
}

module.exports = AuthService; 