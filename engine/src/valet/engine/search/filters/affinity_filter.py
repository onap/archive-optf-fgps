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


class AffinityFilter(object):

    def __init__(self):
        self.name = "affinity"

        self.affinity_id = None
        self.is_first = True

        self.status = None

    def init_condition(self):
        self.affinity_id = None
        self.is_first = True
        self.status = None

    def check_pre_condition(self, _level, _v, _avail_hosts, _avail_groups):
        if isinstance(_v, Group):
            self.affinity_id = _v.vid

            if self.affinity_id in _avail_groups.keys():
                self.is_first = False

        if self.affinity_id is not None:
            return True
        else:
            return False

    def filter_candidates(self, _level, _v, _candidate_list):
        if self.is_first:
            return _candidate_list

        candidate_list = []

        for c in _candidate_list:
            if self._check_candidate(_level, c):
                candidate_list.append(c)

        return candidate_list

    def _check_candidate(self, _level, _candidate):
        """Filter based on named affinity group."""

        memberships = _candidate.get_all_memberships(_level)
        for gk, gr in memberships.iteritems():
            if gr.group_type == "affinity" and gk == self.affinity_id:
                return True

        return False
