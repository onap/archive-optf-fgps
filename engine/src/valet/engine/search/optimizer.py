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
from valet.engine.app_manager.group import Group
from valet.engine.app_manager.server import Server
from valet.engine.search.search import Search


class Optimizer(object):
    """Optimizer to compute the optimal placements."""

    def __init__(self, _logger):
        self.logger = _logger

        self.search = Search(self.logger)

    def place(self, _app):
        """Scheduling placements given app."""

        _app.set_weight()
        _app.set_optimization_priority()

        if self.search.place(_app) is True:
            if _app.status == "ok":
                self._set_app(_app, "create")

                self._set_resource(_app)
                if _app.status != "ok":
                    return
        else:
            if _app.status == "ok":
                _app.status = "failed"

            self._rollback_placements(_app)

    def update(self, _app):
        """Update state of current placements."""

        if _app.state == "delete":
            self._update_app_for_delete(_app)

            self._update_resource(_app)
            if _app.status != "ok":
                return
        else:
            _app.status = "unknown state while updating app"

    def confirm(self, _app):
        """Confirm prior request."""

        if _app.state == "created":
            self._update_app(_app)
            if _app.status != "ok":
                return

            self._update_resource(_app)
            if _app.status != "ok":
                return
        elif _app.state == "deleted":
            self._remove_resource(_app)
            if _app.status != "ok":
                return
        else:
            _app.status = "unknown state while updating app"
            return

    def rollback(self, _app):
        """Rollback prior decision."""

        if _app.state == "created":
            self._update_app(_app)
            if _app.status != "ok":
                return

            self._update_resource(_app)
            if _app.status != "ok":
                return
        elif _app.state == "deleted":
            self._remove_resource(_app)
            if _app.status != "ok":
                return
        else:
            _app.status = "unknown state while updating app"

    def _set_app(self, _app, _state):
        """Update with assigned hosts."""

        for v, p in self.search.node_placements.iteritems():
            if isinstance(v, Server):
                v.host = p.host_name
                if p.rack_name != "any":
                    v.host_group = p.rack_name

                host = self.search.avail_hosts[p.host_name]

                s_info = {}
                if _app.app_id is None or _app.app_id == "none":
                    s_info["stack_id"] = "none"
                else:
                    s_info["stack_id"] = _app.app_id
                s_info["stack_name"] = _app.app_name
                s_info["uuid"] = "none"
                s_info["name"] = v.name

                v.numa = host.NUMA.pop_cell_of_server(s_info)

                v.state = _state

        # Put back servers from groups.
        _app.reset_servers()

    def _update_app(self, _app):
        """Update state of servers."""

        for sk, s in _app.servers.iteritems():
            if s["host"] == "none":
                continue

            s["state"] = _app.state

            host_name = s.get("host")

            host = None
            if host_name in _app.resource.hosts.keys():
                host = _app.resource.hosts[host_name]

            s_info = {}
            if _app.app_id is None or _app.app_id == "none":
                s_info["stack_id"] = "none"
            else:
                s_info["stack_id"] = _app.app_id
            s_info["stack_name"] = _app.app_name
            s_info["uuid"] = "none"
            s_info["name"] = s.get("name")

            # Check if the prior placements changed.
            if host is None or \
               not host.is_available() or \
               not host.has_server(s_info):
                _app.status = "server (" + sk + ") placement has been changed"
                self.logger.error(_app.status)

    def _update_app_for_delete(self, _app):
        """Check the prior placements and update state

        And update placements if they have been changed.
        """

        for sk, s in _app.servers.iteritems():
            if s["host"] == "none":
                continue

            s["state"] = _app.state

            host_name = s.get("host")

            host = None
            if host_name in _app.resource.hosts.keys():
                host = _app.resource.hosts[host_name]

            s_info = {}
            if _app.app_id is None or _app.app_id == "none":
                s_info["stack_id"] = "none"
            else:
                s_info["stack_id"] = _app.app_id
            s_info["stack_name"] = _app.app_name
            s_info["uuid"] = "none"
            s_info["name"] = s.get("name")

            # Check if the prior placements changed.
            if host is None or \
               not host.is_available() or \
               not host.has_server(s_info):
                self.logger.warning("server (" + sk + ") placement has been changed")

                new_host = _app.resource.get_host_of_server(s_info)

                if new_host is not None:
                    s["host"] = new_host.name
                else:
                    s["host"] = "none"
                    self.logger.warning("server (" + sk + ") not exists")

    def _set_resource(self, _app):
        """Update resource status based on new placements."""

        # If host's type (i.e., host-aggregate) is not determined before, 
        # Convert/set host's type to one as specified in VM.
        for v, p in self.search.node_placements.iteritems():
            if isinstance(v, Server):
                # The host object p was deep copied, so use original object.
                rh = self.search.avail_hosts[p.host_name]

                if rh.old_candidate_host_types is not None and len(rh.old_candidate_host_types) > 0:
                    flavor_type_list = v.get_flavor_types()
                    ha = self.search.avail_groups[flavor_type_list[0]]

                    self._convert_host(rh,
                                       ha.name,
                                       rh.get_host_type(ha, rh.old_candidate_host_types),
                                       _app.resource)

        placements = {}

        for v, p in self.search.node_placements.iteritems():
            if isinstance(v, Server):
                s_info = {}

                if _app.app_id is None or _app.app_id == "none":
                    s_info["stack_id"] = "none"
                else:
                    s_info["stack_id"] = _app.app_id
                s_info["stack_name"] = _app.app_name

                s_info["uuid"] = "none"
                s_info["orch_id"] = v.orch_id
                s_info["name"] = v.name

                s_info["flavor_id"] = v.flavor
                s_info["vcpus"] = v.vCPUs
                s_info["mem"] = v.mem
                s_info["disk"] = v.local_volume_size
                s_info["numa"] = v.numa

                s_info["image_id"] = v.image
                s_info["tenant_id"] = _app.tenant_id

                s_info["state"] = v.state
                s_info["status"] = "valid"

                placements[v.vid] = {}
                placements[v.vid]["new_host"] = p.host_name
                placements[v.vid]["info"] = s_info

        # Update compute host with new servers
        if not _app.resource.update_server_placements(change_of_placements=placements):
            _app.status = "fail while updating server placements"
            return

        groups = {}

        for v, p in self.search.node_placements.iteritems():
            if isinstance(v, Server):
                rh = self.search.avail_hosts[p.host_name]

                for gk, g in rh.host_memberships.iteritems():
                    if g.factory in ("valet", "server-group"):
                        if g.level == "host":
                            _app.resource.add_group(gk,
                                                    g.group_type,
                                                    g.level,
                                                    g.factory,
                                                    rh.host_name)

                if rh.rack_name != "any":
                    for gk, g in rh.rack_memberships.iteritems():
                        if g.factory in ("valet", "server-group"):
                            if g.level == "rack":
                                _app.resource.add_group(gk,
                                                        g.group_type,
                                                        g.level,
                                                        g.factory,
                                                        rh.rack_name)

                s_info = placements[v.vid].get("info")

                self._collect_groups_of_server(v, s_info, groups)

        # Update groups with new servers
        _app.resource.update_server_grouping(change_of_placements=placements,
                                             new_groups=groups)

        _app.resource.update_resource()

    def _convert_host(self, _rhost, _ha_name, _host_type, _resource):
        """Convert host's type into the specific type as given."""

        host = _resource.hosts[_rhost.host_name]

        if host.candidate_host_types is None or len(host.candidate_host_types) == 0:
            return

        host.vCPUs = _host_type["vCPUs"]
        host.original_vCPUs = _host_type["original_vCPUs"]
        host.avail_vCPUs = _host_type["avail_vCPUs"]
        host.mem_cap = _host_type["mem"]
        host.original_mem_cap = _host_type["original_mem"]
        host.avail_mem_cap = _host_type["avail_mem"]
        host.local_disk_cap = _host_type["local_disk"]
        host.original_local_disk_cap = _host_type["original_local_disk"]
        host.avail_local_disk_cap = _host_type["avail_local_disk"]
        host.vCPUs_used = _host_type["vCPUs_used"]
        host.free_mem_mb = _host_type["free_mem_mb"]
        host.free_disk_gb = _host_type["free_disk_gb"]
        host.disk_available_least = _host_type["disk_available_least"]

        host.NUMA = _rhost.NUMA

        ha = _resource.groups[_ha_name]
        host.memberships[ha.name] = ha
        ha.member_hosts[host.name] = []
        ha.updated = True

        _resource.mark_host_updated(host.name)

        _resource.update_resource()

        if host.candidate_host_types is not None:
            host.candidate_host_types.clear()

    def _rollback_placements(self, _app):
        """Remove placements when they fail.

           Remove placements from NUMA cells of resource object.
        """

        for v, p in self.search.node_placements.iteritems():
            if isinstance(v, Server):
                s_info = {}

                if _app.app_id is None or _app.app_id == "none":
                    s_info["stack_id"] = "none"
                else:
                    s_info["stack_id"] = _app.app_id
                s_info["stack_name"] = _app.app_name

                s_info["uuid"] = "none"
                s_info["orch_id"] = v.orch_id
                s_info["name"] = v.name

                s_info["flavor_id"] = v.flavor
                s_info["vcpus"] = v.vCPUs
                s_info["mem"] = v.mem
                s_info["disk"] = v.local_volume_size
                s_info["numa"] = v.numa

                s_info["image_id"] = v.image
                s_info["tenant_id"] = _app.tenant_id

                s_info["state"] = v.state
                s_info["status"] = "valid"

                host = _app.resource.hosts[p.host_name]
                host.NUMA.rollback_server_resources(s_info)

    def _collect_groups_of_server(self, _v, _s_info, _groups):
        """Collect all groups of the server and its parent (affinity)."""

        # TODO(Gueyoung): track host-aggregates and availability-zone?

        for gk in _v.exclusivity_groups.keys():
            if gk not in _groups.keys():
                _groups[gk] = []
            _groups[gk].append(_s_info)

        for gk in _v.diversity_groups.keys():
            if gk not in _groups.keys():
                _groups[gk] = []
            _groups[gk].append(_s_info)

        for gk in _v.quorum_diversity_groups.keys():
            if gk not in _groups.keys():
                _groups[gk] = []
            _groups[gk].append(_s_info)

        if isinstance(_v, Group):
            if _v.vid not in _groups.keys():
                _groups[_v.vid] = []
            _groups[_v.vid].append(_s_info)

        # Recursively check server or its affinity group.
        if _v.surgroup is not None:
            self._collect_groups_of_server(_v.surgroup, _s_info, _groups)

    def _remove_resource(self, _app):
        """Remove servers from resources.

        Resources: NUMA, host, host_group, datacenter,
        valet groups and server-groups.
        """

        placements = {}

        for sk, s in _app.servers.iteritems():
            if s["host"] == "none":
                continue

            s_info = {}

            if _app.app_id is None or _app.app_id == "none":
                s_info["stack_id"] = "none"
            else:
                s_info["stack_id"] = _app.app_id
            s_info["stack_name"] = _app.app_name

            s_info["uuid"] = "none"
            s_info["name"] = s.get("name")

            s_info["flavor_id"] = s.get("flavor")
            s_info["vcpus"] = s.get("cpus")
            s_info["mem"] = s.get("mem")
            s_info["disk"] = s.get("local_volume")
            s_info["numa"] = s.get("numa")

            s_info["image_id"] = s.get("image")
            s_info["tenant_id"] = _app.tenant_id

            s_info["state"] = "deleted"

            if s_info["stack_id"] != "none":
                sid = s_info["stack_id"] + ":" + s_info["name"]
            else:
                sid = s_info["stack_name"] + ":" + s_info["name"]

            placements[sid] = {}
            placements[sid]["old_host"] = s.get("host")
            placements[sid]["info"] = s_info

        if not _app.resource.update_server_placements(change_of_placements=placements):
            _app.status = "fail while updating server placements"
            return

        _app.resource.update_server_grouping(change_of_placements=placements,
                                             new_groups={})

        _app.resource.update_resource()

    def _update_resource(self, _app):
        """Update state of servers in resources.

        Resources: NUMA, host, host_group, datacenter,
        valet groups and server-groups.
        """

        placements = {}

        for sk, s in _app.servers.iteritems():
            if s["host"] == "none":
                continue

            s_info = {}

            if _app.app_id is None or _app.app_id == "none":
                s_info["stack_id"] = "none"
            else:
                s_info["stack_id"] = _app.app_id
            s_info["stack_name"] = _app.app_name

            s_info["uuid"] = "none"
            s_info["name"] = s.get("name")

            s_info["flavor_id"] = "none"
            s_info["vcpus"] = -1
            s_info["mem"] = -1
            s_info["disk"] = -1
            s_info["numa"] = "none"

            s_info["image_id"] = "none"

            s_info["state"] = s.get("state")
            s_info["status"] = "none"

            if s_info["stack_id"] != "none":
                sid = s_info["stack_id"] + ":" + s_info["name"]
            else:
                sid = s_info["stack_name"] + ":" + s_info["name"]

            placements[sid] = {}
            placements[sid]["host"] = s.get("host")
            placements[sid]["info"] = s_info

        if not _app.resource.update_server_placements(change_of_placements=placements):
            _app.status = "fail while updating server placements"
            return

        _app.resource.update_server_grouping(change_of_placements=placements,
                                             new_groups={})

        _app.resource.update_resource()
