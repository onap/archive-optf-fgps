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
class Group(object):
    """Container for groups."""

    def __init__(self, _name):
        """Define logical group of compute hosts."""

        self.name = _name

        self.uuid = None

        # Group includes
        # - host-aggregate, availability-zone, 
        # - server groups: affinity, diversity, soft-affinity, soft-diversity, 
        # - affinity, diversity, quorum-diversity, exclusivity
        self.group_type = None

        self.level = None

        # Where the group is originated
        # - 'valet' or 'nova' or 'server-group' or other cloud platform
        self.factory = None

        self.status = "enabled"

        # A list of host_names and their placed servers
        # Value is a list of server infos.
        self.member_hosts = {}

        # For Host-Aggregate group
        self.metadata = {}

        # Group rule object for valet groups
        self.rule = None

        # A list of placed servers (e.g., VMs)
        # Value is a list of server infos.
        self.server_list = []

        self.updated = False

        self.new = False

    def has_server(self, _s_info):
        """Check if the server exists in this group."""

        for s_info in self.server_list:
            if _s_info["uuid"] != "none":
                if s_info["uuid"] != "none" and \
                   s_info["uuid"] == _s_info["uuid"]:
                    return True

            if _s_info["stack_id"] != "none":
                if (s_info["stack_id"] != "none" and \
                    s_info["stack_id"] == _s_info["stack_id"]) and \
                   s_info["name"] == _s_info["name"]:
                    return True

            if _s_info["stack_name"] != "none":
                if (s_info["stack_name"] != "none" and \
                    s_info["stack_name"] == _s_info["stack_name"]) and \
                   s_info["name"] == _s_info["name"]:
                    return True

        return False

    def has_server_uuid(self, _uuid):
        """Check if the server exists in this group with uuid."""

        for s_info in self.server_list:
            if s_info["uuid"] == _uuid:
                return True

        return False

    def has_server_in_host(self, _host_name, _s_info):
        """Check if the server exists in the host in this group."""

        if _host_name in self.member_hosts.keys():
            server_list = self.member_hosts[_host_name]

            for s_info in server_list:
                if _s_info["uuid"] != "none":
                    if s_info["uuid"] != "none" and \
                       s_info["uuid"] == _s_info["uuid"]:
                        return True

                if _s_info["stack_id"] != "none":
                    if (s_info["stack_id"] != "none" and \
                        s_info["stack_id"] == _s_info["stack_id"]) and \
                       s_info["name"] == _s_info["name"]:
                        return True

                if _s_info["stack_name"] != "none":
                    if (s_info["stack_name"] != "none" and \
                        s_info["stack_name"] == _s_info["stack_name"]) and \
                       s_info["name"] == _s_info["name"]:
                        return True

        return False

    def get_server_info(self, _s_info):
        """Get server info."""

        for s_info in self.server_list:
            if _s_info["uuid"] != "none":
                if s_info["uuid"] != "none" and \
                   s_info["uuid"] == _s_info["uuid"]:
                    return s_info

            if _s_info["stack_id"] != "none":
                if (s_info["stack_id"] != "none" and \
                    s_info["stack_id"] == _s_info["stack_id"]) and \
                   s_info["name"] == _s_info["name"]:
                    return s_info

            if _s_info["stack_name"] != "none":
                if (s_info["stack_name"] != "none" and \
                    s_info["stack_name"] == _s_info["stack_name"]) and \
                   s_info["name"] == _s_info["name"]:
                    return s_info

        return None

    def get_server_info_in_host(self, _host_name, _s_info):
        """Get server info."""

        if _host_name in self.member_hosts.keys():
            server_list = self.member_hosts[_host_name]

            for s_info in server_list:
                if _s_info["uuid"] != "none":
                    if s_info["uuid"] != "none" and \
                       s_info["uuid"] == _s_info["uuid"]:
                        return s_info

                if _s_info["stack_id"] != "none":
                    if (s_info["stack_id"] != "none" and \
                        s_info["stack_id"] == _s_info["stack_id"]) and \
                       s_info["name"] == _s_info["name"]:
                        return s_info

                if _s_info["stack_name"] != "none":
                    if (s_info["stack_name"] != "none" and \
                        s_info["stack_name"] == _s_info["stack_name"]) and \
                       s_info["name"] == _s_info["name"]:
                        return s_info

        return None

    def add_server(self, _s_info, _host_name):
        """Add server to this group."""

        if self.has_server(_s_info):
            return False

        if self.has_server_in_host(_host_name, _s_info):
            return False

        self.server_list.append(_s_info)

        if self.factory in ("valet", "server-group"):
            if _host_name not in self.member_hosts.keys():
                self.member_hosts[_host_name] = []

            self.member_hosts[_host_name].append(_s_info)

        return True

    def remove_server(self, _s_info):
        """Remove server from this group's server_list."""

        for s_info in self.server_list:
            if _s_info["uuid"] != "none":
                if s_info["uuid"] != "none" and \
                   s_info["uuid"] == _s_info["uuid"]:
                    self.server_list.remove(s_info)
                    return True

            if _s_info["stack_id"] != "none":
                if (s_info["stack_id"] != "none" and \
                    s_info["stack_id"] == _s_info["stack_id"]) and \
                   s_info["name"] == _s_info["name"]:
                    self.server_list.remove(s_info)
                    return True

            if _s_info["stack_name"] != "none":
                if (s_info["stack_name"] != "none" and \
                    s_info["stack_name"] == _s_info["stack_name"]) and \
                   s_info["name"] == _s_info["name"]:
                    self.server_list.remove(s_info)
                    return True

        return False

    def remove_server_from_host(self, _host_name, _s_info):
        """Remove server from the host of this group."""

        if _host_name in self.member_hosts.keys():
            for s_info in self.member_hosts[_host_name]:
                if _s_info["uuid"] != "none":
                    if s_info["uuid"] != "none" and \
                       s_info["uuid"] == _s_info["uuid"]:
                        self.member_hosts[_host_name].remove(s_info)
                        return True

                if _s_info["stack_id"] != "none":
                    if (s_info["stack_id"] != "none" and \
                        s_info["stack_id"] == _s_info["stack_id"]) and \
                       s_info["name"] == _s_info["name"]:
                        self.member_hosts[_host_name].remove(s_info)
                        return True

                if _s_info["stack_name"] != "none":
                    if (s_info["stack_name"] != "none" and \
                        s_info["stack_name"] == _s_info["stack_name"]) and \
                       s_info["name"] == _s_info["name"]:
                        self.member_hosts[_host_name].remove(s_info)
                        return True

        return False

    def remove_member(self, _host_name):
        """Remove the host from this group's memberships if it is empty.

        To return the host to pool for other placements.
        """

        if self.factory in ("valet", "server-group"):
            if _host_name in self.member_hosts.keys() and \
               len(self.member_hosts[_host_name]) == 0:
                del self.member_hosts[_host_name]

                return True

        return False

    def clean_server(self, _uuid, _host_name):
        """Clean the server that does not have enriched info."""

        if _uuid == "none":
            return

        for s_info in self.server_list:
            if s_info["uuid"] == _uuid and s_info["name"] == "none":
                self.server_list.remove(s_info)
                break

        if _host_name in self.member_hosts.keys():
            for s_info in self.member_hosts[_host_name]:
                if s_info["uuid"] == _uuid and s_info["name"] == "none":
                    self.member_hosts[_host_name].remove(s_info)
                    break

        if _host_name in self.member_hosts.keys() and \
           len(self.member_hosts[_host_name]) == 0:
            del self.member_hosts[_host_name]

    def update_server(self, _s_info):
        """Update server with info from given info.

        The info comes from platform or request (e.g., Heat stack).
        """

        updated = False

        s_info = self.get_server_info(_s_info)

        if s_info is not None:
            if _s_info["stack_id"] != "none" and \
               _s_info["stack_id"] != s_info["stack_id"]:
                s_info["stack_id"] = _s_info["stack_id"]
                updated = True

            if _s_info["uuid"] != "none" and \
               _s_info["uuid"] != s_info["uuid"]:
                s_info["uuid"] = _s_info["uuid"]
                updated = True

            if _s_info["flavor_id"] != "none" and \
               _s_info["flavor_id"] != s_info["flavor_id"]:
                s_info["flavor_id"] = _s_info["flavor_id"]
                updated = True

            if _s_info["vcpus"] != -1 and \
               _s_info["vcpus"] != s_info["vcpus"]:
                s_info["vcpus"] = _s_info["vcpus"]
                updated = True

            if _s_info["mem"] != -1 and \
               _s_info["mem"] != s_info["mem"]:
                s_info["mem"] = _s_info["mem"]
                updated = True

            if _s_info["disk"] != -1 and \
               _s_info["disk"] != s_info["disk"]:
                s_info["disk"] = _s_info["disk"]
                updated = True

            if _s_info["image_id"] != "none" and \
               _s_info["image_id"] != s_info["image_id"]:
                s_info["image_id"] = _s_info["image_id"]
                updated = True

            if _s_info["state"] != "none" and \
               _s_info["state"] != s_info["state"]:
                s_info["state"] = _s_info["state"]
                updated = True

            if _s_info["status"] != "none" and \
               _s_info["status"] != s_info["status"]:
                s_info["status"] = _s_info["status"]
                updated = True

            if _s_info["numa"] != "none" and \
               _s_info["numa"] != s_info["numa"]:
                s_info["numa"] = _s_info["numa"]
                updated = True

        return updated

    def update_server_in_host(self, _host_name, _s_info):
        """Updateserver in the host of this group."""

        if _host_name in self.member_hosts.keys():
            s_info = self.get_server_info_in_host(_host_name, _s_info)

            if s_info is not None:
                if _s_info["stack_id"] != "none" and \
                   _s_info["stack_id"] != s_info["stack_id"]:
                    s_info["stack_id"] = _s_info["stack_id"]

                if _s_info["uuid"] != "none" and \
                   _s_info["uuid"] != s_info["uuid"]:
                    s_info["uuid"] = _s_info["uuid"]

                if _s_info["flavor_id"] != "none" and \
                   _s_info["flavor_id"] != s_info["flavor_id"]:
                    s_info["flavor_id"] = _s_info["flavor_id"]

                if _s_info["vcpus"] != -1 and \
                   _s_info["vcpus"] != s_info["vcpus"]:
                    s_info["vcpus"] = _s_info["vcpus"]

                if _s_info["mem"] != -1 and \
                   _s_info["mem"] != s_info["mem"]:
                    s_info["mem"] = _s_info["mem"]

                if _s_info["disk"] != -1 and \
                   _s_info["disk"] != s_info["disk"]:
                    s_info["disk"] = _s_info["disk"]

                if _s_info["image_id"] != "none" and \
                   _s_info["image_id"] != s_info["image_id"]:
                    s_info["image_id"] = _s_info["image_id"]

                if _s_info["state"] != "none" and \
                   _s_info["state"] != s_info["state"]:
                    s_info["state"] = _s_info["state"]

                if _s_info["status"] != "none" and \
                   _s_info["status"] != s_info["status"]:
                    s_info["status"] = _s_info["status"]

                if _s_info["numa"] != "none" and \
                   _s_info["numa"] != s_info["numa"]:
                    s_info["numa"] = _s_info["numa"]

    def get_json_info(self):
        """Get group info as JSON format."""

        rule_id = "none"
        if self.rule is not None:
            rule_id = self.rule.rule_id

        return {'status': self.status,
                'uuid': self.uuid,
                'group_type': self.group_type,
                'level': self.level,
                'factory': self.factory,
                'rule_id': rule_id,
                'metadata': self.metadata,
                'server_list': self.server_list,
                'member_hosts': self.member_hosts}
