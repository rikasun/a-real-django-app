from enum import Enum
from typing import List, Dict, Set
from dataclasses import dataclass

class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class Permission(str, Enum):
    VIEW_SCHEDULER = "view_scheduler"
    TRIGGER_CLEANUP = "trigger_cleanup"
    MANAGE_USERS = "manage_users"
    VIEW_LOGS = "view_logs"
    SYSTEM_CONFIG = "system_config"

ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.VIEW_SCHEDULER,
        Permission.TRIGGER_CLEANUP,
        Permission.MANAGE_USERS,
        Permission.VIEW_LOGS,
        Permission.SYSTEM_CONFIG
    },
    Role.MANAGER: {
        Permission.VIEW_SCHEDULER,
        Permission.TRIGGER_CLEANUP,
        Permission.VIEW_LOGS
    },
    Role.USER: {
        Permission.VIEW_SCHEDULER
    }
}

@dataclass
class RoleConfig:
    role: Role
    permissions: Set[Permission]

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions 