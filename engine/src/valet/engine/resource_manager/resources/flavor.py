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
import six


class Flavor(object):
    """Container for flavor resource."""

    def __init__(self, _name):
        self.name = _name

        self.flavor_id = None

        self.status = "enabled"

        self.vCPUs = 0
        self.mem_cap = 0        # MB
        self.disk_cap = 0       # including ephemeral (GB) and swap (MB)

        self.extra_specs = {}

        self.updated = False

    def set_info(self, _f):
        """Copy detailed flavor information."""

        self.status = _f.status

        self.vCPUs = _f.vCPUs
        self.mem_cap = _f.mem_cap
        self.disk_cap = _f.disk_cap

        for ek, ev in _f.extra_specs.iteritems():
            self.extra_specs[ek] = ev

    def need_numa_alignment(self):
        """Check if this flavor requires NUMA alignment."""

        for key, req in six.iteritems(self.extra_specs):
            if key == "hw:numa_nodes" and int(req) == 1:
                return True

        return False

    def get_json_info(self):
        return {'status': self.status,
                'flavor_id': self.flavor_id,
                'vCPUs': self.vCPUs,
                'mem': self.mem_cap,
                'disk': self.disk_cap,
                'extra_specs': self.extra_specs}
