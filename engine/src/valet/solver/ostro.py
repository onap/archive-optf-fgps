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


import json
import traceback
from datetime import datetime

from valet.engine.db_connect.locks import *


# noinspection PyBroadException
class Ostro(object):
    """Main class for scheduling and query."""

    def __init__(self, _bootstrapper):
        self.valet_id = _bootstrapper.valet_id

        self.dbh = _bootstrapper.dbh

        self.rh = _bootstrapper.rh
        self.ahandler = _bootstrapper.ah

        self.optimizer = _bootstrapper.optimizer

        self.logger = _bootstrapper.logger

        # To lock valet-engine per datacenter.
        self.lock = _bootstrapper.lock

        self.end_of_process = False

    def run_ostro(self):
        """Run main valet-engine loop."""

        self.logger.info("*** start valet-engine main loop")

        # TODO(Gueyoung): Run resource handler thread.

        try:
            # NOTE(Gueyoung): if DB causes any error, Valet-Engine exits.

            while self.end_of_process is False:

                if not self.lock.set_regions():
                    break

                request_list = self.dbh.get_requests()
                if len(request_list) > 0:
                    rc = self._handle_requests(request_list)
                    Logger.set_req_id(None)
                    if not rc:
                        break

                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.error("keyboard interrupt")
        except Exception:
            self.logger.error(traceback.format_exc())

        self.lock.done_with_my_turn()

        self.logger.info("*** exit valet-engine")

    def plan(self):
        """Handle planning requests.

        This is only for capacity planning.
        """

        self.logger.info("*** start planning......")

        request_list = self.dbh.get_requests()

        if len(request_list) > 0:
            if not self._handle_requests(request_list):
                self.logger.error("while planning")
                return False
        else:
            self.logger.error("while reading plan")
            return False

        return True

    def _handle_requests(self, _req_list):
        """Deal with all requests.

        Request types (operations) are
            Group rule management: 'group_query', 'group_create'.
            Placement management: 'create', 'delete', 'update', 'confirm', 'rollback'.
            Engine management: 'ping'.
        """

        for req in _req_list:
            req_id_elements = req["request_id"].split("-", 1)
            opt = req_id_elements[0]
            req_id = req_id_elements[1]
            Logger.set_req_id(req_id)
            begin_time = datetime.now()

            req_body = json.loads(req["request"])

            self.logger.debug("input request_type = " + opt)
            self.logger.debug("request = " + json.dumps(req_body, indent=4))

            # Check if the same request with prior request.
            (status, result) = self.ahandler.check_history(req["request_id"])

            if result is None:
                if opt in ("create", "delete", "update", "confirm", "rollback"):
                    app = self._handle_app(opt, req_id, req_body)

                    if app is None:
                        errstr = "valet-engine exits due to " + opt + " error"
                        Logger.get_logger('audit').error(errstr, beginTimestamp=begin_time, elapsedTime=datetime.now() - begin_time, statusCode=False)
                        self.logger.error(errstr)
                        return False

                    if app.status == "locked":
                        errstr = "datacenter is being serviced by another valet"
                        Logger.get_logger('audit').error(errstr, beginTimestamp=begin_time, elapsedTime=datetime.now() - begin_time, statusCode=False)
                        self.logger.info(errstr)
                        continue

                    (status, result) = self._get_json_result(app)

                elif opt in ("group_query", "group_create"):
                    # TODO(Gueyoung): group_delete and group_update

                    (status, result) = self._handle_rule(opt, req_body)

                    if result is None:
                        errstr = "valet-engine exits due to " + opt + " error"
                        Logger.get_logger('audit').error(errstr, beginTimestamp=begin_time, elapsedTime=datetime.now() - begin_time, statusCode=False)
                        self.logger.info(errstr)
                        return False

                    if status["status"] == "locked":
                        errstr = "datacenter is locked by the other valet"
                        Logger.get_logger('audit').error(errstr, beginTimestamp=begin_time, elapsedTime=datetime.now() - begin_time, statusCode=False)
                        self.logger.info(errstr)
                        continue

                elif opt == "ping":
                    # To check if the local valet-engine is alive.

                    if req_body["id"] == self.valet_id:
                        self.logger.debug("got ping")

                        status = {"status": "ok", "message": ""}
                        result = {}
                    else:
                        continue

                else:
                    status = {"status": "failed", "message": "unknown operation = " + opt}
                    result = {}

                    self.logger.error(status["message"])

            else:
                self.logger.info("decision already made")

            # Store final result in memory cache.
            if status["message"] != "timeout":
                self.ahandler.record_history(req["request_id"], status, result)

            # Return result
            if not self.dbh.return_request(req["request_id"], status, result):
                return False

            self.logger.debug("output status = " + json.dumps(status, indent=4))
            self.logger.debug("       result = " + json.dumps(result, indent=4))

            Logger.get_logger('audit').info("done request = " + req["request_id"], beginTimestamp=begin_time, elapsedTime=datetime.now() - begin_time)
            self.logger.info("done request = " + req["request_id"] + ' ----')

            # this should be handled by exceptions so we can log the audit correctly
            if self.lock.done_with_my_turn() is None:
                return False

        return True

    def _handle_app(self, _opt, _req_id, _req_body):
        """Deal with placement request.

        Placement management: 'create', 'delete', 'update', 'confirm', 'rollback'.

        Validate the request, extract info, search placements, and store results.
        """

        resource = None
        app = None

        # Validate request.
        if _opt == "create":
            app = self.ahandler.validate_for_create(_req_id, _req_body)
        elif _opt == "update":
            app = self.ahandler.validate_for_update(_req_id, _req_body)
        elif _opt == "delete":
            app = self.ahandler.validate_for_delete(_req_id, _req_body)
        elif _opt == "confirm":
            app = self.ahandler.validate_for_confirm(_req_id, _req_body)
        elif _opt == "rollback":
            app = self.ahandler.validate_for_rollback(_req_id, _req_body)

        if app is None:
            return None
        elif app.status != "ok":
            return app

        # Check if datacenter is locked.
        # Set the expired time of current lock.
        lock_status = self.lock.is_my_turn(app.datacenter_id)
        if lock_status is None:
            return None
        elif lock_status == "no":
            app.status = "locked"
            return app

        # Load valet rules.
        if self.rh.load_group_rules_from_db() is None:
            return None

        if _opt == "create":
            # Make placement decisions for newly created servers in stack.

            # Load resource (hosts, racks, metadata, groups) from DB.
            if not self.rh.load_resource(_req_body.get("datacenter")):
                return None

            resource = self.rh.resource_list[0]

            # Sync rsource status with platform (OpenStack Nova).
            if not resource.sync_with_platform():
                self.logger.error("fail to sync resource status")
                app.status = "fail to sync resource status"
                return app

            app.set_resource(resource)

            self.ahandler.set_for_create(app)
            if app is None:
                return None
            elif app.status != "ok":
                return app

            self.optimizer.place(app)
            if app.status != "ok":
                return app

        elif _opt == "update":
            # TODO(Gueyoung): assume only image update and
            # Valet does not deal with this update.

            self.ahandler.set_for_update(app)
            if app is None:
                return None
            elif app.status != "ok":
                return app

            return app

        elif _opt == "delete":
            # Mark delete state in stack and servers.

            # Load resource (hosts, racks, metadata, groups) from DB
            if not self.rh.load_resource(_req_body.get("datacenter")):
                return None

            resource = self.rh.resource_list[0]

            # Sync rsource status with platform
            if not resource.sync_with_platform():
                self.logger.error("fail to sync resource status")
                app.status = "fail to sync resource status"
                return app

            app.set_resource(resource)

            self.optimizer.update(app)
            if app.status != "ok":
                return app

        elif _opt == "confirm":
            # Confirm prior create, delete, or update request.

            datacenter_info = {"id": app.datacenter_id, "url": "none"}

            # Load resource (hosts, racks, metadata, groups) from DB
            # No sync with platform.
            if not self.rh.load_resource(datacenter_info):
                return None

            resource = self.rh.resource_list[0]

            app.set_resource(resource)

            self.optimizer.confirm(app)
            if app.status != "ok":
                return app

        elif _opt == "rollback":
            # Rollback prior create, delete, or update request.

            datacenter_info = {"id": app.datacenter_id, "url": "none"}

            # Load resource (hosts, racks, metadata, groups) from DB
            # No sync with platform.
            if not self.rh.load_resource(datacenter_info):
                return None

            resource = self.rh.resource_list[0]

            app.set_resource(resource)

            self.optimizer.rollback(app)
            if app.status != "ok":
                return app

        # Check timeout before store data.
        if self.lock.expired < now():
            app.status = "timeout"
            return app

        # Store app info into DB.
        if not self.ahandler.store_app(app):
            return None
        self.logger.info("requested app(" + app.app_name + ") is stored")

        # Store resource into DB.
        if not resource.store_resource(opt=_opt, req_id=_req_id):
            return None
        self.logger.info("resource status(" + resource.datacenter_id + ") is stored")

        # TODO(Gueyoung): if timeout happened at this moment,
        # Rollback data change.

        return app

    def _handle_rule(self, _opt, _req_body):
        """Deal with valet rule and groups request.

        Group rule management: 'group_query', 'group_create'.
        """

        status = {}

        result = None

        if _opt == "group_query":
            # Query valet group rules and server placements under rules.

            rule_name = _req_body.get("name", None)
            datacenter_id = _req_body.get("datacenter_id", None)

            if rule_name is None or rule_name == "":
                # Return basic info of all rules.

                # Load valet rules.
                if self.rh.load_group_rules_from_db() is None:
                    status["status"] = "failed"
                    status["message"] = "DB error"
                    return status, []

                result = self.rh.get_rules()
                if result is None:
                    status["status"] = "failed"
                    status["message"] = "DB error"
                    return status, []

            else:
                # Return rule info with server placements under this rule.

                if datacenter_id is None:
                    status["status"] = "failed"
                    status["message"] = "no region id given"
                    return status, {}

                # Check if datacenter is locked.
                lock_status = self.lock.is_my_turn(datacenter_id)
                if lock_status is None:
                    status["status"] = "failed"
                    status["message"] = "DB error"
                    return status, []
                elif lock_status == "no":
                    status["status"] = "locked"
                    status["message"] = ""
                    return status, {}

                message = self.rh.load_group_rule_from_db(rule_name)
                if message is None:
                    status["status"] = "failed"
                    status["message"] = "DB error while loading rule"
                    return status, {}
                elif message != "ok":
                    status["status"] = "failed"
                    status["message"] = message
                    self.logger.error(status["message"])
                    return status, {}

                datacenter_info = {"id": datacenter_id, "url": "none"}

                # Load resource data from DB.
                message = self.rh.load_resource_with_rule(datacenter_info)
                if message is None:
                    status["status"] = "failed"
                    status["message"] = "DB error while loading resource"
                    return status, {}
                elif message != "ok":
                    status["status"] = "failed"
                    status["message"] = message
                    self.logger.error(status["message"])
                    return status, {}

                resource = self.rh.resource_list[0]

                # Sync rsource status with platform
                if not resource.sync_with_platform():
                    status["status"] = "failed"
                    status["message"] = "Platform delay"
                    return status, {}

                result = self.rh.get_placements_under_rule(rule_name, resource)

                # Check timeout before store data.
                if self.lock.expired < now():
                    status["status"] = "failed"
                    status["message"] = "timeout"
                    return status, {}

                # Store resource into DB.
                if not resource.store_resource():
                    status["status"] = "failed"
                    status["message"] = "DB error while storing resource"
                    return status, {}
                self.logger.info("resource status(" + datacenter_id + ") is stored")

                # TODO(Gueyoung): If timeout happened here, Rollback stored data.

        elif _opt == "group_create":
            result = {}

            rule_name = _req_body.get("name")
            app_scope = _req_body.get("app_scope")
            rule_type = _req_body.get("type")
            level = _req_body.get("level")
            members = _req_body.get("members", [])
            desc = _req_body.get("desc", "none")

            message = self.rh.create_group_rule(rule_name, app_scope,
                                                rule_type, level,
                                                members, desc)
            if message is None:
                status["status"] = "failed"
                status["message"] = "DB error while creating rule"
                return status, {}
            elif message != "ok":
                status["status"] = "failed"
                status["message"] = message
                return status, result

        elif _opt == "group_delete":
            pass
        elif _opt == "group_update":
            pass

        status["status"] = "ok"
        status["message"] = ""

        return status, result

    def _get_json_result(self, _app):
        """Set request result format as JSON."""

        status = {"status": "ok", "message": ""}

        result = {}

        if _app.status != "ok":
            if _app.status.startswith("na:"):
                status_elements = _app.status.split(':')
                if status_elements[1].strip() != "update":
                    status["message"] = status_elements[1].strip()

                    return status, {}
            else:
                status["status"] = "failed"
                status["message"] = _app.status
                return status, {}

        if _app.state == "create":
            for sk, s in _app.servers.iteritems():
                if s.host_assignment_inx == -1:
                    result[s.host_assignment_variable] = '::' + s.host
                else:
                    p = '::' + s.host

                    if s.host_assignment_variable not in result.keys():
                        result[s.host_assignment_variable] = []
                    result[s.host_assignment_variable].insert(s.host_assignment_inx, p)
        elif _app.state == "update":
            for sk, s in _app.servers.iteritems():
                if s.host_assignment_inx == -1:
                    result[s.host_assignment_variable] = ""
                else:
                    p = ""

                    if s.host_assignment_variable not in result.keys():
                        result[s.host_assignment_variable] = []
                    result[s.host_assignment_variable].insert(s.host_assignment_inx, p)

        return status, result
