import json
import logging
from functools import partial
from collections import defaultdict

import requests
import pickle


logger = logging.getLogger(__name__)


class RESTError(Exception):

    def __init__(self, response):
        self.status = response.status_code
        self.content = response.content
        super(RESTError, self).__init__(
            '{s} {c}'.format(s=self.status, c=self.content))


class RESTResource(object):

    def __init__(self, uri):
        self._uri = uri
        self._resources = {}
        self.encode = partial(json.dumps)
        self.decode = partial(json.loads)
        self._config()

    @property
    def id(self):
        return '/'.join(self._uri.parts[2:])

    def _config(self, error_mappings=None, ttl=36000):
        self.error_mappings = error_mappings
        if self.error_mappings is None:
            self.error_mappings = defaultdict(lambda: RESTError)
        self.ttl = ttl

    def get(self, **params):
        return self.decode(self._get(**params))

    def _get(self, **params):
        res = requests.get(str(self._uri), params=params)
        self._handle_response(res)
        return res.content

    def post(self, data):
        res = requests.post(str(self._uri), self.encode(data))
        self._handle_response(res)
        resource = RESTResource(URI(res.headers['location']))
        resource._config(ttl=self.ttl, error_mappings=self.error_mappings)
        return resource

    def delete(self):
        res = requests.delete(str(self._uri))
        self._handle_response(res)

    def put(self, data):
        res = requests.put(str(self._uri), self.encode(data))
        self._handle_response(res)

    def patch(self, **data):
        res = requests.patch(str(self._uri), self.encode(data))
        self._handle_response(res)

    def _handle_response(self, response):
        if not response.ok:
            self._log(logging.ERROR, response)
            error = self.error_mappings[response.status_code]
            raise error(response)
        else:
            self._log(logging.DEBUG, response)

    def _get_resource(self, id):
        uri = self._uri + id
        try:
            return self._resources[id]
        except KeyError:
            self._resources[id] = RESTResource(uri)
            self._resources[id]._config(ttl=self.ttl,
                                        error_mappings=self.error_mappings)
            return self._resources[id]

    def __getitem__(self, key):
        return self._get_resource(key)

    def __getattr__(self, name):
        return self._get_resource(name)

    def _log(self, level, response):
        message = "{method} {url} = {status} {content}"
        logger.log(level, message.format(
            method=response.request.method,
            url=response.request.url,
            status=response.status_code,
            content=response.content))


class URI(object):

    def __init__(self, uri):
        self._uri = uri.rstrip('/') + '/'

    @property
    def parts(self):
        return filter(lambda x: x, self._uri.split('/'))

    def __add__(self, part):
        part = part.strip('/')
        return URI(self._uri + part + '/')

    def __str__(self):
        return self._uri


def api(url):
    return RESTResource(URI(url))

