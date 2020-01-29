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


from valet.engine.resource_manager.resources.host import Host


class ComputeManager(object):
    """Resource Manager to maintain compute host resources."""

    def __init__(self, _source, _logger):
        """Define compute hosts and server allocations."""

        self.source = _source

        self.hosts = {}

        self.logger = _logger

    def get_hosts(self, _resource):
        """Check any inconsistency and perform garbage collection if necessary."""

        self.logger.info("set compute hosts...")

        # Init first
        self.hosts.clear()

        # Get available hosts only
        if self.source.get_hosts(self.hosts) != "ok":
            self.logger.warning("fail to set hosts from source (e.g., nova)")
            return False

        # Get servers
        if self.source.get_servers_in_hosts(self.hosts) != "ok":
            self.logger.warning("fail to set servers from source (e.g., nova)")
            return False

        self._check_host_updated(_resource)

        self._check_server_placements(_resource)

        return True

    def _check_host_updated(self, _resource):
        """Check if hosts and their properties are changed."""

        for hk in self.hosts.keys():
            if hk not in _resource.hosts.keys():
                _resource.hosts[hk] = Host(hk)
                _resource.mark_host_updated(hk)

                self.logger.info("new host (" + hk + ") added")

        for rhk in _resource.hosts.keys():
            if rhk not in self.hosts.keys():
                _resource.hosts[rhk].status = "disabled"
                _resource.mark_host_updated(rhk)

                self.logger.info("host (" + rhk + ") disabled")

        for hk in self.hosts.keys():
            host = self.hosts[hk]
            rhost = _resource.hosts[hk]

            if self._is_host_resources_updated(host, rhost):
                _resource.mark_host_updated(hk)

    def _is_host_resources_updated(self, _host, _rhost):
        """Check the resource amount consistency."""

        resource_updated = False

        if _host.original_vCPUs != _rhost.original_vCPUs:
            _rhost.original_vCPUs = _host.original_vCPUs

            self.logger.info("host (" + _rhost.name + ") updated (origin CPU updated)")
            resource_updated = True

        if _host.vCPUs_used != _rhost.vCPUs_used:
            _rhost.vCPUs_used = _host.vCPUs_used

            self.logger.info("host (" + _rhost.name + ") updated (CPU updated)")
            resource_updated = True

        if _host.original_mem_cap != _rhost.original_mem_cap:
            _rhost.original_mem_cap = _host.original_mem_cap

            self.logger.info("host (" + _rhost.name + ") updated (origin mem updated)")
            resource_updated = True

        if _host.free_mem_mb != _rhost.free_mem_mb:
            _rhost.free_mem_mb = _host.free_mem_mb

            self.logger.info("host (" + _rhost.name + ") updated (mem updated)")
            resource_updated = True

        if _host.original_local_disk_cap != _rhost.original_local_disk_cap:
            _rhost.original_local_disk_cap = _host.original_local_disk_cap

            self.logger.info("host (" + _rhost.name + ") updated (origin disk updated)")
            resource_updated = True

        if _host.free_disk_gb != _rhost.free_disk_gb:
            _rhost.free_disk_gb = _host.free_disk_gb

            self.logger.info("host (" + _rhost.name + ") updated (local disk space updated)")
            resource_updated = True

        if _host.disk_available_least != _rhost.disk_available_least:
            _rhost.disk_available_least = _host.disk_available_least

            self.logger.info("host (" + _rhost.name + ") updated (least disk space updated)")
            resource_updated = True

        return resource_updated

    def _check_server_placements(self, _resource):
        """Check the consistency of server placements with nova."""

        # To keep how server placements changed.
        # key =
        #     If uuid is available, uuid
        #     Else stack_id:name
        # value = {new_host, old_host, server_info}
        # The server's state must be either 'created', 'migrated', or 'rebuilt'.
        # That is, deal with only the server which placement decision is confirmed.
        #     If value of new_host (from nova) exists but not for old_host (valet),
        #        the server is unknown one to valet.
        #     If value of new_host not exists but exist for old_host,
        #        the server is deleted by nova.
        #     If value exists both in new_host and old_host,
        #        the server is moved from old to new host.
        #     If value not exist neither,
        #        the server is placed as planned.
        change_of_placements = {}

        for hk, host in self.hosts.items():
            rhost = _resource.hosts[hk]

            for s_info in host.server_list:
                if s_info["stack_id"] != "none":
                    sid = s_info["stack_id"] + ":" + s_info["name"]
                else:
                    sid = s_info["uuid"]

                change_of_placements[sid] = {}
                change_of_placements[sid]["info"] = s_info

                if not rhost.has_server(s_info):
                    change_of_placements[sid]["new_host"] = hk

                    self.logger.info("host (" + hk + ") updated (server added)")
                else:
                    change_of_placements[sid]["host"] = hk

        for rhk, rhost in _resource.hosts.items():
            if not rhost.is_available():
                continue

            host = self.hosts[rhk]

            for s_info in rhost.server_list:
                # Deal with confirmed placements only.
                if s_info["state"] not in ("created", "migrated", "rebuilt"):
                    continue

                if s_info["stack_id"] != "none":
                    sid = s_info["stack_id"] + ":" + s_info["name"]
                else:
                    sid = s_info["uuid"]

                if not host.has_server(s_info):
                    if sid in change_of_placements.keys():
                        change_of_placements[sid]["old_host"] = rhk

                        self.logger.info("server (" + sid + ") is migrated`")
                    else:
                        change_of_placements[sid] = {}
                        change_of_placements[sid]["old_host"] = rhk
                        change_of_placements[sid]["info"] = s_info

                        self.logger.info("server (" + sid + ") is deleted")

        _resource.change_of_placements = change_of_placements
