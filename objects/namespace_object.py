"""Cognos Analytics Namespace object attributes"""
from dataclasses import dataclass
from typing import Optional
from objects.object import Object

@dataclass
class NamespaceObject(Object):
    """store information about a Namespace object"""
    searchPath: str
    objectClass: str
    creationTime: Optional[str] = None
    modificationTime: Optional[str] = None
    permissions: Optional[str] = None
    hasChildren: Optional[bool] = None
    disabled: Optional[bool] = None
    hidden: Optional[bool] = None
    shown: Optional[bool] = None
    tenantID: Optional[str] = None
    owner: Optional[str] = None
    defaultDescription: Optional[str] = None
    version: Optional[int] = 0
    links: Optional[str] = None
    policies: Optional[str] = None
    ancestors:Optional[str] = None
    position:Optional[str] = None
    capabilities:Optional[str] = None
    defaultScreenTip:Optional[str] = None
    