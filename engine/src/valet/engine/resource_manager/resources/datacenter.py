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
#!/bin/python


class Datacenter(object):
    """Container for datacenter resource."""

    def __init__(self, _name):
        self.name = _name

        self.status = "enabled"

        # Enabled group objects (e.g., aggregate)
        self.memberships = {}

        self.vCPUs = 0
        self.avail_vCPUs = 0

        self.mem_cap = 0   # MB
        self.avail_mem_cap = 0

        self.local_disk_cap = 0   # GB, ephemeral
        self.avail_local_disk_cap = 0

        # Enabled host_group (rack) or host objects
        self.resources = {}

        # A list of placed servers
        self.server_list = []

        self.updated = False

    def is_available(self):
        """Check if host is available."""

        if self.status == "enabled":
            return True
        else:
            return False

    def init_resources(self):
        self.vCPUs = 0
        self.avail_vCPUs = 0
        self.mem_cap = 0
        self.avail_mem_cap = 0
        self.local_disk_cap = 0
        self.avail_local_disk_cap = 0

    def get_json_info(self):
        membership_list = []
        for gk in self.memberships.keys():
            membership_list.append(gk)

        child_list = []
        for ck in self.resources.keys():
            child_list.append(ck)

        return {'status': self.status,
                'name': self.name,
                'membership_list': membership_list,
                'vCPUs': self.vCPUs,
                'avail_vCPUs': self.avail_vCPUs,
                'mem': self.mem_cap,
                'avail_mem': self.avail_mem_cap,
                'local_disk': self.local_disk_cap,
                'avail_local_disk': self.avail_local_disk_cap,
                'children': child_list,
                'server_list': self.server_list}
