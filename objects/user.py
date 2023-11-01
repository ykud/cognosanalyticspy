"""Cognos Analytics User attributes"""
from dataclasses import dataclass
from typing import Optional
from objects.object import Object

@dataclass
class User(Object):
    """store information about a CA user"""
    searchPath: str
    modificationTime: Optional[str] = None
    tenantID: Optional[str] = None
    version: Optional[int] = 0
    links: Optional[str] = None
    email: Optional[str] = None
    userName:Optional[str] = None
    