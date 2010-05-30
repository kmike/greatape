from urllib import urlencode, quote_plus
from datetime import datetime, date
import urllib2

try:
    import functools
    partial = functools.partial
except ImportError:
    def partial(func, *args, **keywords):
        def newfunc(*fargs, **fkeywords):
            newkeywords = keywords.copy()
            newkeywords.update(fkeywords)
            return func(*(args + fargs), **newkeywords)
        newfunc.func = func
        newfunc.args = args
        newfunc.keywords = keywords
        return newfunc


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
    def __init__(self, api_key, ssl=True, debug=False):
        self.data_center = api_key.rsplit('-', 1)[-1]
        self.api_key = api_key
        self.ssl = ssl
        self.debug = debug

    def __getattr__(self, name):
        return partial(self, method=name)

    def __call__(self, **kwargs):
        method = kwargs.pop('method')
        kwargs.update({
            'output': 'json',
            'apikey': self.api_key,
        })
        params = self._serialize(kwargs)
        if self.ssl:
            protocol = 'https'
        else:
            protocol = 'http'
        url = "%s://%s.api.mailchimp.com/1.2/?method=%s" % (
                    protocol, self.data_center, method)
        if self.debug:
            print 'URL:', url
            print 'POST data:', params
        req = urllib2.Request(url, params)
        try:
            handle = urllib2.urlopen(req)
            response = json.loads(handle.read())
            try:
                if 'error' in response:
                    raise MailChimpError(response['error'])
            except TypeError: # the response was boolean
                pass
            return response
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
                if type(value) in (bool, datetime, date, int):
                    value = str(value).lower()
                pairs.append('%s=%s' % (name, quote_plus(value)))
        return '&'.join(pairs)


__all__ = ["MailChimp", "MailChimpError"]
