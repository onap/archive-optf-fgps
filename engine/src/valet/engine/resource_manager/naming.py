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


import copy
import re

from sre_parse import isdigit
from valet.engine.resource_manager.resources.host_group import HostGroup


class Naming(object):
    """Using cannonical naming convention to capture datacenter layout."""

    def __init__(self, _config, _logger):
        self.logger = _logger

        self.rack_code_list = _config.get("rack_codes")
        self.host_code_list = _config.get("host_codes")

    def get_topology(self, _datacenter, _host_groups, _hosts, _rhosts):
        """Set datacenter resource structure (racks, hosts)."""

        status = "ok"

        for rhk, rhost in _rhosts.iteritems():
            h = copy.deepcopy(rhost)

            (rack_name, parsing_status) = self._set_layout_by_name(rhk)
            if parsing_status != "ok":
                self.logger.warning(parsing_status + " in host_name (" + rhk + ")")

            if rack_name == "none":
                h.host_group = _datacenter
                _datacenter.resources[rhk] = h
            else:
                if rack_name not in _host_groups.keys():
                    host_group = HostGroup(rack_name)
                    host_group.host_type = "rack"
                    _host_groups[host_group.name] = host_group
                else:
                    host_group = _host_groups[rack_name]

                h.host_group = host_group
                host_group.child_resources[rhk] = h

            _hosts[h.name] = h

        for hgk, hg in _host_groups.iteritems():
            hg.parent_resource = _datacenter
            _datacenter.resources[hgk] = hg

        if "none" in _host_groups.keys():
            self.logger.warning("some hosts are into unknown rack")

        return status

    def _set_layout_by_name(self, _host_name):
        """Set the rack-host layout, use host nameing convention.

        Naming convention includes
            zone name is any word followed by at least one of [0-9]
            rack name is rack_code followd by at least one of [0-9]
            host name is host_code followed by at least one of [0-9]
            an example is
                'abcd_001A' (as a zone_name) +
                'r' (as a rack_code) + '01A' +
                'c' (as a host_code) + '001A'
        """

        zone_name = None
        rack_name = None
        host_name = None

        # To check if zone name follows the rule
        index = 0
        for c in _host_name:
            if isdigit(c):
                break
            index += 1
        zone_indicator = _host_name[index:]
        if len(zone_indicator) == 0:
            return 'none', "no numberical digit in name"

        # To extract rack indicator
        for rack_code in self.rack_code_list:
            rack_index_list = [rc.start() for rc in re.finditer(rack_code, zone_indicator)]

            start_of_rack_index = -1
            for rack_index in rack_index_list:
                rack_prefix = rack_index + len(rack_code)
                if rack_prefix > len(zone_indicator):
                    continue

                # Once rack name follows the rule
                if isdigit(zone_indicator[rack_prefix]):
                    rack_indicator = zone_indicator[rack_prefix:]

                    # To extract host indicator
                    for host_code in self.host_code_list:
                        host_index_list = [hc.start() for hc in re.finditer(host_code, rack_indicator)]

                        start_of_host_index = -1
                        for host_index in host_index_list:
                            host_prefix = host_index + len(host_code)
                            if host_prefix > len(rack_indicator):
                                continue

                            if isdigit(rack_indicator[host_prefix]):
                                host_name = rack_indicator[host_index:]
                                start_of_host_index = rack_index + host_index + 1
                                break

                        if host_name is not None:
                            rack_name = zone_indicator[rack_index:start_of_host_index]
                            break

                    if rack_name is not None:
                        start_of_rack_index = index + rack_index
                        break

            if rack_name is not None:
                zone_name = _host_name[:start_of_rack_index]
                break

        if rack_name is None:
            return 'none', "no host or rack name found in " + _host_name
        else:
            return zone_name + rack_name, "ok"
