"""Roles related REST endpoints"""
from dataclasses import fields
import logging
from services.rest import RestService
from objects.object import Object
from objects.role import Role
from objects.group import Group
from objects.user import User
from objects.members import Members


class RolesService:
    """ Roles related endpoints"""

    def __init__(self, rest: RestService, logger: logging.Logger = None):
        """ Initiate the Service
        """
        self._ca_rest = rest
        self._base_endpoint = '/api/v1/roles'
        self._logger = logger or logging.getLogger(__name__)

    def get_role(self, role_id='') -> Role:
        """ Get roles
        https://developer.ibm.com/apis/catalog/cognosanalytics--cognos-analytics-rest-api/api/API--cognosanalytics--cognos-analytics#list_role_objects
        """
        response = self._ca_rest.get(
            endpoint=f'{self._base_endpoint}/{role_id}')
        return Role(
            **{k:v for k,v in response.data.items() if k in set(f.name for f in fields(Role))}
            )

    def get_child_roles(self, parent_id='') -> [Role]:
        """ Get roles by namespace folder ID
        https://developer.ibm.com/apis/catalog/cognosanalytics--cognos-analytics-rest-api/api/API--cognosanalytics--cognos-analytics#list_role_objects
        """
        response = self._ca_rest.get(
            endpoint=f'{self._base_endpoint}',
            params={'parent_id': parent_id})
        roles = []
        if 'roles' in response.data:
            for role in response.data['roles']:
                roles.append(Role(
                    **{k:v for k,v in role.items() if k in set(f.name for f in fields(Role))}
                    ))
        return roles

    def get_role_members(self, role: Role) -> Members:
        """ Get role members"""
        response = self._ca_rest.get(
            endpoint=f'{self._base_endpoint}/{role.id}/members')
        groups = []
        if 'groups' in response.data:
            for grp in response.data['groups']:
                groups.append(Group(
                    **{k:v for k,v in grp.items() if k in set(f.name for f in fields(Group))}
                    ))
        users = []
        if 'users' in response.data:
            for usr in response.data['users']:
                users.append(User(
                    **{k:v for k,v in usr.items() if k in set(f.name for f in fields(User))}
                    ))
        return Members(**{'groups': groups, 'users': users})

    def delete_role(self, role: Role):
        """ delete role
        """
        self._logger.debug('Deleting role %s', role.defaultName)
        response = self._ca_rest.delete(
            endpoint=f'{self._base_endpoint}/{role.id}')
        if response.status_code == 204:
            self._logger.info("Deleted role %s", role.defaultName)
        else:
            self._logger.error("Couldn't delete %s : %s",
                               role.defaultName, response.message, exc_info=1)

    def create_role_as_child(self, parent_id: str, role_name: str):
        """	Create a role as a child of namespace_object
        """
        data = {'defaultName': role_name, 'type': 'role'}
        response = self._ca_rest.post(
            endpoint=f'{self._base_endpoint}/{parent_id}', data=data)
        if response.status_code == 201:
            self._logger.info('Added role %s successfully', role_name)
        else:
            self._logger.error('Adding role %s failed: %s',
                               role_name, response.content, exc_info=1)

    def add_role_members(self, 
                          role: Role,
                          groups_to_add: [Group] = None, 
                          users_to_add: [User] = None):
        """	adding role members : users & roles
        """
        self._logger.debug('Adding members to role to %s, roles %s, users %s ',
                           role.defaultName, groups_to_add, users_to_add)
        data = {}
        if users_to_add:
            data['users'] = [{'id': usr.id} for usr in users_to_add]
        if groups_to_add:
            data['groups'] = [{'id': grp.id} for grp in groups_to_add]
        response = self._ca_rest.post(
            endpoint=f'{self._base_endpoint}/{role.id}/members', data=data)
        if response.status_code in (200, 201):
            self._logger.info('Added %d role members to %s',
                              0 if users_to_add is None else len(users_to_add)
                              +
                              0 if groups_to_add is None else len(groups_to_add), role.defaultName)
        else:
            self._logger.error(
                'Changing role %s members failed:%s', 
                role.defaultName, response.message, exc_info=1)

    def remove_role_member(self, role: Role, member: Object, member_type='user'):
        """	removing specified role member from role
        https://developer.ibm.com/apis/catalog/cognosanalytics--cognos-analytics-rest-api/api/API--cognosanalytics--cognos-analytics#delete_member_from_role
        """
        response = self._ca_rest.delete(
            endpoint=f"{self._base_endpoint}/{role.id}/members/{member_type}/{member.id}")
        if response.status_code == 200:
            self._logger.info('Removed member %s from role %s',
                              member.defaultName, role.defaultName)
        else:
            self._logger.error(
                'Changing role members failed:%s', response.message, exc_info=1)
