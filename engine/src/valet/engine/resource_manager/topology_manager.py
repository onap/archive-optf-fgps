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


from valet.engine.resource_manager.resources.datacenter import Datacenter
from valet.engine.resource_manager.resources.host_group import HostGroup


class TopologyManager(object):
    """Manager to maintain the layout of datacenter."""

    def __init__(self, _source, _logger):
        self.source = _source

        self.datacenter = None
        self.host_groups = {}
        self.hosts = {}

        self.logger = _logger

    def get_topology(self, _resource):
        """Set datacenter layout into resource."""

        self.logger.info("set datacenter layout...")

        # Init first
        self.datacenter = Datacenter(_resource.datacenter_id)
        self.host_groups.clear()
        self.hosts.clear()

        if self.source.get_topology(self.datacenter, self.host_groups, self.hosts,
                                    _resource.hosts) != "ok":
            return False

        self._check_updated(_resource)

        return True

    def _check_updated(self, _resource):
        """Check if the layout is changed."""

        if _resource.datacenter is None:
            _resource.datacenter = Datacenter(_resource.datacenter_id)
            _resource.datacenter.updated = True

            self.logger.info("new datacenter (" + _resource.datacenter_id + ") added")

        for hgk in self.host_groups.keys():
            if hgk not in _resource.host_groups.keys():
                new_host_group = HostGroup(hgk)
                new_host_group.host_type = self.host_groups[hgk].host_type

                _resource.host_groups[new_host_group.name] = new_host_group
                _resource.mark_host_group_updated(hgk)

                self.logger.info("new host_group (" + hgk + ") added")

        for rhgk in _resource.host_groups.keys():
            if rhgk not in self.host_groups.keys():
                host_group = _resource.host_groups[rhgk]
                host_group.status = "disabled"
                host_group.mark_host_group_updated(rhgk)

                self.logger.info("host_group (" + rhgk + ") disabled")

        # TODO(Gueyoung): what if host exists in topology,
        # but does not in resource (DB or platform)?

        for rhk in _resource.hosts.keys():
            if not _resource.hosts[rhk].is_available():
                continue

            if rhk not in self.hosts.keys():
                _resource.hosts[rhk].status = "disabled"
                _resource.mark_host_updated(rhk)

                self.logger.info("host (" + rhk + ") removed from topology")

        if self._is_datacenter_updated(_resource):
            _resource.datacenter.updated = True

        for hgk in self.host_groups.keys():
            hg = self.host_groups[hgk]

            if self._is_host_group_updated(hg, _resource):
                _resource.mark_host_group_updated(hgk)

        for hk in self.hosts.keys():
            if hk in _resource.hosts.keys():
                if not _resource.hosts[hk].is_available():
                    continue

                host = self.hosts[hk]

                if self._is_host_updated(host, _resource):
                    _resource.mark_host_updated(hk)

        # TODO(Gueyoung): Hierachical failure propagation

    def _is_datacenter_updated(self, _resource):
        """Check if datacenter's resources are changed."""

        updated = False

        _rdatacenter = _resource.datacenter

        for rk in self.datacenter.resources.keys():

            h = None
            if rk in _resource.host_groups.keys():
                h = _resource.host_groups[rk]
            elif rk in _resource.hosts.keys():
                h = _resource.hosts[rk]

            if h is not None and h.is_available():
                if rk not in _rdatacenter.resources.keys() or h.updated:
                    _rdatacenter.resources[rk] = h
                    updated = True

                    self.logger.info("datacenter updated (new resource)")

        for rk in _rdatacenter.resources.keys():

            h = None
            if rk in _resource.host_groups.keys():
                h = _resource.host_groups[rk]
            elif rk in _resource.hosts.keys():
                h = _resource.hosts[rk]

            if h is None or \
               not h.is_available() or \
               rk not in self.datacenter.resources.keys():
                del _rdatacenter.resources[rk]
                updated = True

                self.logger.info("datacenter updated (resource removed)")

        return updated

    def _is_host_group_updated(self, _hg, _resource):
        """Check if host_group's parent or children are changed."""

        updated = False

        _rhg = _resource.host_groups[_hg.name]

        if _hg.host_type != _rhg.host_type:
            _rhg.host_type = _hg.host_type
            updated = True
            self.logger.info("host_group (" + _rhg.name + ") updated (hosting type)")

        if _rhg.parent_resource is None or \
           _rhg.parent_resource.name != _hg.parent_resource.name:
            if _hg.parent_resource.name in _resource.host_groups.keys():
                hg = _resource.host_groups[_hg.parent_resource.name]
                if hg.is_available():
                    _rhg.parent_resource = hg
                    updated = True
            elif _hg.parent_resource.name == _resource.datacenter.name:
                _rhg.parent_resource = _resource.datacenter
                updated = True

            if updated:
                self.logger.info("host_group (" + _rhg.name + ") updated (parent host_group)")

        for rk in _hg.child_resources.keys():

            h = None
            if rk in _resource.hosts.keys():
                h = _resource.hosts[rk]
            elif rk in _resource.host_groups.keys():
                h = _resource.host_groups[rk]

            if h is not None and h.is_available():
                if rk not in _rhg.child_resources.keys() or h.updated:
                    _rhg.child_resources[rk] = h
                    updated = True

                    self.logger.info("host_group (" + _rhg.name + ") updated (new child host)")

        for rk in _rhg.child_resources.keys():

            h = None
            if rk in _resource.hosts.keys():
                h = _resource.hosts[rk]
            elif rk in _resource.host_groups.keys():
                h = _resource.host_groups[rk]

            if h is None or \
               not h.is_available() or \
               rk not in _hg.child_resources.keys():
                del _rhg.child_resources[rk]
                updated = True

                self.logger.info("host_group (" + _rhg.name + ") updated (child host removed)")

        return updated

    def _is_host_updated(self, _host, _resource):
        """Check if host's parent (e.g., rack) is changed."""

        updated = False

        _rhost = _resource.hosts[_host.name]

        if _rhost.host_group is None or \
           _rhost.host_group.name != _host.host_group.name:
            if _host.host_group.name in _resource.host_groups.keys():
                rhost_group = _resource.host_groups[_host.host_group.name]
                if rhost_group.is_available():
                    _rhost.host_group = rhost_group
                    updated = True
            elif _host.host_group.name == _resource.datacenter.name:
                _rhost.host_group = _resource.datacenter
                updated = True

        if updated:
            self.logger.info("host (" + _rhost.name + ") updated (host_group)")

        return False
