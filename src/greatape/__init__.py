import urllib
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
            'method': kwargs['method']
        }
        params.update(kwargs)
        req = urllib2.Request(
                "https://%s.api.mailchimp.com/1.2/?%s" % (
                    self.data_center, urllib.urlencode(params)))
        try:
            handle = urllib2.urlopen(req)
            return json.loads(handle.read())
        except urllib2.HTTPError, e:
            if (e.code == 304):
                return []
            else:
                raise MailChimpError


__all__ = ["MailChimp", "MailChimpError"]
