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
package org.onap.fgps.api.service;

import org.apache.catalina.connector.Response;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import org.onap.fgps.api.beans.schema.Schema;
import org.onap.fgps.api.dao.ValetServicePlacementDAO;
import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.onap.fgps.api.utils.Constants;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

@Service
public class ValetGroupsService {
	private ValetServicePlacementDAO valetServicePlacementDAO;
	private Schema schema;
	private static final EELFLoggerDelegate LOGGER = EELFLoggerDelegate.getLogger(ValetGroupsService.class);

	@Autowired
	public ValetGroupsService(ValetServicePlacementDAO valetServicePlacementDAO, Schema schema) {
		super();
		this.valetServicePlacementDAO = valetServicePlacementDAO;
		this.schema = schema;
	}

	public static JSONObject parseToJSON(String jsonString) {
	    LOGGER.info(EELFLoggerDelegate.applicationLogger,"parseToJSON : parsing json");
		JSONParser parser = new JSONParser();
		try {
			JSONObject json = (JSONObject) parser.parse(jsonString);
			return json;
		} catch (ParseException e) {
			e.printStackTrace();
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"parseToJSON : Error in parsing JSON : "+ e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"parseToJSON : Error in parsing JSON  : "+ e.getMessage());
			return null;
		}
	}
	
	public String authorizeAAF() {
		
		return "";
	}

	public ResponseEntity<String> saveGroupsRequest(JSONObject request, String operation, String requestId) {
	    LOGGER.info(EELFLoggerDelegate.applicationLogger,"SaveGroupRequest : request passed", requestId);
	    
		String dbRequest = schema.formMsoInsertUpdateRequest(requestId, operation, request.toJSONString());
		String insertRow = valetServicePlacementDAO.insertRow(dbRequest);
		return pollForResult(request, operation + "-" + requestId, Constants.WAIT_UNITL_SECONDS,
				Constants.POLL_EVERY_SECONDS);

	}
	//Junit integration test method
	public ResponseEntity<String> saveGroupsRequest1(JSONObject request, String operation, String requestId) {
	    LOGGER.info(EELFLoggerDelegate.applicationLogger,"SaveGroupRequest : request passed", requestId);
	    
		String dbRequest = schema.formMsoInsertUpdateRequest(requestId, operation, request.toJSONString());
		return ResponseEntity.ok(dbRequest);

	}

	public ResponseEntity<String> pollForResult(JSONObject values, String requestId, int waitUntilSeconds,
			int pollEverySeconds) {
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"pollForResult : called", requestId);

		String result = null;
		long waitUntil = System.currentTimeMillis() + (1000 * waitUntilSeconds);
		int counter = 1;

		JSONObject response = new JSONObject();
		boolean isTimedOut = false;
		while (true) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"pollForResult : polling database - ", counter++);
			result = valetServicePlacementDAO.getRowFromResults(requestId);
			response = result != null ? parseToJSON(result) : null;

			if (response != null && ((JSONObject) response.get("result")).get("row 0") != null) {
				LOGGER.debug(EELFLoggerDelegate.debugLogger,"pollForResult : response recieved", result);
				valetServicePlacementDAO.deleteRowFromResults(requestId, schema.formMsoDeleteRequest());
			}
			if (System.currentTimeMillis() < waitUntil
					&&( response == null || ((JSONObject) response.get("result")).get("row 0") == null)) {
				try {
					Thread.sleep(1000 * pollEverySeconds);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			} else {
				break;
			}
		}
		if (System.currentTimeMillis()>waitUntil) {
			return ResponseEntity.status(Response.SC_GATEWAY_TIMEOUT).body("Request timedout");
		}
		System.out.println("Response"+ ((JSONObject)((JSONObject) response.get("result")).get("row 0")).toJSONString());
		JSONObject obj = ((JSONObject)((JSONObject) response.get("result")).get("row 0"));
		obj.put("result",( (String) obj.get("result")));
		return ResponseEntity.ok(obj.toJSONString());
	}
	
}
