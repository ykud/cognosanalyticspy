"""Cognos Analytics content object attributes"""
from dataclasses import dataclass
from typing import Optional,List
from objects.object import Object
from objects.policy import Policy

@dataclass
class ContentObject(Object):
    """store information about a content object"""
    policies: [Policy] = None
    modificationTime: Optional[str] = None
