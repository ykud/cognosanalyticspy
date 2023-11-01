"""Groups related REST endpoints"""
import logging
from dataclasses import fields
from services.rest import RestService
from objects.object import Object
from objects.group import Group
from objects.user import User
from objects.members import Members


class GroupsService:
    """ Groups related endpoints"""

    def __init__(self, rest: RestService, logger: logging.Logger = None):
        """ Initiate the Service
        """
        self._ca_rest = rest
        self._base_endpoint = '/api/v1/groups'
        self._logger = logger or logging.getLogger(__name__)

    def get_group(self, group_id='') -> Group:
        """ Get groups
        https://developer.ibm.com/apis/catalog/cognosanalytics--cognos-analytics-rest-api/api/API--cognosanalytics--cognos-analytics#list_group_objects
        """
        response = self._ca_rest.get(
            endpoint=f'{self._base_endpoint}/{group_id}')
        return Group(
            **{k:v for k,v in response.data.items() if k in set(f.name for f in fields(Group))}
        )

    def get_child_groups(self, parent_id='') -> [Group]:
        """ Get groups by namespace folde ID
        https://developer.ibm.com/apis/catalog/cognosanalytics--cognos-analytics-rest-api/api/API--cognosanalytics--cognos-analytics#list_group_objects
        """
        response = self._ca_rest.get(
            endpoint=f'{self._base_endpoint}',
            params={'parent_id': parent_id})
        groups = []
        if 'groups' in response.data:
            for grp in response.data['groups']:
                groups.append(Group(
                    **{k:v for k,v in grp.items() if k in set(f.name for f in fields(Group))}
                    ))
        return groups

    def get_group_members(self, group: Group) -> Members:
        """ Get group members"""
        response = self._ca_rest.get(
            endpoint=f'{self._base_endpoint}/{group.id}/members')
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

    def delete_group(self, group: Group):
        """ delete group
        """
        self._logger.debug('Deleting group %s', group.defaultName)
        response = self._ca_rest.delete(
            endpoint=f'{self._base_endpoint}/{group.id}')
        if response.status_code == 204:
            self._logger.info("Deleted group %s", group.defaultName)
        else:
            self._logger.error("Couldn't delete %s : %s",
                               group.defaultName, response.message, exc_info=1)

    def create_group_as_child(self, parent_id: str, group_name: str):
        """	Create a group as a child of 
        """
        data = {'defaultName': group_name, 'type': 'group'}
        response = self._ca_rest.post(
            endpoint=f'{self._base_endpoint}/{parent_id}', data=data)
        if response.status_code == 201:
            self._logger.info('Added group %s successfully', group_name)
        else:
            self._logger.error('Adding group %s failed: %s',
                               group_name, response.content, exc_info=1)

    def add_group_members(self, 
                          group: Group,
                          groups_to_add: [Group] = None, 
                          users_to_add: [User] = None):
        """	adding group members : users & groups
        """
        self._logger.debug('Adding members to group to %s, groups %s, users %s ',
                           group.defaultName, groups_to_add, users_to_add)
        data = {}
        if users_to_add:
            data['users'] = [{'id': usr.id} for usr in users_to_add]
        if groups_to_add:
            data['groups'] = [{'id': grp.id} for grp in groups_to_add]
        response = self._ca_rest.post(
            endpoint=f'{self._base_endpoint}/{group.id}/members', data=data)
        if response.status_code in (200, 201):
            self._logger.info('Added %d groups and %d users as members to %s',
                            0 if groups_to_add is None else len(groups_to_add),
                            0 if users_to_add is None else len(users_to_add),
                            group.defaultName)
        else:
            self._logger.error(
                'Changing group %s members failed:%s', 
                group.defaultName, response.message, exc_info=1)

    def remove_group_member(self, group: Group, member: Object, member_type='user'):
        """	removing specified group member from group
        https://developer.ibm.com/apis/catalog/cognosanalytics--cognos-analytics-rest-api/api/API--cognosanalytics--cognos-analytics#delete_member_from_group
        """
        response = self._ca_rest.delete(
            endpoint=f"{self._base_endpoint}/{group.id}/members/{member_type}/{member.id}")
        if response.status_code in (200,204):
            self._logger.info('Removed member %s from group %s',
                              member.defaultName, group.defaultName)
        else:
            self._logger.error(
                'Changing group members failed:%s', response.message, exc_info=1)
