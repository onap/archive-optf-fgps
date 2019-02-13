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


from valet.engine.app_manager.group import Group, LEVEL


def get_next_placements(_n, _level):
    """Get servers and groups to be handled in the next level of search."""

    servers = {}
    groups = {}

    if isinstance(_n, Group):
        if LEVEL.index(_n.level) < LEVEL.index(_level):
            groups[_n.vid] = _n
        else:
            for _, sg in _n.subgroups.iteritems():
                if isinstance(sg, Group):
                    groups[sg.vid] = sg
                else:
                    servers[sg.vid] = sg
    else:
        servers[_n.vid] = _n

    return servers, groups
