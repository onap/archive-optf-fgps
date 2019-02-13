#
# -------------------------------------------------------------------------
#   Copyright (c) 2019 AT&T Intellectual Property
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2016 AT&T
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.


import base64
import json
import requests

from valet.utils.decryption import decrypt


class REST(object):
    """Helper class for REST operations."""

    def __init__(self, hosts, port, path, timeout, retries,
                 userid, password, ns, logger):
        """Initializer. Accepts target host list, port, and path."""

        self.hosts = hosts   # List of IP or FQDNs
        self.port = port   # Port Number
        self.path = path   # Path starting with /
        self.timeout = float(timeout)   # REST request timeout in seconds
        self.retries = retries   # Retires before failing over to next Music server.
        self.userid = userid
        self.password = password
        self.ns = ns
        self.logger = logger  # For logging

        self.urls = []
        for host in self.hosts:
            # Must end without a slash
            self.urls.append('http://%(host)s:%(port)s%(path)s' % {
                'host': host,
                'port': self.port,
                'path': self.path,
            })

    def __headers(self, content_type='application/json'):
        """Returns HTTP request headers."""

        headers = {
            'ns': self.ns,
            'accept': content_type,
            'content-type': content_type,
            'authorization': 'Basic %s' % base64.b64encode(self.userid + ':' + self.password)
        }

        return headers

    def request(self, method='get', content_type='application/json', path='/',
                data=None, raise400=True):
        """ Performs HTTP request """

        if method not in ('post', 'get', 'put', 'delete'):
            raise KeyError("Method must be: post, get, put, or delete.")

        method_fn = getattr(requests, method)

        if data:
            data_json = json.dumps(data)
        else:
            data_json = None

        response = None
        timeout = False
        err_message = ""
        full_url = ""
        for url in self.urls:
            # Try each url in turn. First one to succeed wins.
            full_url = url + path

            for attempt in range(self.retries):
                # Ignore the previous exception.
                try:
                    my_headers = self.__headers(content_type)
                    for header_key in my_headers:
                        if (type(my_headers[header_key]).__name__ == 'unicode'):
                            my_headers[header_key] = my_headers[header_key].encode('ascii', 'ignore')
                    response = method_fn(full_url, data=data_json,
                                         headers=my_headers,
                                         timeout=self.timeout)
                    if raise400 or not response.status_code == 400:
                        response.raise_for_status()
                    return response

                except requests.exceptions.Timeout as err:
                    err_message = err.message
                    response = requests.Response()
                    response.url = full_url
                    if not timeout:
                        self.logger.warning("Music: %s Timeout" % url, errorCode='availability')
                        timeout = True

                except requests.exceptions.RequestException as err:
                    err_message = err.message
                    self.logger.debug("Music: %s Request Exception" % url)
                    self.logger.debug(" method = %s" % method)
                    self.logger.debug(" timeout = %s" % self.timeout)
                    self.logger.debug(" err = %s" % err)
                    self.logger.debug(" full url = %s" % full_url)
                    self.logger.debug(" request data = %s" % data_json)
                    self.logger.debug(" request headers = %s" % my_headers)
                    self.logger.debug(" status code = %s" % response.status_code)
                    self.logger.debug(" response = %s" % response.text)
                    self.logger.debug(" response headers = %s" % response.headers)

        # If we get here, an exception was raised for every url,
        # but we passed so we could try each endpoint. Raise status
        # for the last attempt (for now) so that we report something.
        if response is not None:
            self.logger.debug("Music: Full Url: %s", full_url)
            self.logger.debug("Music: %s ", err_message)
            response.raise_for_status()


