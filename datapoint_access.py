import json
import urllib2

class DPRequest(object):

    """
    A class to construct and hold valid Met Office DataPoint url queries, and
    translate the query response into Pythonic data structures.

    Based on the information at http://www.metoffice.gov.uk/datapoint/api, the
    base query string for requests to DataPoint is:

        http://datapoint.metoffice.gov.uk/public/data/<resource>?key=<APIkey>

    where:

        * <resource> defines the scope of the data requested and in general
          is composed of:
          <data type>/<wx type>/<time period>/<data container>/<site id>

          in turn where:

              * <data type> is the type of data returned by the query.
                Valid options: 'val', 'txt', ('image', 'layer')
              * <wx type> is weather type for location(s) - forecast or obs
                Valid options: 'wxfcs', 'wxobs'
              * <time period> is the time period within which to retrieve data
                Valid options: 'all' [default], ...
              * <data container> is container language the data is returned in
                Valid options: json, (xml [not supported])
              * <site id> is the ID of a specific site returning weather data.
                The list of valid sites may be determined using the _sitelist_
                common request type.
                Valid options: 'all' [default], _number_ (e.g. 3840)

        * <APIkey> is a unique key needed to access and use DataPoint. You must
          register for DataPoint to receive your own API key.

        * Further, temporal resolution may be specified with the 'res' query,
          e.g. ?res=_n_hourly&...

    :Note:

        DataPoint can return images as well as text data. This is beyond the
        scope of this class, however, as it is designed only to request and
        translate text-based data.

    """
    data_types = ['val', 'txt']
    unsupported_data_types = ['image', 'layer']
    wx_types = ['wxfcs', 'wxobs']
    request_types = {'fcs_sites': 'val/wxfcs/all/{}/sitelist',
                     'fcs_capabilities': 'val/wxfcs/all/{}/capabilities',
                     'fcs_fiveday': 'val/wxfcs/all/{}/{}',
                     'obs_sites': 'val/wxobs/all/{}/sitelist',
                     'obs_capabilities': 'val/wxobs/all/{}/capabilities',
                     'obs_fiveday': 'val/wxobs/all/{}/{}'}


    def __init__(self, data_type, wx_type, api_key,
                 request_type=None, time_period='all', site_id='all',
                 **kwargs):
        """
        Define the variables to compose the query to DataPoint.

        Args:

            * data_type: the type of data to be returned ['val'|'txt'].
            * wx_type: weather data - forecast or obs ['wxfcs'|'wxobs'].
            * api_key: your API key used to access DataPoint.

        Keyword Args:
            
            * time_period: a valid time period or 'all' (default). Use the
              capabilities request to determine valid time periods.
            * site_id: the ID of an observing/forecast site or 'all' (default).
              Use the sitelist request to determine valid sites.
            * **kwargs: other keyword args, for specific keyword queries. For
              example:

                  * res: the temporal resolution of the data requested; an
                    integer value or `None` (default).
                  * query_time: to request data for a specific time; a string
                    of format yyyy-mm-ddThhZ or `None` (default).

        Other class constants:
            
            * base_url: the query base string, to be populated with
              relevant settings.
            * data_container: the fixed data container format (json). Fixed
              to keep the code simple so that only one format need be parsed.
            * request_str: base_url, but populated.
            * response: the response from the server: a json-formatted string
              or error code.
            * data: the json data in `self.response` converted to a Pythonic
              data structure.

        """
        self.data_type = data_type
        self.wx_type = wx_type
        self.api_key = api_key
        self.time_period = time_period
        self.site_id = site_id
        self.kwargs = kwargs
        self.base_url = 'http://datapoint.metoffice.gov.uk/public/data/{}?{}key={}'
        self.data_container = 'json'
        self.request_str = None
        self.http_code = None
        self.response = None
        self.data = None

    def _request(self):
        """
        Uses urllib2 to send the request and read the result. Catches http
        errors (response code != 200).

        """
        if self.request_str is not None:
            try:
                resp = urllib2.urlopen(self.request_str)
                self.response = resp.read()
            except urllib2.HTTPError:
                raise
        else:
            raise ValueError('Request string has not been set.')

    def query_string(self):
        """Prints the instance's query string."""

        if self.request_str is None:
            return self.base_url
        else:
            return self.request_str

    def common_requests(self, request_type):
        """
        DataPoint defines a number of 'common' requests, for example the
        get capabilities and get sitelist requests. This function simplifies
        access to these requests and catches request problems that would
        otherwise cause an http error to be returned.

        Arg:
            * request_type: a common request type or None (default).

        """
        c_keys = self.request_types.keys()

        if request_type in c_keys:
            wx, common_type = request_type.split('_')
            if common_type == 'fiveday' and self.locn_id == 'all':
                raise ValueError('Location ID cannot equal \'all\' for a '
                                 'five-day {} request'.format(wx))
            elif common_type == 'fiveday':
                resource = self.request_types[
                    request_type].format(self.data_container, self.locn_id)
            else:
                resource = self.request_types[
                    request_type].format(self.data_container)
        else:
            raise ValueError('Request type supplied does not match to the '
                             'following valid options:\n  {}'.format(c_keys()))

        self.build_request(resource=resource)

    def build_request(self, resource=None):
        """
        Builds the query string from the base string and input variables,
        notably the following elements:

            * resource: a URL element to fill the gap between `data/` and `?`.
            * query: to specify any query keywords, for example 'res'.

        Keyword arg:
            * resource: interface for :func:common_requests. If specified, this
              overrides this function's resource string builder.

        """
        if resource is None:
            resource = '{}/{}/{}/{}/{}'.format(self.data_type,
                                               self.wx_type,
                                               self.time_period,
                                               self.data_container,
                                               self.site_id)

        # Add a keyword query for each specified **kw:
        sub_query = '{}{}{}{}'
        query = ''
        for kw, val in self.kwargs.iteritems():
            if kw == 'res' and isinstance(val, int):
                query_end = 'hourly&'
            else:
                query_end = '&'
            query += sub_query.format(kw, '=', val, query_end)

        self.request_str = self.base_url.format(resource,
                                                query,
                                                self.api_key)
        print self.request_str
        print 'Requesting data, please wait...'
        self._request()

    def parse_response(self):
        """
        Converts the JSON response from DataPoint into a Pythonic data
        structure.

        :Note:

            As the JSON spec requires unicode strings, the parsed response
            will likewise be comprised of unicode strings.

        """
        if self.response is None:
            if self.request_str is not None:
                self._request()
            else:
                raise ValueError('Request string has not been defined.')
        self.data = json.loads(self.response)
        return self.data
