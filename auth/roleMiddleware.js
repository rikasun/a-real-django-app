const { PERMISSIONS } = require('../config/roles');

function requirePermission(permission) {
  return (req, res, next) => {
    const userRole = req.user?.role;
    
    if (!userRole || !AuthService.hasPermission(userRole, permission)) {
      return res.status(403).json({
        error: 'Insufficient permissions'
      });
    }
    
    next();
  };
}

module.exports = { requirePermission }; 