class Music(object):
    """Wrapper for Music API"""

    def __init__(self, _config, _logger):
        """Initializer. Accepts a lock_timeout for atomic operations."""

        self.logger = _logger

        pw = decrypt(_config["engine"]["ek"],
                     _config["logging"]["lk"],
                     _config["db"]["dk"],
                     _config["music"]["password"])

        kwargs = {
            'hosts': _config["music"]["hosts"],
            'port': _config["music"]["port"],
            'path': _config["music"]["path"],
            'timeout': _config["music"]["timeout"],
            'retries': _config["music"]["retries"],
            'userid': _config["music"]["userid"],
            'password': pw,
            'ns': _config["music"]["namespace"],
            'logger': _logger,
        }
        self.rest = REST(**kwargs)

        self.lock_names = []
        self.lock_timeout = _config["music"]["lock_timeout"]

        self.replication_factor = _config["music"]["replication_factor"]

    @staticmethod
    def __row_url_path(keyspace, table, pk_name=None, pk_value=None):
        """Returns a Music-compliant row URL path."""

        path = '/keyspaces/%(keyspace)s/tables/%(table)s/rows' % {
            'keyspace': keyspace,
            'table': table,
        }

        if pk_name and pk_value:
            path += '?%s=%s' % (pk_name, pk_value)

        return path

    def create_keyspace(self, keyspace):
        """Creates a keyspace."""

        data = {
            'replicationInfo': {
                #  'class': 'NetworkTopologyStrategy',
                #  'dc1': self.replication_factor,
                'class': 'SimpleStrategy',
                'replication_factor': self.replication_factor,
            },
            'durabilityOfWrites': True,
            'consistencyInfo': {
                'type': 'eventual',
            },
        }

        path = '/keyspaces/%s' % keyspace
        response = self.rest.request(method='post', path=path, data=data)

        return response.ok

    def drop_keyspace(self, keyspace):
        """Drops a keyspace."""

        data = {
            'consistencyInfo': {
                'type': 'eventual',
            },
        }

        path = '/keyspaces/%s' % keyspace
        response = self.rest.request(method='delete', path=path, data=data)

        return response.ok

    def create_table(self, keyspace, table, schema):
        """Creates a table."""

        data = {
            'fields': schema,
            'consistencyInfo': {
                'type': 'eventual',
            },
        }
        self.logger.debug(data)

        path = '/keyspaces/%(keyspace)s/tables/%(table)s' % {
            'keyspace': keyspace,
            'table': table,
        }

        response = self.rest.request(method='post', path=path, data=data)

        return response.ok

    def create_index(self, keyspace, table, index_field, index_name=None):
        """Creates an index for the referenced table."""

        data = None
        if index_name:
            data = {
                'index_name': index_name,
            }

        pstr = '/keyspaces/%(keyspace)s/tables/%(table)s/index/%(index_field)s'
        path = pstr % {
            'keyspace': keyspace,
            'table': table,
            'index_field': index_field,
        }

        response = self.rest.request(method='post', path=path, data=data)

        return response.ok

    def version(self):
        """Returns version string."""

        path = '/version'
        response = self.rest.request(method='get', content_type='text/plain', path=path)

        return response.text

    def create_lock(self, lock_name):
        """Returns the lock id. Use for acquiring and releasing."""

        path = '/locks/create/%s' % lock_name
        response = self.rest.request(method='post', path=path)

        return json.loads(response.text)["lock"]["lock"]

    def acquire_lock(self, lock_id):
        """Acquire a lock."""

        path = '/locks/acquire/%s' % lock_id
        response = self.rest.request(method='get', path=path, raise400=False)

        return json.loads(response.text)["status"] == "SUCCESS"

    def release_lock(self, lock_id):
        """Release a lock."""

        path = '/locks/release/%s' % lock_id
        response = self.rest.request(method='delete', path=path)

        return response.ok

    def delete_lock(self, lock_name):
        """Deletes a lock by name."""

        path = '/locks/delete/%s' % lock_name
        response = self.rest.request(method='delete', path=path, raise400=False)

        return response.ok

    def delete_all_locks(self):
        """Delete all locks created during the lifetime of this object."""

        # TODO(JD): Shouldn't this really be part of internal cleanup?
        # FIXME: It can be several API calls. Any way to do in one fell swoop?
        for lock_name in self.lock_names:
            self.delete_lock(lock_name)

    def create_row(self, keyspace, table, values):
        """Create a row."""

        # self.logger.debug("MUSIC: create_row "+ table)

        data = {
            'values': values,
            'consistencyInfo': {
                'type': 'eventual',
            },
        }

        path = '/keyspaces/%(keyspace)s/tables/%(table)s/rows' % {
            'keyspace': keyspace,
            'table': table,
        }
        response = self.rest.request(method='post', path=path, data=data)

        return response.ok

    def insert_atom(self, keyspace, table, values, name=None, value=None):
        """Atomic create/update row."""

        data = {
            'values': values,
            'consistencyInfo': {
                'type': 'atomic', 
            } 
        }

        path = self.__row_url_path(keyspace, table, name, value)
        method = 'post'

        # self.logger.debug("MUSIC: Method: %s ", (method.upper()))
        # self.logger.debug("MUSIC: Path: %s", (path))
        # self.logger.debug("MUSIC: Data: %s", (data))

        self.rest.request(method=method, path=path, data=data)

    def update_row_eventually(self, keyspace, table, values):
        """Update a row. Not atomic."""

        data = {
            'values': values,
            'consistencyInfo': {
                'type': 'eventual',
            },
        }

        path = self.__row_url_path(keyspace, table)
        response = self.rest.request(method='post', path=path, data=data)

        return response.ok

    def delete_row_eventually(self, keyspace, table, pk_name, pk_value):
        """Delete a row. Not atomic."""

        data = {
            'consistencyInfo': {
                'type': 'eventual',
            },
        }

        path = self.__row_url_path(keyspace, table, pk_name, pk_value)
        response = self.rest.request(method='delete', path=path, data=data)

        return response.ok

    def delete_atom(self, keyspace, table, pk_name, pk_value):
        """Atomic delete row."""

        data = {
            'consistencyInfo': {
                'type': 'atomic', 
            } 
        }
        path = self.__row_url_path(keyspace, table, pk_name, pk_value)
        self.rest.request(method='delete', path=path, data=data)

    def read_row(self, keyspace, table, pk_name, pk_value):
        """Read one row based on a primary key name/value."""

        path = self.__row_url_path(keyspace, table, pk_name, pk_value)
        response = self.rest.request(path=path) 
        return response.json()

    def read_all_rows(self, keyspace, table):
        """Read all rows."""

        return self.read_row(keyspace, table, pk_name=None, pk_value=None)
