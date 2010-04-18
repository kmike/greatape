from urllib import urlencode, quote_plus
import urllib2
from functools import partial

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError('Ape requires either Python >2.6 or simplejson')


class MailChimpError(Exception):
    pass


class MailChimp(object):
    def __init__(self, api_key):
        self.data_center = api_key.rsplit('-', 1)[-1]
        self.api_key = api_key

    def __getattr__(self, name):
        return partial(self, method=name)

    def __call__(self, **kwargs):
        params = {
            'output': 'json',
            'apikey': self.api_key,
            'method': kwargs.pop('method')
        }
        querystring = '%s&%s' % (urlencode(params), self._serialize(kwargs))
        req = urllib2.Request(
                "https://%s.api.mailchimp.com/1.2/?%s" % (
                    self.data_center, querystring))
        try:
            handle = urllib2.urlopen(req)
            response = json.loads(handle.read())
            if 'error' in response:
                raise MailChimpError(response['error'])
        except urllib2.HTTPError, e:
            if (e.code == 304):
                return []
            else:
                raise MailChimpError

    def _serialize(self, params, key=None):
        """Replicates PHP's (incorrect) serialization to query parameters to
        accommodate the "array-based" parameters of MailChimp API methods.
        """
        pairs = []
        try:
            items = params.items()
        except AttributeError:
            items = [(str(i), n) for i, n in enumerate(params)]
        for name, value in items:
            name = quote_plus(name)
            if key is not None:
                name = '%s[%s]' % (key, name)
            if type(value) in (list, dict):
                pairs.append(self._serialize(value, name))        
            elif value is not None:
                if type(value) == bool:
                    value = str(value).lower()
                pairs.append('%s=%s' % (name, quote_plus(value)))
        return '&'.join(pairs)


__all__ = ["MailChimp", "MailChimpError"]
