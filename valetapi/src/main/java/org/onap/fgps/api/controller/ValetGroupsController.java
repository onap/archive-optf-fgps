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
import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.onap.fgps.api.logging.aspect.AuditLog;
import org.onap.fgps.api.logging.aspect.MetricsLog;
import org.onap.fgps.api.service.ValetGroupsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.context.annotation.EnableAspectJAutoProxy;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.onap.fgps.api.utils.UserUtils;

@CrossOrigin(origins = "*")
@RestController
@EnableAutoConfiguration
@RequestMapping("/groups/v1/")
@EnableAspectJAutoProxy
@AuditLog
@MetricsLog
public class ValetGroupsController {
	private ValetGroupsService valetGroupsService;
	private EELFLoggerDelegate LOGGER = EELFLoggerDelegate.getLogger(ValetGroupsController.class);
	@Autowired
	public ValetGroupsController(ValetGroupsService valetGroupsService) {
		super();
		this.valetGroupsService = valetGroupsService;
	}


	@PropertyBasedAuthorization("groups.query")
	@SuppressWarnings("unchecked")
	@RequestMapping(consumes = "application/json", method = RequestMethod.GET)
	public ResponseEntity<String> queryGroups(@RequestParam("requestId") String requestId,
			@RequestParam(value = "name", required = false) String name,
			@RequestParam(value = "datacenter_id", required = false) String datacenterId,
			@RequestParam(value = "host", required = false) String host) {
		requestId = UserUtils.htmlEscape(requestId);
		name = UserUtils.htmlEscape(name);
		datacenterId = UserUtils.htmlEscape(datacenterId);
		host = UserUtils.htmlEscape(host);
		
	    LOGGER.info(EELFLoggerDelegate.applicationLogger,"queryGroups controller - ", requestId);
		JSONObject requestJson = new JSONObject();
		if(name !=null && datacenterId !=null) {
			requestJson.put("name", name);
			requestJson.put("datacenter_id", datacenterId);
		}
		LOGGER.debug(EELFLoggerDelegate.debugLogger,"queryGroups: Initiating request to query groups for requestJson: {}, requestId: {}", requestJson, requestId);
		return valetGroupsService.saveGroupsRequest(requestJson, "group_query", requestId);
	}
	@PropertyBasedAuthorization("groups.create")
	@RequestMapping(consumes = "application/json", method = RequestMethod.POST)
	public ResponseEntity<String> getCreateDetails(HttpServletRequest httpRequest, @RequestBody JSONObject request, @RequestParam("requestId") String requestId) {
		requestId = UserUtils.htmlEscape(requestId);
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"getCreateDetails controller - ", requestId);
		LOGGER.debug(EELFLoggerDelegate.debugLogger,"getCreateDetails: Initiating request to get create groups details for requestJson: {}, requestId: {}", request, requestId);
		return valetGroupsService.saveGroupsRequest(request, "group_create", requestId);
	}
	@PropertyBasedAuthorization("groups.update")
	@RequestMapping(consumes = "application/json", method = RequestMethod.PUT)
	public ResponseEntity<String> getUpdateDetails(HttpServletRequest httpRequest, @RequestBody JSONObject request, @RequestParam("requestId") String requestId) {
		requestId = UserUtils.htmlEscape(requestId);
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"getUpdateDetails controller - ", requestId);
		LOGGER.debug(EELFLoggerDelegate.debugLogger,"getCreateDetails: Initiating request to get update groups details for requestJson: {}, requestId: {}", request, requestId);
		return valetGroupsService.saveGroupsRequest(request, "group_update", requestId);
	}
	@PropertyBasedAuthorization("groups.delete")
	@RequestMapping(consumes = "application/json", method = RequestMethod.DELETE)
	public ResponseEntity<String> getDeleteDetails(HttpServletRequest httpRequest, @RequestBody JSONObject request, @RequestParam("requestId") String requestId) {
		requestId = UserUtils.htmlEscape(requestId);
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"getDeleteDetails controller - ", requestId);
		LOGGER.debug(EELFLoggerDelegate.debugLogger,"getDeleteDetails: Initiating request to get delete groups details for requestJson: {}, requestId: {}", request, requestId);
		return valetGroupsService.saveGroupsRequest(request, "group_delete", requestId);
	}
	
	//j unit test cases controller
	@SuppressWarnings("unchecked")
	@RequestMapping(value = "portal", method = RequestMethod.GET)
	public ResponseEntity<String> queryGroups1(@RequestParam("requestId") String requestId,
			@RequestParam(value = "name", required = false) String name,
			@RequestParam(value = "datacenter_id", required = false) String datacenterId,
			@RequestParam(value = "host", required = false) String host) {
		requestId = UserUtils.htmlEscape(requestId);
		name = UserUtils.htmlEscape(name);
		datacenterId = UserUtils.htmlEscape(datacenterId);
		host = UserUtils.htmlEscape(host);
		
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"queryGroups controller - ", requestId);
		JSONObject requestJson = new JSONObject();
		if(name !=null && datacenterId !=null) {
			requestJson.put("name", name);
			requestJson.put("datacenter_id", datacenterId);
		}

		return valetGroupsService.saveGroupsRequest1(requestJson, "group_query", requestId);
	}
}
