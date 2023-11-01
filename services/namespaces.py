"""Namespaces related services 
NOTE: this is not part of official API
done via looking at what calls Cognos Analytics UI does when navigating the `Accounts` menu
Need to be logged in via report_data.login method to get the X-XSRF-Token set up
"""
import logging
from dataclasses import fields
from services.rest import RestService
from objects.namespace_object import NamespaceObject


class NamespacesService:
    """ Namespaces related endpoints"""

    def __init__(self, rest: RestService, logger: logging.Logger = None):
        """ Initiate the Service
        """
        self._ca_rest = rest
        self._base_endpoint = '/v1/namespaces'
        self._logger = logger or logging.getLogger(__name__)

    def get_list_of_namespaces(self) -> [NamespaceObject]:
        """ Return the list of configured namespaces"""
        response = self._ca_rest.get(endpoint=f'{self._base_endpoint}')
        # filter the class init for the attributes defined in dataclass
        return [NamespaceObject(
            **{k:v for k,v in obj.items() if k in set(f.name for f in fields(NamespaceObject))})
            for obj in response.data['data']]

    def get_namespace_items(self, namespace_object: NamespaceObject) -> [NamespaceObject]:
        """ Get namespace object items"""
        response = self._ca_rest.get(
            endpoint=f'{self._base_endpoint}/{namespace_object.id}/items')
        # filter the class init for the attributes defined in dataclass
        return [NamespaceObject(
            **{k:v for k,v in obj.items() if k in set(f.name for f in fields(NamespaceObject))})
            for obj in response.data['data']]
