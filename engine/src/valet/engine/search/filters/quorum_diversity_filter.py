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
import math


class QuorumDiversityFilter(object):

    def __init__(self):
        self.name = "quorum-diversity"

        self.quorum_diversity_group_list = []

        self.status = None

    def init_condition(self):
        self.quorum_diversity_group_list = []
        self.status = None

    def check_pre_condition(self, _level, _v, _avail_hosts, _avail_groups):
        if len(_v.quorum_diversity_groups) > 0:
            for _, qdiv_group in _v.quorum_diversity_groups.items():
                if qdiv_group.level == _level:
                    self.quorum_diversity_group_list.append(qdiv_group)

        if len(self.quorum_diversity_group_list) > 0:
            return True
        else:
            return False

    def filter_candidates(self, _level, _v, _candidate_list):
        candidate_list = []

        # First, try diversity rule.

        for c in _candidate_list:
            if self._check_diversity_candidate(_level, c):
                candidate_list.append(c)

        if len(candidate_list) > 0:
            return candidate_list

        # Second, if no available hosts for diversity rule, try quorum rule.

        for c in _candidate_list:
            if self._check_quorum_candidate(_level, c):
                candidate_list.append(c)

        return candidate_list

    def _check_diversity_candidate(self, _level, _candidate):
        """Filter based on named diversity groups."""

        memberships = _candidate.get_memberships(_level)

        for qdiv in self.quorum_diversity_group_list:
            for gk, gr in memberships.items():
                if gr.group_type == "quorum-diversity" and gk == qdiv.vid:
                    return False

        return True

    def _check_quorum_candidate(self, _level, _candidate):
        """Filter based on quorum-diversity rule."""

        memberships = _candidate.get_memberships(_level)
        hk = _candidate.get_resource_name(_level)

        for qdiv in self.quorum_diversity_group_list:
            # Requested num of servers under this rule
            total_num_of_servers = len(qdiv.server_list)

            num_of_placed_servers_in_candidate = -1

            for gk, gr in memberships.items():
                if gr.group_type == "quorum-diversity" and gk == qdiv.vid:
                    # Total num of servers under this rule
                    total_num_of_servers += gr.original_num_of_placed_servers

                    if hk in gr.num_of_placed_servers_of_host.keys():
                        num_of_placed_servers_in_candidate = gr.num_of_placed_servers_of_host[hk]

                    break

            # Allowed maximum num of servers per host
            quorum = max(math.ceil(float(total_num_of_servers) / 2.0 - 1.0), 1.0)

            if num_of_placed_servers_in_candidate >= quorum:
                return False

        return True
