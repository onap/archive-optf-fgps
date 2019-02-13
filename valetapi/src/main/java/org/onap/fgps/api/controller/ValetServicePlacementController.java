/* 
 * ============LICENSE_START========================================== 
 * ONAP - F-GPS API 
 * =================================================================== 
 * Copyright © 2019 ATT Intellectual Property. All rights reserved. 
 * =================================================================== 
 * 
 * Unless otherwise specified, all software contained herein is licensed 
 * under the Apache License, Version 2.0 (the "License"); 
 * you may not use this software except in compliance with the License. 
 * You may obtain a copy of the License at 
 * 
 *             http://www.apache.org/licenses/LICENSE-2.0 
 * 
 * Unless required by applicable law or agreed to in writing, software 
 * distributed under the License is distributed on an "AS IS" BASIS, 
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
 * See the License for the specific language governing permissions and 
 * limitations under the License. 
 * 
 * Unless otherwise specified, all documentation contained herein is licensed 
 * under the Creative Commons License, Attribution 4.0 Intl. (the "License"); 
 * you may not use this documentation except in compliance with the License. 
 * You may obtain a copy of the License at 
 * 
 *             https://creativecommons.org/licenses/by/4.0/ 
 * 
 * Unless required by applicable law or agreed to in writing, documentation 
 * distributed under the License is distributed on an "AS IS" BASIS, 
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
 * See the License for the specific language governing permissions and 
 * limitations under the License. 
 * 
 * ============LICENSE_END============================================ 
 * 
 * 
 */
package org.onap.fgps.api.controller;

import javax.servlet.http.HttpServletRequest;

import org.json.simple.JSONObject;
import org.onap.fgps.api.annotation.PropertyBasedAuthorization;
import org.onap.fgps.api.helpers.Helper;
import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.onap.fgps.api.logging.aspect.AuditLog;
import org.onap.fgps.api.logging.aspect.MetricsLog;
import org.onap.fgps.api.service.ValetPlacementService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.context.annotation.EnableAspectJAutoProxy;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.onap.fgps.api.utils.UserUtils;

@CrossOrigin(origins = "*")
@RestController
@EnableAutoConfiguration
@RequestMapping("/placement/v1/")
@EnableAspectJAutoProxy
@AuditLog
@MetricsLog
public class ValetServicePlacementController {

	private ValetPlacementService valetPlacementService;
	private static final EELFLoggerDelegate LOGGER = EELFLoggerDelegate.getLogger(ValetServicePlacementController.class);

	@Autowired
	public ValetServicePlacementController(ValetPlacementService valetPlacementService) {
		super();
		this.valetPlacementService = valetPlacementService;
	}
	
	@PropertyBasedAuthorization("placement.create")
	@RequestMapping(consumes = "application/json", method = RequestMethod.POST)
	public ResponseEntity<String> createVm(HttpServletRequest httpRequest, @RequestBody JSONObject request, @RequestParam("requestId") String requestId) {
		requestId = UserUtils.htmlEscape(requestId);
		LOGGER.debug(EELFLoggerDelegate.debugLogger,"createVm: Initiating request to create VM for request: {}, requestId: {}", request, requestId);
		return valetPlacementService.processMSORequest1(request, requestId, "create");
	}
	
