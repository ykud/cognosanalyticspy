"""Main Cognos Analytics interaction service, entry point to all others
will put login / logout methods here"""
import logging
from services.rest import RestService
from services.users import UsersService
from services.groups import GroupsService
from services.roles import RolesService
from services.namespaces import NamespacesService
from services.report_data import ReportDataService
from services.content import ContentService


class CognosAnalyticsService:
    """ Will expose all other services throughout this one
    """

    def __init__(self, logger: logging.Logger = None, **kwargs):
        """ Initiate the CognosAnalyticsService
        """
        self._ca_rest = RestService(**kwargs)
        self._base_endpoint = '/api/v1/session'
        self.users = UsersService(rest=self._ca_rest)
        self.groups = GroupsService(rest=self._ca_rest)
        self.roles = RolesService(rest=self._ca_rest)
        self.namespaces = NamespacesService(rest=self._ca_rest)
        self.report_data = ReportDataService(rest=self._ca_rest)
        self.content = ContentService(rest=self._ca_rest)
        self._logger = logger or logging.getLogger(__name__)

    def login(self, namespace="", user="", password=""):
        """ login to CA using provided credentials username / password
        https://www.ibm.com/docs/en/cognos-analytics/12.0.0?topic=window-rest-sample
        """

        credentials = {
            "parameters": [
                {
                    "name": "CAMNamespace",
                    "value": namespace
                },
                {
                    "name": "CAMUsername",
                    "value": user
                },
                {
                    "name": "CAMPassword",
                    "value": password
                }
            ]
        }
        response = self._ca_rest.put(
            endpoint=f'{self._base_endpoint}', params=None, data=credentials)
        if response.status_code in (200, 201):
            # session ID header
            self._ca_rest.add_http_header(
                key='IBM-BA-Authorization', 
                value = response.data['session_key']
                )
            self._logger.info(
                "Logged in to Cognos Analytics as %s\%s",namespace, user)
        else:
            self._logger.error("Couldn't login into CA as %s\%s:%s",
                               namespace, user, response.message)

    def login_with_code(self, namespace="", code=""):
        """ login to OIDC using authorization code
        https://www.ibm.com/support/pages/cognos-analytics-oidc-authentication-sdk
        """
        credentials = {
            "parameters": [
                {
                    "name": "CAMNamespace",
                    "value": namespace
                },
                {
                    "name": "code",
                    "value": code
                }
            ]
        }
        response = self._ca_rest.put(
            endpoint=f'{self._base_endpoint}', params=None, data=credentials)
        if response.status_code == 201:
            self._ca_rest.add_http_header(
                key='IBM-BA-Authorization', value=response.data['session_key'])
            self._logger.info(
                "Logged in to Cognos Analytics namespace %s",namespace)
        else:
            self._logger.error("Couldn't login into Cognos Analytics namespace %s : %s",
                namespace, response.message)

    def login_with_api_key(self, api_key=""):
        """ login with API key
        https://developer.ibm.com/apis/catalog/cognosanalytics--cognos-analytics-rest-api/Getting%20Started
        """
        credentials = {
            "parameters": [
                {
                    "name": "CAMAPILoginKey",
                    "value": api_key
                }
            ]
        }
        response = self._ca_rest.put(
            endpoint=f'{self._base_endpoint}', params=None, data=credentials)
        if response.status_code == 201:
            self._ca_rest.add_http_header(
                key='IBM-BA-Authorization', value=response.data['session_key'])
            self._logger.info("Logged in to Cognos Analytics")
        else:
            self._logger.error("Couldn't login into Cognos Analytics namespace: %s",
                               response.message)

    def logout(self):
        """ logout from CA
        """
        response = self._ca_rest.delete(endpoint=f'{self._base_endpoint}', params=None, data=None)
        if response.status_code == 204:
            self._logger.info("Logged out of Cognos Analytics")
        else:
            self._logger.error("Couldn't logout of  CA: %s",
                               response.message, exc_info=1)
