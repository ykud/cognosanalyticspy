from dataclasses import dataclass
from objects.user import User
from objects.group import Group

@dataclass
class Members:
    """
    store information group or role members
    """
    users: [User]
    groups: [Group]    