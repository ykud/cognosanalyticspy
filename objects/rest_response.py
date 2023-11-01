"""Rest response attributes"""
from typing import List, Dict


class RestResponse:
    """wrapper for response of rest service"""    
    def __init__(self, 
                 status_code: int, 
                 message: str = '', 
                 data: List[Dict] = None
                 ):
        """
        Result returned from low-level RestService
        :param status_code: Standard HTTP Status code
        :param cookies: cookie jar of the request
        :param headers: request headers
        :param message: Human readable result
        :param data: Python List of Dictionaries (or maybe just a single Dictionary on error)
        """
        self.status_code = int(status_code)
        self.message = str(message)
        self.data = data if data else []