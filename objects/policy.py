"""Common attributes for Policies"""
from dataclasses import dataclass
import json
from objects.permission import Permission
from objects.security_object import SecurityObject

@dataclass
class Policy:
    """
    All attributes for Policy
    """
    permissions: [Permission]
    securityObject: SecurityObject

    def to_json(self):
        """convert to json"""
        return json.dumps(self, default=lambda o: o.__dict__)
    
