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
import glob
import json
import os
import sys

from valet.engine.app_manager.app_handler import AppHandler
from valet.engine.db_connect.db_apis.music import Music
from valet.engine.db_connect.db_handler import DBHandler
from valet.engine.db_connect.locks import Locks
from valet.engine.resource_manager.compute_manager import ComputeManager
from valet.engine.resource_manager.metadata_manager import MetadataManager
from valet.engine.resource_manager.naming import Naming
from valet.engine.resource_manager.nova_compute import NovaCompute
from valet.engine.resource_manager.resource_handler import ResourceHandler
from valet.engine.resource_manager.topology_manager import TopologyManager
from valet.engine.search.optimizer import Optimizer


class Bootstrapper(object):
    """Bootstrap valet-engine.

       Instantiate and configure all valet-engine sub-systems.
    """

    def __init__(self, _config, _logger):
        self.config = _config
        self.logger = _logger

        self.valet_id = None

        self.dbh = None
        self.ah = None
        self.rh = None
        self.compute = None
        self.topology = None
        self.metadata = None
        self.optimizer = None

        self.lock = None

    def config_valet(self):
        """Set all required modules and configure them."""

        self.valet_id = self.config["engine"]["id"]

        # Set DB connection.
        db_config = self.config.get("db")
        self.logger.info("launch engine -- keyspace: %s" % db_config.get("keyspace"))
        db = Music(self.config, self.logger)

        self.dbh = DBHandler(db, db_config, self.logger)

        # Set lock to deal with datacenters in parallel.
        self.lock = Locks(self.dbh, self.config["engine"]["timeout"])

        # Set backend platform connection.
        compute_config = self.config.get("compute")
        compute_source = NovaCompute(self.config,
                                     self.logger)

        topology_config = self.config.get("topology")
        topology_source = Naming(self.config.get("naming"), self.logger)

        self.compute = ComputeManager(compute_source, self.logger)
        self.topology = TopologyManager(topology_source, self.logger)
        self.metadata = MetadataManager(compute_source, self.logger)

        # Set resource handler.
        self.rh = ResourceHandler("ResourceHandler",
                                  self.dbh,
                                  self.compute,
                                  self.metadata,
                                  self.topology,
                                  compute_config,
                                  self.logger)

        dha = self.config["engine"]["dha"]
        use_dha = True
        if dha == "false" or not dha:
            use_dha = False

        # Set application handler.
        self.ah = AppHandler(self.dbh, use_dha, self.logger)

        # Set optimizer for placement decisions.
        self.optimizer = Optimizer(self.logger)

        # Read initial Valet Group rules and create in DB.
        root = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
        for rule_file in glob.glob(root + "/valet/rules/" + "*.json"):
            rule = json.loads(open(rule_file).read())
            self.dbh.create_group_rule(
                rule["name"],
                rule["app_scope"],
                rule["type"],
                rule["level"],
                rule["members"],
                rule["description"]
            )

            self.logger.debug("rule (" + rule["name"] + ") created")

        return True
