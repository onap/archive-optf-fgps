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
import json
import time
import traceback

from novaclient import client as nova_client

from valet.engine.resource_manager.resources.flavor import Flavor
from valet.engine.resource_manager.resources.group import Group
from valet.engine.resource_manager.resources.host import Host
from valet.utils.decryption import decrypt


# Nova API version
VERSION = 2


# noinspection PyBroadException
class NovaCompute(object):
    """Source to collect resource status (i.e., OpenStack Nova).

    Manupulate Host-Aggregate with Valet placement decisions.
    """

    def __init__(self, _config, _logger):
        self.logger = _logger

        self.nova = None

        self.novas = {}
        self.last_activate_urls = {}
        self.life_time = 43200    # 12 hours

        # TODO(Gueyoung): handle both admin and admin_view accounts.

        pw = decrypt(_config["engine"]["ek"],
                     _config["logging"]["lk"],
                     _config["db"]["dk"],
                     _config["nova"]["admin_view_password"])

        self.admin_username = _config["nova"]["admin_view_username"]
        self.admin_password = pw
        self.project = _config["nova"]["project_name"]

    def set_client(self, _auth_url):
        """Set nova client."""

        try:
            # TODO: add timeout=_timeout?
            self.novas[_auth_url] = nova_client.Client(VERSION,
                                                       self.admin_username,
                                                       self.admin_password,
                                                       self.project,
                                                       _auth_url)

            self.last_activate_urls[_auth_url] = time.time()

            self.nova = self.novas[_auth_url]
            return True
        except Exception:
            self.logger.error(traceback.format_exc())
            return False

    def valid_client(self, _auth_url):
        """Check if nova connection is valid."""

        if _auth_url not in self.novas.keys():
            return False

        if _auth_url not in self.last_activate_urls.keys():
            return False

        elapsed_time = time.time() - self.last_activate_urls[_auth_url]

        if elapsed_time > self.life_time:
            return False

        self.nova = self.novas[_auth_url]

        return True

    def get_groups(self, _groups):
        """Get server-groups, availability-zones and host-aggregates

        from OpenStack Nova.
        """

        status = self._get_availability_zones(_groups)
        if status != "ok":
            self.logger.error(status)
            return status

        status = self.get_aggregates(_groups)
        if status != "ok":
            self.logger.error(status)
            return status

        status = self._get_server_groups(_groups)
        if status != "ok":
            self.logger.error(status)
            return status

        return "ok"

    def _get_availability_zones(self, _groups):
        """Set AZs."""

        try:
            # TODO: try hosts_list = self.nova.hosts.list()?

            az_list = self.nova.availability_zones.list(detailed=True)

            for a in az_list:
                if a.zoneState["available"]:
                    # NOTE(Gueyoung): add 'az:' to avoid conflict with
                    # Host-Aggregate name.
                    az_id = "az:" + a.zoneName

                    az = Group(az_id)

                    az.group_type = "az"
                    az.factory = "nova"
                    az.level = "host"

                    # TODO: Get AZ first with init Compute Hosts?

                    for hk, h_info in a.hosts.items():
                        if "nova-compute" in h_info.keys():
                            if h_info["nova-compute"]["active"] and \
                               h_info["nova-compute"]["available"]:
                                az.member_hosts[hk] = []

                    _groups[az_id] = az

        except Exception:
            self.logger.error(traceback.format_exc())
            return "error while setting availability-zones from Nova"

        return "ok"

    def get_aggregates(self, _groups):
        """Set host-aggregates and corresponding hosts."""

        try:
            aggregate_list = self.nova.aggregates.list()

            for a in aggregate_list:
                if not a.deleted:
                    aggregate = Group(a.name)

                    aggregate.uuid = a.id

                    aggregate.group_type = "aggr"
                    aggregate.factory = "nova"
                    aggregate.level = "host"

                    metadata = {}
                    for mk in a.metadata.keys():
                        if mk == "prior_metadata":
                            metadata[mk] = json.loads(a.metadata.get(mk))
                        else:
                            metadata[mk] = a.metadata.get(mk)
                    aggregate.metadata = metadata

                    for hn in a.hosts:
                        aggregate.member_hosts[hn] = []
            
                    _groups[aggregate.name] = aggregate

        except Exception:
            self.logger.error(traceback.format_exc())
            return "error while setting host-aggregates from Nova"

        return "ok"

    def set_aggregate(self, _name, _az):
        """Create a Host-Aggregate."""

        try:
            self.nova.aggregates.create(_name, _az)
        except Exception:
            self.logger.error(traceback.format_exc())
            return "error while setting a host-aggregate in Nova"

        return "ok"

    def add_host_to_aggregate(self, _aggr, _host):
        """Add a Host into the Host-Aggregate."""

        try:
            self.nova.aggregates.add_host(_aggr, _host)
        except Exception:
            self.logger.error(traceback.format_exc())
            return "error while adding a host into host-aggregate in Nova"

        return "ok"

    def delete_aggregate(self, _aggr):
        """Delete the Host-Aggregate."""

        try:
            self.nova.aggregates.delete(_aggr)
        except Exception:
            self.logger.error(traceback.format_exc())
            return "error while deleting host-aggregate from Nova"

        return "ok"

    def remove_host_from_aggregate(self, _aggr, _host):
        """Remove the Host from the Host-Aggregate."""

        try:
            self.nova.aggregates.remove_host(_aggr, _host)
        except Exception:
            self.logger.error(traceback.format_exc())
            return "error while removing host from host-aggregate in Nova"

        return "ok"

    def set_metadata_of_aggregate(self, _aggr, _metadata):
        """Set metadata.

           Note that Nova adds key/value pairs into metadata instead of replacement.
        """

        try:
            self.nova.aggregates.set_metadata(_aggr, _metadata)
        except Exception:
            self.logger.error(traceback.format_exc())
            return "error while setting metadata of host-aggregate in Nova"

        return "ok"

    def _get_server_groups(self, _groups):
        """Set host-aggregates and corresponding hosts."""

        try:
            # NOTE(Gueyoung): novaclient v2.18.0 does not have 'all_projects=True' param.
            server_group_list = self.nova.server_groups.list()

            for g in server_group_list:
                server_group = Group(g.name)

                server_group.uuid = g.id

                # TODO: Check len(g.policies) == 1
                # policy is either 'affinity', 'anti-affinity', 'soft-affinity',
                # or 'soft-anti-affinity'
                if g.policies[0] == "anti-affinity":
                    server_group.group_type = "diversity"
                else:
                    server_group.group_type = g.policies[0]
                server_group.factory = "server-group"
                server_group.level = "host"

                # Members attribute is a list of server uuids
                for s_uuid in g.members:
                    s_info = {}
                    s_info["stack_id"] = "none"
                    s_info["stack_name"] = "none"
                    s_info["uuid"] = s_uuid
                    s_info["orch_id"] = "none"
                    s_info["name"] = "none"
                    s_info["flavor_id"] = "none"
                    s_info["vcpus"] = -1
                    s_info["mem"] = -1
                    s_info["disk"] = -1
                    s_info["numa"] = "none"
                    s_info["image_id"] = "none"
                    s_info["tenant_id"] = "none"
                    s_info["state"] = "created"
                    s_info["status"] = "valid"

                    server_group.server_list.append(s_info)

                # TODO: Check duplicated name as group identifier
                _groups[server_group.name] = server_group

        except Exception:
            self.logger.error(traceback.format_exc())
            return "error while setting server-groups from Nova"

        return "ok"

    def get_hosts(self, _hosts):
        """Set host resources info."""

        # TODO: Deprecated as of version 2.43
        status = self._get_hosts(_hosts)
        if status != "ok":
            self.logger.error(status)
            return status

        status = self._get_host_details(_hosts)
        if status != "ok":
            self.logger.error(status)
            return status

        return "ok"

    # TODO: Deprecated as of version 2.43
    def _get_hosts(self, _hosts):
        """Init hosts."""

        try:
            host_list = self.nova.hosts.list()

            for h in host_list:
                if h.service == "compute":
                    host = Host(h.host_name)
                    _hosts[host.name] = host
        except Exception:
            self.logger.error(traceback.format_exc())
            return "error while setting hosts from Nova"

        return "ok"

    def _get_host_details(self, _hosts):
        """Get each host's resource status."""

        try:
            # TODO: marker: the last UUID of return, limit: the number of hosts returned.
            # with_servers=True
            host_list = self.nova.hypervisors.list(detailed=True)

            for hv in host_list:
                if hv.service['host'] in _hosts.keys():
                    if hv.status != "enabled" or hv.state != "up":
                        del _hosts[hv.service['host']]
                    else:
                        host = _hosts[hv.service['host']]

                        host.uuid = hv.id

                        host.status = hv.status
                        host.state = hv.state
                        host.original_vCPUs = float(hv.vcpus)
                        host.vCPUs_used = float(hv.vcpus_used)
                        host.original_mem_cap = float(hv.memory_mb)
                        host.free_mem_mb = float(hv.free_ram_mb)
                        host.original_local_disk_cap = float(hv.local_gb)
                        host.free_disk_gb = float(hv.free_disk_gb)
                        host.disk_available_least = float(hv.disk_available_least)

                        # TODO: cpu_info:topology:sockets

        except Exception:
            self.logger.error(traceback.format_exc())
            return "error while setting host resources from Nova"

        return "ok"

    def get_servers_in_hosts(self, _hosts):
        """Set servers in hosts."""

        (status, server_list) = self.get_server_detail()
        if status != "ok":
            self.logger.error(status)
            return status

        for s in server_list:
            s_info = {}

            if "stack-id" in s.metadata.keys():
                s_info["stack_id"] = s.metadata["stack-id"]
            else:
                s_info["stack_id"] = "none"
            s_info["stack_name"] = "none"

            s_info["uuid"] = s.id

            s_info["orch_id"] = "none"
            s_info["name"] = s.name

            s_info["flavor_id"] = s.flavor["id"]

            if "vcpus" in s.flavor.keys():
                s_info["vcpus"] = s.flavor["vcpus"]
                s_info["mem"] = s.flavor["ram"]
                s_info["disk"] = s.flavor["disk"]
                s_info["disk"] += s.flavor["ephemeral"]
                s_info["disk"] += s.flavor["swap"] / float(1024)
            else:
                s_info["vcpus"] = -1
                s_info["mem"] = -1
                s_info["disk"] = -1

            s_info["numa"] = "none"

            try:
                s_info["image_id"] = s.image["id"]
            except TypeError:
                self.logger.warning("In get_servers_in_hosts, expected s.image to have id tag, but it's actually " + s.image)
                s_info["image_id"] = s.image

            s_info["tenant_id"] = s.tenant_id

            s_info["state"] = "created"
            s_info["status"] = "valid"

            s_info["host"] = s.__getattr__("OS-EXT-SRV-ATTR:host")

            # s_info["power_state"] = s.__getattr__("OS-EXT-STS:power_state")
            # s_info["vm_state"] = s.__getattr__("OS-EXT-STS:vm_state")
            # s_info["task_state"] = s.__getattr__("OS-EXT-STS:task_state")

            if s_info["host"] in _hosts.keys():
                host = _hosts[s_info["host"]]
                host.server_list.append(s_info)

        return "ok"

    def get_server_detail(self, project_id=None, host_name=None, server_name=None, uuid=None):
        """Get the detail of server with search by option."""

        # TODO: Get servers' info  in each host
        # Minimum requirement for server info: s["metadata"]["stack-id"],
        # More: s["flavor"]["id"], s["tenant_id"]
        # Maybe: s["image"], server.__getattr__("OS-EXT-AZ:availability_zone"), s["status"]
        #        and scheduler_hints?
        try:
            options = {"all_tenants": 1}
            if project_id is not None:
                options["project_id"] = project_id
            if host_name is not None:
                options["host"] = host_name
            if server_name is not None:
                options["name"] = server_name
            if uuid is not None:
                options["uuid"] = uuid

            # TODO: search by vm_state?

            if len(options) > 0:
                server_list = self.nova.servers.list(detailed=True, search_opts=options)
            else:
                server_list = self.nova.servers.list(detailed=True)

        except Exception:
            self.logger.error(traceback.format_exc())
            return "error while getting server detail from nova", None

        return "ok", server_list

    def get_flavors(self, _flavors, detailed=True):
        """Get flavors."""

        if detailed:
            result_status = self._get_flavors(_flavors, True)
        else:
            result_status = self._get_flavors(_flavors, False)

        if result_status != "ok":
            self.logger.error(result_status)

        return result_status

    def _get_flavors(self, _flavors, _detailed):
        """Get a list of all flavors."""

        try:
            flavor_list = self.nova.flavors.list(detailed=_detailed)

            for f in flavor_list:
                flavor = self._set_flavor(f, _detailed)
                _flavors[flavor.name] = flavor
        except Exception:
            self.logger.error(traceback.format_exc())
            return "error while getting flavors"

        # To get non-public flavors.
        try:
            flavor_list = self.nova.flavors.list(detailed=_detailed, is_public=False)

            for f in flavor_list:
                if f.name not in _flavors.keys():
                    flavor = self._set_flavor(f, _detailed)
                    _flavors[flavor.name] = flavor
        except Exception:
            self.logger.error(traceback.format_exc())
            return "error while getting flavors"

        return "ok"

    def get_flavor(self, _flavor_id):
        """Get the flavor."""

        try:
            f = self.nova.flavors.get(_flavor_id)
            flavor = self._set_flavor(f, True)
        except Exception:
            self.logger.error(traceback.format_exc())
            return None

        return flavor

    def _set_flavor(self, _f, _detailed):
        """Set flavor with detailed infomation."""

        flavor = Flavor(_f.name)

        flavor.flavor_id = _f.id

        if _detailed:
            # NOTE(Gueyoung): This is not allowed with current credential.
            # if getattr(_f, "OS-FLV-DISABLED:disabled"):
            #     flavor.status = "disabled"

            flavor.vCPUs = float(_f.vcpus)
            flavor.mem_cap = float(_f.ram)

            root_gb = float(_f.disk)
            ephemeral_gb = 0.0
            if hasattr(_f, "OS-FLV-EXT-DATA:ephemeral"):
                ephemeral_gb = float(getattr(_f, "OS-FLV-EXT-DATA:ephemeral"))
            swap_mb = 0.0
            if hasattr(_f, "swap"):
                sw = getattr(_f, "swap")
                if sw != '':
                    swap_mb = float(sw)
            flavor.disk_cap = root_gb + ephemeral_gb + swap_mb / float(1024)

            extra_specs = _f.get_keys()
            for sk, sv in extra_specs.items():
                flavor.extra_specs[sk] = sv

        return flavor
