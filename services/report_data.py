"""Cognos Mashup Services 
https://www.ibm.com/docs/en/cognos-analytics/11.2.0?topic=developer-developing-mashup-service-applications-using-rest-interface
"""
import logging
from services.rest import RestService



class ReportDataService:
    """ CMS related endpoints"""

    def __init__(self, rest: RestService, logger: logging.Logger = None):
        """ Initiate the Service
        """
        self._ca_rest = rest
        self._base_endpoint = '/v1/disp/rds'
        self._logger = logger or logging.getLogger(__name__)

    def login(self, namespace="", user="", password=""):    
        """	THIS IS NOT NEEDED for running reports. logging into CA REST is enough
        but this login is required for getting the XSRF-TOKEN 
        that is required to use the non-api based services (like namespaces)
        try logging in CMS with provided credentials
        https://www.ibm.com/support/pages/mashup-using-rest-url-logon-ibm-cognos-analytics-server
        """
        xml_credentials = f"""<credentials>
        <credentialElements>
            <name>CAMNamespace</name>
            <label>Namespace:</label>
            <value>
                <actualValue>{namespace}</actualValue>
            </value>
        </credentialElements>
        <credentialElements>
            <name>CAMUsername</name>
            <label>User ID:</label>
            <value><actualValue>{user}</actualValue></value>
        </credentialElements>
        <credentialElements>
            <name>CAMPassword</name>
            <label>Password:</label>
            <value><actualValue>{password}</actualValue></value>
        </credentialElements>
        </credentials>"""
        response = self._ca_rest.post(endpoint=f'{self._base_endpoint}/auth/logon?xmlData={xml_credentials}')
        if response.status_code == 200:
            # Copying the XSRF token header to be able to login to other services if need be
            # https://developer.ibm.com/apis/catalog/cognosanalytics--cognos-analytics-rest-api/Getting%20Started
            self._ca_rest.add_http_header(
                key="X-XSRF-Token",
                value=self._ca_rest.get_cookie('XSRF-TOKEN'))
            logging.info('Logged into Cognos Mashup Services as %s\\%s',namespace,user)
        else:
            logging.error('Failed to login into Cognos Mashup Services as %s\\%s',namespace,user)

    def run_report_sync(self, 
                        reportid:str,
                        report_object:str='',
                        fmt:str = 'DataSetJSON',
                        row_limit:int = 0)-> dict :
        """	run a report synchroniously and return the resulting dataset in JSON
        """
        logging.debug("Running Cognos report %s with the object %s ",reportid, report_object)
        params = {'v':3, 'async':'OFF','fmt':fmt} 
        if report_object != '':
            params['selection'] = report_object
        if row_limit != 0:
            params['row_limit'] = row_limit
        response = self._ca_rest.post(
            endpoint=f'{self._base_endpoint}/reportData/report/{reportid}',params=params)
        if response.status_code == 200:
            return response.data
    