	@PropertyBasedAuthorization("placement.update")
	@RequestMapping( consumes = "application/json", method = RequestMethod.PUT)
	public ResponseEntity<String> updateVm(HttpServletRequest httpRequest, @RequestBody JSONObject request, @RequestParam("requestId") String requestId) {
		requestId = UserUtils.htmlEscape(requestId);
		LOGGER.debug(EELFLoggerDelegate.debugLogger,"updateVm: Initiating request to update VM for request: {}, requestId: {}", request, requestId);
		return valetPlacementService.processMSORequest1(request,requestId,"update");
	}
	@PropertyBasedAuthorization("placement.delete")
	@RequestMapping(consumes = "application/json", method = RequestMethod.DELETE)
	public ResponseEntity<String> deleteVm(HttpServletRequest httpRequest, @RequestBody JSONObject request, @RequestParam("requestId") String requestId) {
		requestId = UserUtils.htmlEscape(requestId);
		LOGGER.debug(EELFLoggerDelegate.debugLogger,"deleteVm: Initiating request to delete VM for request: {}, requestId: {}", request, requestId);
		return valetPlacementService.saveRequest(Helper.formatDeleteRequest(request), "delete", requestId);
	}
	@PropertyBasedAuthorization("placement.confirm")
	@RequestMapping(value = "/{priorRequestId}/confirm", consumes = "application/json", method = RequestMethod.PUT)
	public ResponseEntity<String> confirm(HttpServletRequest httpRequest, @PathVariable("priorRequestId") String priorRequestId, @RequestBody JSONObject request){
		priorRequestId = UserUtils.htmlEscape(priorRequestId);
		LOGGER.debug(EELFLoggerDelegate.debugLogger,"confirm: Initiating request to confirm VM for request: {}, priorRequestId: {}", request, priorRequestId);
		return valetPlacementService.saveRequest(request, "confirm", priorRequestId);
	}
	@PropertyBasedAuthorization("placement.rollback")
	@RequestMapping(value = "/{priorRequestId}/rollback", consumes = "application/json", method = RequestMethod.PUT)
	public ResponseEntity<String> rollback(HttpServletRequest httpRequest, @PathVariable("priorRequestId") String priorRequestId, @RequestBody JSONObject request) {
		priorRequestId = UserUtils.htmlEscape(priorRequestId);
		LOGGER.debug(EELFLoggerDelegate.debugLogger,"rollback: Initiating request to rollback VM for request: {}, priorRequestId: {}", request, priorRequestId);
		return valetPlacementService.saveRequest(request, "rollback", priorRequestId);
	}

	//Unit test cases mocked controllers 
	@RequestMapping(value = "/createVM2", consumes = "application/json", method = RequestMethod.POST)
	public ResponseEntity<String> createVm2(@RequestBody JSONObject request, @RequestParam("requestId") String requestId) {
		requestId = UserUtils.htmlEscape(requestId);
		ResponseEntity<String> response = valetPlacementService.processMSORequest2(request, requestId);
		return valetPlacementService.processMSORequest2(request, requestId);
	}

	@RequestMapping(value = "/updateVm1", consumes = "application/json", method = RequestMethod.PUT)
	public ResponseEntity<String> updateVm1(@RequestBody JSONObject request, @RequestParam("requestId") String requestId) {
		requestId = UserUtils.htmlEscape(requestId);
		return valetPlacementService.processMSORequest2(request,requestId);
	}

	@RequestMapping(value = "/deleteVm1",consumes = "application/json", method = RequestMethod.DELETE)
	public ResponseEntity<String> deleteVm1(@RequestBody JSONObject request, @RequestParam("requestId") String requestId) {
		requestId = UserUtils.htmlEscape(requestId);
		return valetPlacementService.saveRequesttest(Helper.formatDeleteRequest(request), "delete", requestId);
	}

	@RequestMapping(value = "/{priorRequestId}/confirm1", consumes = "application/json", method = RequestMethod.PUT)
	public ResponseEntity<String> confirm1(@PathVariable("priorRequestId") String priorRequestId, @RequestBody JSONObject request) {
		priorRequestId = UserUtils.htmlEscape(priorRequestId);
		return valetPlacementService.saveRequesttest(request, "confirm", priorRequestId);
	}

	@RequestMapping(value = "/{priorRequestId}/rollback1", consumes = "application/json", method = RequestMethod.PUT)
	public ResponseEntity<String> rollback1(@PathVariable("priorRequestId") String priorRequestId, @RequestBody JSONObject request) {
		priorRequestId = UserUtils.htmlEscape(priorRequestId);
		return valetPlacementService.saveRequesttest(request, "rollback", priorRequestId);
	}


}
