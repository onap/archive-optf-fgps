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
import operator
import time

from valet.engine.app_manager.app import App


class AppHistory(object):
    """Data container for scheduling decisions."""

    def __init__(self, _key):
        self.decision_key = _key
        self.status = None
        self.result = None
        self.timestamp = None


class AppHandler(object):
    """Handler for all requested applications."""

    def __init__(self, _dbh, _use_dha, _logger):
        self.dbh = _dbh

        self.decision_history = {}
        self.max_decision_history = 5000
        self.min_decision_history = 1000

        self.use_dha = _use_dha

        self.logger = _logger

    def validate_for_create(self, _req_id, _req):
        """Validate create request and return app."""

        app = App(_req_id, self.use_dha, self.logger)
        app.init_for_create(_req)

        if app.status != "ok" and not app.status.startswith("na:"):
            self.logger.error(app.status)
        else:
            self.logger.info("got 'create' for app = " + app.app_name)

        return app

    def validate_for_update(self, _req_id, _req):
        """Validate update request and return app."""

        app = App(_req_id, self.use_dha, self.logger)

        # Use create validation module.
        app.init_for_create(_req)
        app.state = "update"

        if app.status != "ok" and not app.status.startswith("na:"):
            self.logger.error(app.status)
        else:
            self.logger.info("got 'update' for app = " + app.app_name)

        return app

    def validate_for_delete(self, _req_id, _req):
        """Validate delete request and return app."""

        app = App(_req_id, self.use_dha, self.logger)
        app.init_for_delete(_req)

        if app.status != "ok":
            self.logger.error(app.status)
            return app

        prior_app = self.dbh.get_stack(app.app_name)
        if prior_app is None:
            return None

        if len(prior_app) == 0:
            app.status = "na: no prior request via valet"
            return app

        # Once taking prior app, valet deterimnes placements or error.
        app.init_prior_app(prior_app)

        self.logger.info("got 'delete' for app = " + app.app_name)

        return app

    def validate_for_confirm(self, _req_id, _req):
        """Validate confirm request and return app."""

        app = App(_req_id, self.use_dha, self.logger)
        app.init_for_confirm(_req)

        if app.status != "ok":
            self.logger.error(app.status)
            return app

        stack_id_map = self.dbh.get_stack_id_map(app.last_req_id)
        if stack_id_map is None:
            return None

        if len(stack_id_map) == 0:
            app.status = "na: not handled request via valet"
            return app

        prior_app = self.dbh.get_stack(stack_id_map.get("stack_id"))
        if prior_app is None:
            return None

        if len(prior_app) == 0:
            app.status = "cannot find prior stack info"
            return app

        # Once taking prior app, valet deterimnes placements or error.
        app.init_prior_app(prior_app)

        self.logger.info("got 'confirm' for app = " + app.app_name)

        return app

    def validate_for_rollback(self, _req_id, _req):
        """Validate rollback request and return app."""

        app = App(_req_id, self.use_dha, self.logger)
        app.init_for_rollback(_req)

        if app.status != "ok":
            self.logger.error(app.status)
            return app

        stack_id_map = self.dbh.get_stack_id_map(app.last_req_id)
        if stack_id_map is None:
            return None

        if len(stack_id_map) == 0:
            app.status = "na: not handled request via valet"
            return app

        prior_app = self.dbh.get_stack(stack_id_map.get("stack_id"))
        if prior_app is None:
            return None

        if len(prior_app) == 0:
            app.status = "cannot find prior stack info"
            return app

        # Once taking prior app, valet deterimnes placements or error.
        app.init_prior_app(prior_app)

        self.logger.info("got 'rollback' for app = " + app.app_name)

        return app

    def set_for_create(self, _app):
        """Set for stack-creation request."""

        # Set Valet groups.
        _app.init_valet_groups()
        if _app.status != "ok":
            return

        # Set flavor properties for each server.
        for rk, r in _app.stack.iteritems():
            if "vcpus" not in r["properties"].keys():
                flavor = _app.resource.get_flavor(r["properties"]["flavor"])

                if flavor is None:
                    _app.status = "fail to get flavor details"
                    self.logger.error(_app.status)
                    return

                if flavor.status != "enabled":
                    # TODO(Gueyoung): what to do if flavor is disabled?
                    self.logger.warning("disabled flavor = " + flavor.name)

                r["properties"]["vcpus"] = flavor.vCPUs
                r["properties"]["mem"] = flavor.mem_cap
                r["properties"]["local_volume"] = flavor.disk_cap

                if len(flavor.extra_specs) > 0:
                    extra_specs = {}
                    for mk, mv in flavor.extra_specs.iteritems():
                        extra_specs[mk] = mv
                    r["properties"]["extra_specs"] = extra_specs

        # Set servers.
        # Once parsing app, valet deterimnes placements or error.
        if not _app.parse():
            self.logger.error(_app.status)
            return

        return

    def set_for_update(self, _app):
        """Set for stack-update request."""

        # Set servers.
        # Once parsing app, valet deterimnes placements or error.
        if not _app.parse():
            self.logger.error(_app.status)
            return

        # Skip stack-update and rely on platform at this version.
        _app.status = "na:update: pass stack-update"

        return

    def check_history(self, _req_id):
        """Check if the request is determined already."""

        if _req_id in self.decision_history.keys():
            status = self.decision_history[_req_id].status
            result = self.decision_history[_req_id].result
            return status, result
        else:
            return None, None

    def record_history(self, _req_id, _status, _result):
        """Record an app placement decision."""

        if _req_id not in self.decision_history.keys():
            if len(self.decision_history) > self.max_decision_history:
                self._flush_decision_history()

            app_history = AppHistory(_req_id)
            app_history.status = _status
            app_history.result = _result
            app_history.timestamp = time.time()

            self.decision_history[_req_id] = app_history

    def _flush_decision_history(self):
        """Unload app placement decisions."""

        count = 0
        num_of_removes = len(self.decision_history) - self.min_decision_history

        remove_item_list = []
        for decision in (sorted(self.decision_history.values(), key=operator.attrgetter('timestamp'))):  # type: AppHistory
            remove_item_list.append(decision.decision_key)
            count += 1
            if count == num_of_removes:
                break

        for dk in remove_item_list:
            del self.decision_history[dk]

    def store_app(self, _app):
        """Store new app or update existing app."""

        if _app.state == "create":
            metadata = {"service_instance_id": _app.service_instance_id, "vnf_instance_id": _app.vnf_instance_id,
                        "vnf_instance_name": _app.vnf_instance_name}

            servers = {}
            for sk, s in _app.servers.iteritems():
                servers[sk] = s.get_json_info()

            if not self.dbh.create_stack(_app.app_name,
                                         _app.status,
                                         _app.datacenter_id, _app.app_name, "none",
                                         _app.tenant_id, metadata,
                                         servers, {},
                                         _app.state, "none"):
                return False
        elif _app.state in ("delete", "created"):
            metadata = {"service_instance_id": _app.service_instance_id, "vnf_instance_id": _app.vnf_instance_id,
                        "vnf_instance_name": _app.vnf_instance_name}

            if not self.dbh.update_stack(_app.app_name,
                                         _app.status,
                                         _app.datacenter_id, _app.app_name, _app.app_id,
                                         _app.tenant_id, metadata,
                                         _app.servers, _app.prior_servers,
                                         _app.state, _app.prior_state):
                return False
        elif _app.state == "deleted":
            if not self.dbh.delete_stack(_app.app_name):
                return False
        else:
            self.logger.error("unknown operaton")
            return False

        # To manage the map between request_id and Heat stack requested
        if _app.state in ("create", "delete"):
            if not self.dbh.create_stack_id_map(_app.last_req_id, _app.app_name):
                return False
        elif _app.state in ("created", "deleted"):
            if not self.dbh.delete_stack_id_map(_app.last_req_id):
                return False

        return True
