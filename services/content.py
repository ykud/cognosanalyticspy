"""Content related REST endpoints"""
import logging
from dataclasses import fields
from services.rest import RestService
from objects.content_object import ContentObject
from objects.policy import Policy

class ContentService:
    """ Content related endpoints"""

    def __init__(self, rest: RestService, logger: logging.Logger = None):
        """ Initiate the Service
        """
        self._ca_rest = rest
        self._base_endpoint = '/api/v1/content'
        self._logger = logger or logging.getLogger(__name__)

    def get_content(self,
                    content_id: str ='',
                    content_fields_list:[str]=None) -> ContentObject:
        """ Get content object
        """
        response = self._ca_rest.get(
            endpoint=f'{self._base_endpoint}/{content_id}',
            params={'fields':','.join(content_fields_list)} if content_fields_list is not None 
            else None)
        # need to return policies
        permissions_list = []
        if 'policies' in response.data:
            for element in response.data["policies"]:
                permissions_list.append(Policy(
                        permissions= element['permissions'],
                        securityObject =  element['securityObject'])
                    )

        return ContentObject(id=response.data['id'],
                             type=response.data['type'],
                             defaultName=response.data['defaultName'],
                             modificationTime=response.data['modificationTime'],
                             policies=permissions_list)

    def get_content_items(self,
                    content_id: str ='') -> [ContentObject]:
        """ Get content objects items, e.g. objects in folder
        """
        response = self._ca_rest.get(
            endpoint=f'{self._base_endpoint}/{content_id}/items')
        object_list = []
        if 'content' in response.data:
            for obj in response.data['content']:
                object_list.append(
                    ContentObject(id=obj['id'],
                                type=obj['type'],
                                modificationTime=obj['modificationTime'],
                                defaultName=obj['defaultName'])
                )
        return object_list
    
    def update_content(self,
                    content_object: ContentObject):
        """ Update content object
        """
        class_attributes = set(f.name for f in fields(ContentObject))
        data = {}
        for attr in class_attributes:
            if attr not in ('policies'):
                data[attr] = content_object.__getattribute__(attr)

        #TODO: there must be a better way to deserialize nested class to JSON
        policy_list = []
        for policy in content_object.policies:
            #print (policy.to_json())
            policy_serialized = {}
            permission_list = []
            for permission in policy.permissions:
                permission_list.append(permission)
            policy_serialized['securityObject'] = policy.securityObject
            policy_serialized['permissions'] = permission_list
            policy_list.append(policy_serialized)
        data['policies'] = policy_list
        response = self._ca_rest.put(
            endpoint=f'{self._base_endpoint}/{content_object.id}',
            data=data)
        if response.status_code == 204:
            logging.debug('Object %s updated sucessfully',content_object.defaultName)
        else:
            logging.warning('Updating object %s failed with %s'
                         ,content_object.defaultName, response.message)