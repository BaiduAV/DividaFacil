from typing import Dict
from src.models.user import User
from src.models.group import Group
from src.services.database_service import DatabaseService

# Initialize database on module import
DatabaseService.initialize()

class DatabaseBackedDict:
    """Dictionary-like interface backed by database for backward compatibility."""
    
    def __init__(self, entity_type: str):
        self.entity_type = entity_type
    
    def get(self, key: str, default=None):
        if self.entity_type == "users":
            user = DatabaseService.get_user(key)
            return user if user else default
        else:  # groups
            group = DatabaseService.get_group(key)
            return group if group else default
    
    def __getitem__(self, key: str):
        result = self.get(key)
        if result is None:
            raise KeyError(key)
        return result
    
    def __setitem__(self, key: str, value):
        # This is handled by the service methods, not direct assignment
        pass
    
    def __contains__(self, key: str):
        return self.get(key) is not None
    
    def keys(self):
        if self.entity_type == "users":
            return DatabaseService.get_all_users().keys()
        else:
            return DatabaseService.get_all_groups().keys()
    
    def values(self):
        if self.entity_type == "users":
            return DatabaseService.get_all_users().values()
        else:
            return DatabaseService.get_all_groups().values()
    
    def items(self):
        if self.entity_type == "users":
            return DatabaseService.get_all_users().items()
        else:
            return DatabaseService.get_all_groups().items()
    
    def clear(self):
        # For tests - not implemented for production safety
        pass

# Global storage backed by database
USERS: Dict[str, User] = DatabaseBackedDict("users")
GROUPS: Dict[str, Group] = DatabaseBackedDict("groups")
