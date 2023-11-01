"""Wrapper for rest calls"""
import logging
import json
from json import JSONDecodeError
from typing import Dict

import requests
from requests_toolbelt.utils import dump
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from objects.rest_response import RestResponse
from exceptions.rest_service_exception import RestServiceException

class RestService:
    """Wrapper service for rest interactions"""

    def __init__(self,
                 ca_url: str = '',
                 ssl_verify: bool = True,
                 timeout: int = 300,
                 logger: logging.Logger = None):
        """
        Constructor for RestService
        :param ca_url: The {gateway} before /v1/api endpoint for Cognos Analytics
        :param ver: always v1
        :param ssl_verify: Normally set to True, but if having SSL/TLS cert validation issues, 
            can turn off with False
        :param logger: (optional) If your app has a logger, pass it in here.
        """
        self._logger = logger or logging.getLogger(__name__)
        self.url = ca_url
        self._timeout = timeout
        self._headers = {}
        self._ssl_verify = ssl_verify
        self._session = requests.Session()
        # setup a retry mechanism on set of error codes
        # along the lines of 
        # https://www.peterbe.com/plog/best-practice-with-retries-with-requests
        retries = 3
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=0.3,
            status_forcelist=(400, 500, 502, 504),
            method_whitelist=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount('http://', adapter)
        self._session.mount('https://', adapter)
        if not ssl_verify:
            requests.urllib3.disable_warnings()

    def get_http_header(self, key: str) -> str:
        """get header"""
        return self._headers[key]

    def add_http_header(self, key: str, value: str):
        """add header"""
        self._headers[key] = value

    def remove_http_header(self, key: str):
        """remove header"""
        if key in self._headers:
            self._headers.pop(key)

    def get_cookie(self, key: str) -> str:
        """get header"""
        return self._session.cookies[key]

    def add_cookie(self, key: str, value: str):
        """add header"""
        self._session.cookies[key] = value

    def remove_cookie(self, key: str):
        """remove header"""
        if key in self._session.cookies:
            self._session.cookies.pop(key)

    def _do(self,
            http_method: str,
            endpoint: str,
            params: Dict = None,
            data: Dict = None
            ) -> RestResponse:
        """
        Private method for get(), post(), delete(), etc. methods
        :param http_method: GET, POST, DELETE, etc.
        :param endpoint: URL Endpoint as a string
        :param params: Dictionary of Endpoint parameters (Optional)
        :param data: Dictionary of data to pass to (Optional)
        :return: a Result object
        """
        full_url = self.url + endpoint

        log_line_pre = f"method={http_method}, url={full_url}, params={params}"
        # Log HTTP params and perform an HTTP request, catching and re-raising any exceptions
        try:
            self._logger.debug(msg=log_line_pre)
            response = self._session.request(method=http_method,
                                             url=full_url,
                                             params=params,
                                             json=data,
                                             headers=self._headers,
                                             timeout=self._timeout,
                                             verify=self._ssl_verify
                                             )
            # print(dump.dump_all(response).decode("utf-8"))
            response.raise_for_status()
            #TODO: should I pass through all the status codes like 404, etc?
        except requests.exceptions.RequestException as exc:
            self._logger.error(msg=str(exc))
            if response.status_code in [409,500]:
                  return RestResponse(response.status_code,
                            message=response.reason,
                            data={})
            else:    
                raise RestServiceException("Request failed") from exc
        data_out = {}
        if response.content:
            # Deserialize JSON output to Python object
            try:
                data_out = json.loads(response.content)
            except (ValueError, JSONDecodeError):
                # return the whole response content
                data_out = {'data':response.content}
                
        log_line = log_line_pre + \
            f": status_code={response.status_code}, message={response.reason}"
        self._logger.debug(msg=log_line)
        return RestResponse(response.status_code,
                            message=response.reason,
                            data=data_out)

    def get(self, endpoint: str, params: Dict = None) -> RestResponse:
        """get method wrapper"""
        return self._do(http_method='GET', endpoint=endpoint, params=params)

    def post(self, endpoint: str, params: Dict = None, data: Dict = None) -> RestResponse:
        """post method wrapper"""
        return self._do(http_method='POST', endpoint=endpoint, params=params, data=data)

    def put(self, endpoint: str, params: Dict = None, data: Dict = None) -> RestResponse:
        """put method wrapper"""
        return self._do(http_method='PUT', endpoint=endpoint, params=params, data=data)

    def delete(self, endpoint: str, params: Dict = None, data: Dict = None) -> RestResponse:
        """delete method wrapper"""
        return self._do(http_method='DELETE', endpoint=endpoint, params=params, data=data)
