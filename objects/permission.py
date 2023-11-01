"""Permissions object"""
from dataclasses import dataclass

@dataclass
class Permission:
    """
    All attributes for permissions
    """
    access: str
    name: str
