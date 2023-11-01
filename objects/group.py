"""store information about a CA Group"""
from dataclasses import dataclass
from typing import Optional
from objects.object import Object

@dataclass
class Group(Object):
    """
    store information about a CA Group
    """
    searchPath: str
    modificationTime: Optional[str] = None
    defaultDescription: Optional[str] = None
    hidden: Optional[bool] = None
    disabled: Optional[bool] = None
    permissions: Optional[str] = None
    #defaultName: Optional[str] = None
    tenantID: Optional[str] = None
    version: Optional[int] = 0
    links: Optional[str] = None
    policies:Optional[str] = None
    