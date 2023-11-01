"""User related Cognos Analytics Rest API calls"""
from dataclasses import fields
import logging
from services.rest import RestService
from objects.user import User

class UsersService:
    """ Users related endpoints
    """
    def __init__(self, rest: RestService,logger: logging.Logger = None):
        """ Initiate the service
        """
        self._ca_rest = rest
        self._base_endpoint = '/api/v1/users'
        self._logger = logger or logging.getLogger(__name__)

    def get_users(self, identifier="") -> [User]:
        """ List existing users with the given user identifier.
        """
        response = self._ca_rest.get(
            endpoint=f'{self._base_endpoint}',
            params={'identifier':identifier})
        users = []
        if 'users' in response.data:
            for usr in response.data['users']:
                users.append(User(
                    **{k:v for k,v in usr.items() if k in set(f.name for f in fields(User))}
                    ))
        return users

    def add_user (self, 
                  namespace:str, 
                  identity:str,
                  defaultName:str):
        """	add user to the namespace
        """
        self._logger.debug('Adding user to %s with identity %s, defaultName %s '
                           ,namespace,identity,defaultName)
        data = {'defaultName':defaultName, 'identity':identity}
        response = self._ca_rest.post(endpoint=f'{self._base_endpoint}'
                                      ,params={'namespace':namespace},data=data)
        if response.status_code == 201:
            self._logger.info("Added user %s:%s to %s",identity,defaultName,namespace)
        elif response.status_code == 409:
            self._logger.info("User %s:%s is already in %s",identity,defaultName,namespace)
        else:
            self._logger.error("Couldn't add %s:%s to %s",identity,defaultName,namespace)

    def delete_user (self, user:User):
        """	delete user by id
        """
        self._logger.debug('Deleting user %s ',user.defaultName)
        response = self._ca_rest.delete(endpoint=f'{self._base_endpoint}/{user.id}')
        if response.status_code == 204:
            self._logger.info("Deleted user %s",user.defaultName)
        else:
            self._logger.error("Couldn't delete %s : %s",user.defaultName,response.message)

    def copy_user_profile (self,
                           source_user:User,
                           target_user_list:[User], 
                           copy_folders:bool=True,
                           copy_pages:bool=True,
                           copy_preferences:bool=True):
        """	copy source user profile to target user profile
        https://developer.ibm.com/apis/catalog/cognosanalytics--cognos-analytics-rest-api/api/API--cognosanalytics--cognos-analytics#copy_user_profile
        """
        self._logger.debug('Copying user %s to %s',source_user.defaultName,target_user_list)
        body = {'folders':copy_folders,
                'pages':copy_pages,
                'preferences':copy_preferences,
                'targetUsers':[usr.id for usr in target_user_list]} 
        response = self._ca_rest.post(
            endpoint=f"{self._base_endpoint}/{source_user.id}/copy_profile",
            params={},
            data=body)
        if response.status_code==500:
            self._logger.error('User profile copy failed')
        elif  response.data['failed']!=0:
            self._logger.error('User profile copy failed: %s', response.data['failedList'])
        else:
            self._logger.info('Copied user profile from %s to %s with %s',
                              source_user.defaultName,
                              [usr.defaultName for usr in target_user_list],
                              response.data['succesList'])
            