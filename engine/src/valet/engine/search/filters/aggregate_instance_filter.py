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
import filter_utils
import six


_SCOPE = 'aggregate_instance_extra_specs'


class AggregateInstanceExtraSpecsFilter(object):
    """AggregateInstanceExtraSpecsFilter works with InstanceType records."""

    def __init__(self):
        self.name = "aggregate-instance-extra-specs"
        self.avail_hosts = {}
        self.status = None

    def init_condition(self):
        self.avail_hosts = {}
        self.status = None

    def check_pre_condition(self, _level, _v, _avail_hosts, _avail_groups):
        if len(_v.extra_specs_list) > 0:
            self.avail_hosts = _avail_hosts
            return True
        else:
            return False

    def filter_candidates(self, _level, _v, _candidate_list):
        candidate_list = []

        for c in _candidate_list:
            if self._check_candidate(_level, _v, c):
                candidate_list.append(c)

        return candidate_list

    def _check_candidate(self, _level, _v, _candidate):
        """Check given candidate host if instance's extra specs matches to metadata."""

        # If the candidate's host_type is not determined, skip the filter.
        if _level == "host":
            if len(_candidate.candidate_host_types) > 0:
                return True
        else:
            # In rack level, if any host's host_type in the rack is not determined,
            # skip the filter
            for _, rh in self.avail_hosts.iteritems():
                if rh.rack_name == _candidate.rack_name:
                    if len(rh.candidate_host_types) > 0:
                        return True

        metadatas = filter_utils.aggregate_metadata_get_by_host(_level, _candidate)

        for extra_specs in _v.extra_specs_list:
            for gk, metadata in metadatas.iteritems():
                if self._match_metadata(gk, extra_specs, metadata):
                    break
            else:
                return False

        return True

    def _match_metadata(self, _g_name, _extra_specs, _metadata):
        """Match conditions
           - No extra_specs
           - Different SCOPE of extra_specs keys
           - key of extra_specs exists in metadata & any value matches
        """

        for key, req in six.iteritems(_extra_specs):
            scope = key.split(':', 1)
            if len(scope) > 1:
                if scope[0] != _SCOPE:
                    continue
                else:
                    del scope[0]
            key = scope[0]

            aggregate_vals = _metadata.get(key, None)
            if not aggregate_vals:
                return False

            for aggregate_val in aggregate_vals:
                if filter_utils.match(aggregate_val, req):
                    break
            else:
                return False

        return True
