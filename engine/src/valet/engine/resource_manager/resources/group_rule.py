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


class GroupRule(object):
    """Container for valet group rule."""

    def __init__(self, _id):
        self.rule_id = _id

        self.status = "enabled"

        self.app_scope = "lcp"
        self.rule_type = "affinity"
        self.level = "host"

        self.members = []    # a lit of tenent ids who can use this rule

        self.desc = None

        # self.groups = []    # a list of group ids generated under this rule

        self.updated = False

    def get_json_info(self):
        """Get group info as JSON format."""

        return {'status': self.status,
                'app_scope': self.app_scope,
                'rule_type': self.rule_type,
                'level': self.level,
                'members': self.members,
                'desc': self.desc
                # 'groups': self.groups
                }
