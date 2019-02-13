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

from valet.engine.app_manager.group import Group, LEVEL
from valet.engine.app_manager.server import Server


class Parser(object):

    def __init__(self, _logger):
        self.logger = _logger

        self.status = "ok"

    def set_servers(self, _app_name, _stack, _groups):
        """Parse stack resources to set servers (e.g., VMs) for search."""

        servers = {}

        for rk, r in _stack.iteritems():
            properties = r.get("properties")

            server_name = properties["name"].strip()
            server_id = _app_name + ":" + server_name

            server = Server(server_id, rk)

            server.name = server_name

            flavor_id = properties.get("flavor")
            if isinstance(flavor_id, six.string_types):
                server.flavor = flavor_id.strip()
            else:
                server.flavor = str(flavor_id)

            image_id = properties.get("image", None)
            if image_id is not None:
                if isinstance(image_id, six.string_types):
                    server.image = image_id.strip()
                else:
                    server.image = str(image_id)

            if "vcpus" in properties.keys():
                server.vCPUs = int(properties.get("vcpus"))
                server.mem = int(properties.get("mem"))
                server.local_volume_size = int(properties.get("local_volume"))

                ess = properties.get("extra_specs", {})
                if len(ess) > 0:
                    extra_specs = {}
                    for mk, mv in ess.iteritems():
                        extra_specs[mk] = mv
                    server.extra_specs_list.append(extra_specs)

            az = properties.get("availability_zone", None)
            if az is not None:
                server.availability_zone = az[0].strip()
                server.host_assignment_variable = az[1].strip()
                if len(az) == 3:
                    server.host_assignment_inx = az[2]

            servers[server_id] = server

        if self._merge_diversity_groups(_groups, servers) is False:
            self.status = "fail while merging diversity groups"
            return {}, {}
        if self._merge_quorum_diversity_groups(_groups, servers) is False:
            self.status = "fail while merging quorum-diversity groups"
            return {}, {}
        if self._merge_exclusivity_groups(_groups, servers) is False:
            self.status = "fail while merging exclusivity groups"
            return {}, {}
        if self._merge_affinity_groups(_groups, servers) is False:
            self.status = "fail while merging affinity groups"
            return {}, {}

        # To delete all exclusivity and diversity groups after merging
        groups = {gk: g for gk, g in _groups.iteritems() if g.group_type == "affinity"}

        return servers, groups

    def _merge_diversity_groups(self, _groups, _servers):
        """Merge diversity sub groups."""

        for level in LEVEL:
            for gk, group in _groups.iteritems():
                if group.level == level and group.group_type == "diversity":
                    for sk in group.server_list:
                        if sk in _servers.keys():
                            group.subgroups[sk] = _servers[sk]
                            _servers[sk].diversity_groups[group.vid] = group
                        else:
                            self.status = "invalid server = " + sk + " in group = " + group.vid
                            return False

        return True

    def _merge_quorum_diversity_groups(self, _groups, _servers):
        """Merge quorum-diversity sub groups."""

        for level in LEVEL:
            for gk, group in _groups.iteritems():
                if group.level == level and group.group_type == "quorum-diversity":
                    for sk in group.server_list:
                        if sk in _servers.keys():
                            group.subgroups[sk] = _servers[sk]
                            _servers[sk].quorum_diversity_groups[group.vid] = group
                        else:
                            self.status = "invalid server = " + sk + " in group = " + group.vid
                            return False

        return True

    def _merge_exclusivity_groups(self, _groups, _servers):
        """Merge exclusivity sub groups."""

        for level in LEVEL:
            for gk, group in _groups.iteritems():
                if group.level == level and group.group_type == "exclusivity":
                    for sk in group.server_list:
                        if sk in _servers.keys():
                            group.subgroups[sk] = _servers[sk]
                            _servers[sk].exclusivity_groups[group.vid] = group
                        else:
                            self.status = "invalid server = " + sk + " in group = " + group.vid
                            return False

        return True

    def _merge_affinity_groups(self, _groups, _servers):
        """Merge affinity subgroups."""

        # To track each server's or group's parent group (i.e., affinity)
        affinity_map = {}

        # To make cannonical order of groups
        group_list = [gk for gk in _groups.keys()]
        group_list.sort()

        for level in LEVEL:
            for gk in group_list:
                if gk in _groups.keys():
                    if _groups[gk].level == level and _groups[gk].group_type == "affinity":
                        group = _groups[gk]
                    else:
                        continue
                else:
                    continue

                group.server_list.sort()

                for sk in group.server_list:
                    if sk in _servers.keys():
                        self._merge_server(group, sk, _servers, affinity_map)
                    else:
                        if sk not in affinity_map.keys():
                            self.status = "invalid server = " + sk + " in group = " + group.vid
                            return False

                        # If server belongs to the other group already,
                        # take the group as a subgroup of this group
                        if affinity_map[sk].vid != group.vid:
                            if group.is_parent_affinity(sk):
                                self._set_implicit_grouping(sk, group, affinity_map, _groups)

        return True

    def _merge_server(self, _group, _sk, _servers, _affinity_map):
        """Merge a server into the group."""

        _group.subgroups[_sk] = _servers[_sk]
        _servers[_sk].surgroup = _group
        _affinity_map[_sk] = _group

        self._add_implicit_diversity_groups(_group, _servers[_sk].diversity_groups)
        self._add_implicit_quorum_diversity_groups(_group, _servers[_sk].quorum_diversity_groups)
        self._add_implicit_exclusivity_groups(_group, _servers[_sk].exclusivity_groups)
        self._add_memberships(_group, _servers[_sk])

        del _servers[_sk]

    def _add_implicit_diversity_groups(self, _group, _diversity_groups):
        """Add subgroup's diversity groups."""

        for dk, div_group in _diversity_groups.iteritems():
            if LEVEL.index(div_group.level) >= LEVEL.index(_group.level):
                _group.diversity_groups[dk] = div_group

    def _add_implicit_quorum_diversity_groups(self, _group, _quorum_diversity_groups):
        """Add subgroup's quorum diversity groups."""

        for dk, div_group in _quorum_diversity_groups.iteritems():
            if LEVEL.index(div_group.level) >= LEVEL.index(_group.level):
                _group.quorum_diversity_groups[dk] = div_group

    def _add_implicit_exclusivity_groups(self, _group, _exclusivity_groups):
        """Add subgroup's exclusivity groups."""

        for ek, ex_group in _exclusivity_groups.iteritems():
            if LEVEL.index(ex_group.level) >= LEVEL.index(_group.level):
                _group.exclusivity_groups[ek] = ex_group

    def _add_memberships(self, _group, _v):
        """Add subgroups's host-aggregates and AZs."""

        for extra_specs in _v.extra_specs_list:
            _group.extra_specs_list.append(extra_specs)

        if isinstance(_v, Server):
            if _v.availability_zone is not None:
                if _v.availability_zone not in _group.availability_zone_list:
                    _group.availability_zone_list.append(_v.availability_zone)

        if isinstance(_v, Group):
            for az in _v.availability_zone_list:
                if az not in _group.availability_zone_list:
                    _group.availability_zone_list.append(az)

    def _set_implicit_grouping(self, _vk, _g, _affinity_map, _groups):
        """Take server's most top parent as a child group of this group _g."""

        tg = _affinity_map[_vk]    # Where _vk currently belongs to

        if tg.vid in _affinity_map.keys():    # If the parent belongs to the other parent group
            self._set_implicit_grouping(tg.vid, _g, _affinity_map, _groups)
        else:
            if LEVEL.index(tg.level) > LEVEL.index(_g.level):
                tg.level = _g.level

            if _g.is_parent_affinty(tg.vid):
                _g.subgroups[tg.vid] = tg
                tg.surgroup = _g
                _affinity_map[tg.vid] = _g

                self._add_implicit_diversity_groups(_g, tg.diversity_groups)
                self._add_implicit_quorum_diversity_groups(_g, tg.quorum_diversity_groups)
                self._add_implicit_exclusivity_groups(_g, tg.exclusivity_groups)
                self._add_memberships(_g, tg)

                del _groups[tg.vid]
