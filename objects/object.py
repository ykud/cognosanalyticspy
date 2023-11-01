"""Common attributes for every Cognos Analytics object"""
from dataclasses import dataclass


@dataclass
class Object:
    """
    All attributes for every CA object
    """
    id: str
    type: str
    defaultName: str
    