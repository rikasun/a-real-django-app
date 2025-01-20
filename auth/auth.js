const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const { getUserByCredentials, createUser, getUserByUsername, updateUserRole } = require('../services/users');
const { ROLES, ROLE_PERMISSIONS } = require('../config/roles');

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

  static async signup(username, password, email, role = ROLES.USER) {
    try {
      // Check if username already exists
      const existingUser = await getUserByUsername(username);
      if (existingUser) {
        throw new Error('Username already exists');
      }

      // Only admins can create other admins
      if (role === ROLES.ADMIN && (!this.currentUser || this.currentUser.role !== ROLES.ADMIN)) {
        throw new Error('Unauthorized to create admin users');
      }

      // Validate role
      if (!Object.values(ROLES).includes(role)) {
        throw new Error('Invalid role specified');
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
        role,
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

  static async updateUserRole(userId, newRole, adminToken) {
    try {
      // Verify admin token
      const decoded = await this.verifyToken(adminToken);
      if (decoded.role !== ROLES.ADMIN) {
        throw new Error('Only admins can update user roles');
      }

      // Validate new role
      if (!Object.values(ROLES).includes(newRole)) {
        throw new Error('Invalid role specified');
      }

      const updatedUser = await updateUserRole(userId, newRole);
      return {
        success: true,
        user: {
          id: updatedUser.id,
          username: updatedUser.username,
          role: updatedUser.role
        }
      };
    } catch (error) {
      throw new Error(`Role update failed: ${error.message}`);
    }
  }

  static hasPermission(userRole, permission) {
    return ROLE_PERMISSIONS[userRole]?.includes(permission) || false;
  }
}

module.exports = AuthService; 