const ROLES = {
  ADMIN: 'admin',
  MANAGER: 'manager',
  USER: 'user'
};

const PERMISSIONS = {
  VIEW_SCHEDULER: 'view_scheduler',
  TRIGGER_CLEANUP: 'trigger_cleanup',
  MANAGE_USERS: 'manage_users',
  VIEW_LOGS: 'view_logs',
  SYSTEM_CONFIG: 'system_config'
};

const ROLE_PERMISSIONS = {
  [ROLES.ADMIN]: [
    PERMISSIONS.VIEW_SCHEDULER,
    PERMISSIONS.TRIGGER_CLEANUP,
    PERMISSIONS.MANAGE_USERS,
    PERMISSIONS.VIEW_LOGS,
    PERMISSIONS.SYSTEM_CONFIG
  ],
  [ROLES.MANAGER]: [
    PERMISSIONS.VIEW_SCHEDULER,
    PERMISSIONS.TRIGGER_CLEANUP,
    PERMISSIONS.VIEW_LOGS
  ],
  [ROLES.USER]: [
    PERMISSIONS.VIEW_SCHEDULER
  ]
};

module.exports = {
  ROLES,
  PERMISSIONS,
  ROLE_PERMISSIONS
}; 