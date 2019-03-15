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
class NUMA(object):
    """Container for NUMA cells."""

    def __init__(self, numa=None):
        """Init NUMA cells.

        Assume 2 NUMA cells of each compute host
        """

        self.cell_0 = {}

        # Available resources
        self.cell_0["cpus"] = 0
        self.cell_0["mem"] = 0

        # A list of server infos
        self.cell_0["server_list"] = []

        self.cell_1 = {}

        # Available resources
        self.cell_1["cpus"] = 0
        self.cell_1["mem"] = 0

        # A list of server infos
        self.cell_1["server_list"] = []

        if numa is not None:
            self.cell_0["cpus"] = numa["cell_0"]["cpus"]
            self.cell_0["mem"] = numa["cell_0"]["mem"]
            self.cell_0["server_list"] = numa["cell_0"]["server_list"]

            self.cell_1["cpus"] = numa["cell_1"]["cpus"]
            self.cell_1["mem"] = numa["cell_1"]["mem"]
            self.cell_1["server_list"] = numa["cell_1"]["server_list"]

    def init_cpus(self, _cpus):
        """Apply CPU capacity faily across NUMA cells.

        Caused by new compute host.
        """

        div = int(float(_cpus) / 2.0)

        self.cell_0["cpus"] = div
        self.cell_1["cpus"] = (_cpus - div)

    def init_mem(self, _mem):
        """Apply mem capacity faily across NUMA cells.

        Caused by new compute host.
        """

        div = int(float(_mem) / 2.0)

        self.cell_0["mem"] = div
        self.cell_1["mem"] = (_mem - div)

    def adjust_cpus(self, _old_cpus, _new_cpus):
        """Adjust CPU capacity across NUMA cells.

        Caused by change in compute host.
        """

        div = int(float(_old_cpus) / 2.0)

        old_cpus_0 = div
        old_cpus_1 = (_old_cpus - div)

        used_0 = old_cpus_0 - self.cell_0["cpus"]
        used_1 = old_cpus_1 - self.cell_1["cpus"]

        div = int(float(_new_cpus) / 2.0)

        self.cell_0["cpus"] = div - used_0
        self.cell_1["cpus"] = _new_cpus - div - used_1

    def adjust_mem(self, _old_mem, _new_mem):
        """Adjust mem capacity across NUMA cells.

        Caused by change in compute host.
        """

        div = int(float(_old_mem) / 2.0)

        old_mem_0 = div
        old_mem_1 = (_old_mem - div)

        used_0 = old_mem_0 - self.cell_0["mem"]
        used_1 = old_mem_1 - self.cell_1["mem"]

        div = int(float(_new_mem) / 2.0)

        self.cell_0["mem"] = div - used_0
        self.cell_1["mem"] = _new_mem - div - used_1

    def has_enough_resources(self, _vcpus, _mem):
        """Check if any cell has enough resources."""

        if _vcpus <= self.cell_0["cpus"] and _mem <= self.cell_0["mem"]:
            return True

        if _vcpus <= self.cell_1["cpus"] and _mem <= self.cell_1["mem"]:
            return True

        return False

    def pop_cell_of_server(self, _s_info):
        """Get which cell server is placed."""

        cell = None

        for s_info in self.cell_0["server_list"]:
            if _s_info["uuid"] != "none":
                if s_info["uuid"] != "none" and \
                   s_info["uuid"] == _s_info["uuid"]:
                    cell = "cell_0"
                    self.cell_0["server_list"].remove(s_info)
                    break

            if _s_info["stack_id"] != "none":
                if (s_info["stack_id"] != "none" and \
                    s_info["stack_id"] == _s_info["stack_id"]) and \
                   s_info["name"] == _s_info["name"]:
                    cell = "cell_0"
                    self.cell_0["server_list"].remove(s_info)
                    break

            if _s_info["stack_name"] != "none":
                if (s_info["stack_name"] != "none" and \
                    s_info["stack_name"] == _s_info["stack_name"]) and \
                   s_info["name"] == _s_info["name"]:
                    cell = "cell_0"
                    self.cell_0["server_list"].remove(s_info)
                    break

        if cell is None:
            for s_info in self.cell_1["server_list"]:
                if _s_info["uuid"] != "none":
                    if s_info["uuid"] != "none" and \
                       s_info["uuid"] == _s_info["uuid"]:
                        cell = "cell_1"
                        self.cell_1["server_list"].remove(s_info)
                        break

                if _s_info["stack_id"] != "none":
                    if (s_info["stack_id"] != "none" and \
                        s_info["stack_id"] == _s_info["stack_id"]) and \
                       s_info["name"] == _s_info["name"]:
                        cell = "cell_1"
                        self.cell_1["server_list"].remove(s_info)
                        break

                if _s_info["stack_name"] != "none":
                    if (s_info["stack_name"] != "none" and \
                        s_info["stack_name"] == _s_info["stack_name"]) and \
                       s_info["name"] == _s_info["name"]:
                        cell = "cell_1"
                        self.cell_1["server_list"].remove(s_info)
                        break

        if cell is None:
            return "none"
        else:
            return cell

    def deduct_server_resources(self, _s_info):
        """Reduce the available resources in a cell by adding a server."""

        self.pop_cell_of_server(_s_info)

        if self.cell_0["cpus"] > self.cell_1["cpus"]:
            self.cell_0["cpus"] -= _s_info.get("vcpus")
            self.cell_0["mem"] -= _s_info.get("mem")
            self.cell_0["server_list"].append(_s_info)
            return "cell_0"
        else:
            self.cell_1["cpus"] -= _s_info.get("vcpus")
            self.cell_1["mem"] -= _s_info.get("mem")
            self.cell_1["server_list"].append(_s_info)
            return "cell_1"

    def rollback_server_resources(self, _s_info):
        """Rollback the server placement in cell by removing server."""

        cell = self.pop_cell_of_server(_s_info)

        if cell == "cell_0":
            self.cell_0["cpus"] += _s_info.get("vcpus")
            self.cell_0["mem"] += _s_info.get("mem")
        elif cell == "cell_1":
            self.cell_1["cpus"] += _s_info.get("vcpus")
            self.cell_1["mem"] += _s_info.get("mem")

        # TODO: need to non-NUMA server?
        # else:
        #     self.apply_cpus_fairly(-1.0*_cpus)
        #     self.apply_mem_fairly(-1.0*_mem)

    def add_server(self, _s_info):
        """Add the server info into the cell."""

        if _s_info["numa"] == "cell_0":
            self.cell_0["server_list"].append(_s_info)
        elif _s_info["numa"] == "cell_1":
            self.cell_1["server_list"].append(_s_info)

    def apply_unknown_cpus(self, _diff):
        """Apply unknown cpus fairly across cells."""

        if _diff > 0:
            # Deduct

            div = int(float(_diff) / 2.0)
            self.cell_0["cpus"] -= div
            self.cell_1["cpus"] -= (_diff - div)
        elif _diff < 0:
            # Rollback
            _diff *= -1

            div = int(float(_diff) / 2.0)
            self.cell_0["cpus"] += div
            self.cell_1["cpus"] += (_diff - div)

    def apply_unknown_mem(self, _diff):
        """Apply unknown mem capacity fairly across cells."""

        if _diff > 0:
            # Deduct

            div = int(float(_diff) / 2.0)
            self.cell_0["mem"] -= div
            self.cell_1["mem"] -= (_diff - div)
        elif _diff < 0:
            # Rollback
            _diff *= -1

            div = int(float(_diff) / 2.0)
            self.cell_0["mem"] += div
            self.cell_1["mem"] += (_diff - div)

    def get_json_info(self):
        """Get NUMA info as JSON format"""

        return {'cell_0': self.cell_0,
                'cell_1': self.cell_1}
