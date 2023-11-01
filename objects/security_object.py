"""Common attributes for SecurityObject"""
from dataclasses import dataclass

@dataclass
class SecurityObject:
    """
    All attributes for SecurityObject
    """
    searchPath: str
    type: str
    
