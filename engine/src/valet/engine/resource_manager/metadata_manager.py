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
#!/usr/bin/env python3


import json

from copy import deepcopy


class MetadataManager(object):
    """Metadata Manager to maintain flavors and groups."""

    def __init__(self, _source, _logger):
        self.source = _source

        self.groups = {}

        self.flavors = {}

        self.logger = _logger

    def get_groups(self, _resource):
        """Set groups (availability-zones, host-aggregates, server groups)

        from platform (e.g., nova).
        """

        self.logger.info("set metadata (groups)...")

        # Init first
        self.groups.clear()

        # Get enabled groups only
        if self.source.get_groups(self.groups) != "ok":
            self.logger.warning("fail to set groups from source (e.g., nova)")
            return False

        self._check_group_updated(_resource)

        self._check_host_memberships_updated(_resource)

        return True

    def _check_group_updated(self, _resource):
        """Check any inconsistency for groups."""

        for gk in self.groups.keys():
            if gk not in _resource.groups.keys():
                _resource.groups[gk] = deepcopy(self.groups[gk])
                _resource.groups[gk].updated = True

                self.logger.info("new group (" + gk + ") added")

        for rgk in _resource.groups.keys():
            rg = _resource.groups[rgk]

            if rg.factory != "valet":
                if rgk not in self.groups.keys():
                    rg.status = "disabled"
                    rg.updated = True

                    self.logger.info("group (" + rgk + ") disabled")

        for gk in self.groups.keys():
            g = self.groups[gk]
            rg = _resource.groups[gk]

            if rg.uuid is None and g.uuid is not None:
                rg.uuid = g.uuid
                rg.updated = True

                self.logger.info("group (" + gk + ") uuid updated")

            # TODO: Clean up resource.hosts if each is not in any AZ members.

            if g.group_type == "aggr":
                if not gk.startswith("valet:"):
                    if self._is_group_metadata_updated(g, rg):
                        rg.updated = True

                        self.logger.info("group (" + gk + ") metadata updated")

            if g.group_type == "az" or g.group_type == "aggr":
                if self._is_member_hosts_updated(g, _resource):
                    rg.updated = True

                    self.logger.info("group (" + gk + ") member hosts updated")

            if g.factory == "server-group":
                if self._is_new_servers(g, rg):
                    rg.updated = True

                    self.logger.info("group (" + gk + ") server_list updated")

    def _is_group_metadata_updated(self, _g, _rg):
        """Check any change in metadata of group."""

        updated = False

        for mdk in _g.metadata.keys():
            if mdk not in _rg.metadata.keys():
                _rg.metadata[mdk] = _g.metadata[mdk]
                updated = True

        for rmdk in _rg.metadata.keys():
            if rmdk not in _g.metadata.keys():
                del _rg.metadata[rmdk]
                updated = True

        for mdk in _g.metadata.keys():
            mdv = _g.metadata[mdk]
            rmdv = _rg.metadata[mdk]
            if mdv != rmdv:
                _rg.metadata[mdk] = mdv
                updated = True

        return updated

    def _is_member_hosts_updated(self, _g, _resource):
        """Check any change in member hosts of group."""

        updated = False

        _rg = _resource.groups[_g.name]

        for hk in _g.member_hosts.keys():
            if hk not in _rg.member_hosts.keys():
                if hk in _resource.hosts.keys():
                    if _resource.hosts[hk].is_available():
                        _rg.member_hosts[hk] = deepcopy(_g.member_hosts[hk])
                        updated = True
            # else not needed

        for rhk in _rg.member_hosts.keys():
            if rhk not in _resource.hosts.keys() or \
               not _resource.hosts[rhk].is_available() or \
               rhk not in _g.member_hosts.keys():
                del _rg.member_hosts[rhk]
                updated = True

        return updated

    def _is_new_servers(self, _g, _rg):
        """Check if there is any new server."""

        updated = False

        for s_info in _g.server_list:
            exist = False
            for rs_info in _rg.server_list:
                if rs_info.get("uuid") == s_info.get("uuid"):
                    exist = True
                    break

            if not exist:
                _rg.server_list.append(s_info)
                updated = True

        return updated

    def _check_host_memberships_updated(self, _resource):
        """Check host memberships consistency."""

        for gk, g in _resource.groups.items():
            # Other group types will be handled later
            if g.factory != "valet" and g.status == "enabled":
                for hk in g.member_hosts.keys():
                    host = _resource.hosts[hk]
                    if gk not in host.memberships.keys() or g.updated:
                        host.memberships[gk] = g
                        _resource.mark_host_updated(hk)

                        self.logger.info("host (" + hk + ") updated (update membership - " + gk + ")")

        for hk, host in _resource.hosts.items():
            if host.is_available():
                for gk in host.memberships.keys():
                    if gk in _resource.groups.keys():
                        g = _resource.groups[gk]
                        if g.factory != "valet":
                            if g.status == "enabled":
                                if g.updated:
                                    host.memberships[gk] = g
                                    _resource.mark_host_updated(hk)

                                    self.logger.info("host (" + hk + ") updated (update membership - " + gk + ")")
                            else:
                                del host.memberships[gk]
                                _resource.mark_host_updated(hk)

                                self.logger.info("host (" + hk + ") updated (remove membership - " + gk + ")")
                    else:
                        del host.memberships[gk]
                        _resource.mark_host_updated(hk)

                        self.logger.info("host (" + hk + ") updated (remove membership - " + gk + ")")

    def create_exclusive_aggregate(self, _group, _hosts):
        """Set Host-Aggregate to apply Exclusivity."""

        az = _hosts[0].get_availability_zone()

        # To remove 'az:' header from name
        az_name_elements = az.name.split(':', 1)
        if len(az_name_elements) > 1:
            az_name = az_name_elements[1]
        else:
            az_name = az.name

        status = self.source.set_aggregate(_group.name, az_name)
        if status != "ok":
            return status

        self.logger.debug("dynamic host-aggregate(" + _group.name + ") created")

        aggregates = {}
        status = self.source.get_aggregates(aggregates)
        if status != "ok":
            return status

        if _group.name in aggregates.keys():
            _group.uuid = aggregates[_group.name].uuid

            if len(_group.metadata) > 0:
                metadata = {}
                for mk, mv in _group.metadata.items():
                    if mk == "prior_metadata":
                        metadata[mk] = json.dumps(mv)
                    else:
                        metadata[mk] = mv

                status = self.source.set_metadata_of_aggregate(_group.uuid, metadata)
                if status != "ok":
                    return status

                self.logger.debug("dynamic host-aggregate(" + _group.name + ") metadata created")

            for host in _hosts:
                if host.name in _group.metadata.keys():
                    aggr_uuids = _group.metadata[host.name].split(',')

                    for uuid in aggr_uuids:
                        status = self.source.remove_host_from_aggregate(int(uuid), host.name)
                        if status != "ok":
                            return status

                        self.logger.debug("host-aggregate(" + uuid + ") host(" + host.name + ") removed")

                status = self.source.add_host_to_aggregate(_group.uuid, host.name)
                if status != "ok":
                    return status

                self.logger.debug("dynamic host-aggregate(" + _group.name + ") host(" + host.name + ") added")
        else:
            status = "dynamic host-aggregate not found"
            self.logger.error(status)
            return status

        return "ok"

    def update_exclusive_aggregate(self, _id, _metadata, _host, _old_aggregates):
        """Update Host-Aggregate to apply Exclusivity."""

        if len(_metadata) > 0:
            metadata = {}
            for mk, mv in _metadata.items():
                if mk == "prior_metadata":
                    metadata[mk] = json.dumps(mv)
                else:
                    metadata[mk] = mv

            status = self.source.set_metadata_of_aggregate(_id, metadata)
            if status != "ok":
                return status

            self.logger.debug("dynamic host-aggregate(" + str(_id) + ") metadata updated")

        for oa in _old_aggregates:
            status = self.source.remove_host_from_aggregate(oa.uuid, _host)
            if status != "ok":
                return status

            self.logger.debug("host-aggregate(" + oa.name + ") host(" + _host + ") removed")

        status = self.source.add_host_to_aggregate(_id, _host)
        if status != "ok":
            return status

        self.logger.debug("dynamic host-aggregate(" + str(_id) + ") host(" + _host + ") added")

        return "ok"

    def remove_host_from_exclusive_aggregate(self, _id, _metadata, _host, _old_aggregates):
        """Remove host from Host-Aggregate to apply Exclusivity."""

        if len(_metadata) > 0:
            metadata = {}
            for mk, mv in _metadata.items():
                if mk == "prior_metadata":
                    metadata[mk] = json.dumps(mv)
                else:
                    metadata[mk] = mv

            status = self.source.set_metadata_of_aggregate(_id, metadata)
            if status != "ok":
                return status

            self.logger.debug("dynamic host-aggregate(" + str(_id) + ") metadata updated")

        status = self.source.remove_host_from_aggregate(_id, _host)
        if status != "ok":
            return status

        self.logger.debug("dynamic host-aggregate(" + str(_id) + ") host(" + _host + ") removed")

        for oa in _old_aggregates:
            status = self.source.add_host_to_aggregate(oa.uuid, _host)
            if status != "ok":
                return status

            self.logger.debug("host-aggregate(" + oa.name + ") host(" + _host + ") added")

        return "ok"

    def remove_exclusive_aggregate(self, _id):
        """Remove Host-Aggregate."""

        status = self.source.delete_aggregate(_id)
        if status != "ok":
            return status

        self.logger.debug("dynamic host-aggregate(" + str(_id) + ") removed")

        return "ok"

    def get_flavors(self, _resource):
        """Set flavors from nova."""

        self.logger.info("set metadata (flavors)...")

        # Init first
        self.flavors.clear()

        # Get enabled flavors only
        if self.source.get_flavors(self.flavors, detailed=False) != "ok":
            return False

        self._check_flavor_update(_resource, False)

        return True

    def _check_flavor_update(self, _resource, _detailed):
        """Check flavor info consistency."""

        for fk in self.flavors.keys():
            if fk not in _resource.flavors.keys():
                _resource.flavors[fk] = deepcopy(self.flavors[fk])
                _resource.flavors[fk].updated = True

                self.logger.info("new flavor (" + fk + ":" + self.flavors[fk].flavor_id + ") added")

        for rfk in _resource.flavors.keys():
            rf = _resource.flavors[rfk]
            if rfk not in self.flavors.keys():
                rf.status = "disabled"
                rf.updated = True

                self.logger.info("flavor (" + rfk + ":" + rf.flavor_id + ") removed")

        if _detailed:
            for fk in self.flavors.keys():
                f = self.flavors[fk]
                rf = _resource.flavors[fk]
                if self._is_flavor_spec_updated(f, rf):
                    rf.updated = True

                    self.logger.info("flavor (" + fk + ":" + rf.flavor_id + ") spec updated")

    def _is_flavor_spec_updated(self, _f, _rf):
        """Check flavor's spec consistency."""

        spec_updated = False

        if _f.vCPUs != _rf.vCPUs or _f.mem_cap != _rf.mem_cap or _f.disk_cap != _rf.disk_cap:
            _rf.vCPUs = _f.vCPUs
            _rf.mem_cap = _f.mem_cap
            _rf.disk_cap = _f.disk_cap
            spec_updated = True

        for sk in _f.extra_specs.keys():
            if sk not in _rf.extra_specs.keys():
                _rf.extra_specs[sk] = _f.extra_specs[sk]
                spec_updated = True

        for rsk in _rf.extra_specs.keys():
            if rsk not in _f.extra_specs.keys():
                del _rf.extra_specs[rsk]
                spec_updated = True

        for sk in _f.extra_specs.keys():
            sv = _f.extra_specs[sk]
            rsv = _rf.extra_specs[sk]
            if sv != rsv:
                _rf.extra_specs[sk] = sv
                spec_updated = True

        return spec_updated
