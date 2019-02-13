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

import java.io.InputStream;
import java.util.Properties;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import org.onap.fgps.api.annotation.AafRoleRequired;
import org.onap.fgps.api.annotation.BasicAuthRequired;
import org.onap.fgps.api.annotation.PropertyBasedAuthorization;
import org.onap.fgps.api.beans.Status;
import org.onap.fgps.api.beans.schema.Schema;
import org.onap.fgps.api.dao.ValetServicePlacementDAO;
import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.onap.fgps.api.utils.Constants;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import org.onap.fgps.api.utils.UserUtils;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

@CrossOrigin(origins = "*")
@RestController
@EnableAutoConfiguration
@RequestMapping("/")
public class ValetUtilityController {

	//static final Logger LOGGER = LoggerFactory.getLogger(ValetServiceApplication.class);
	private static EELFLoggerDelegate LOGGER = EELFLoggerDelegate.getLogger(ValetGroupsController.class);
	
	@Value("${logging.ping:false}")
	private boolean pingLogFlag;
	
	@RequestMapping(value = "/alive", produces = "text/plain")
	public String alive() {
		return "ok";
	}

	@SuppressWarnings("unchecked")
	@RequestMapping(value = "/ping", method = RequestMethod.GET)
	public ResponseEntity<String> ping() {
		JSONObject pingResponse = new JSONObject();
		JSONObject valetStatus = new JSONObject();
		boolean allOk = true;

		valetStatus.put("valet_service", "ok");
		try {
			ValetServicePlacementDAO valetServicePlacementDAO = new ValetServicePlacementDAO(pingLogFlag);
			String response = valetServicePlacementDAO.getRow("pingRequest");
			if(response.contains("DBRequest Failed")) 
				  valetStatus.put("db_service", "Failed");
				else
				  valetStatus.put("db_service", "OK");
		} catch (Exception e) {
			valetStatus.put("DB_Service", "failed");
			allOk = false;
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"Ping failed!, Error details : "+e.getMessage());
		}
		
		pingResponse.put("status", valetStatus);
		if (allOk) {
			if(pingLogFlag) {
				LOGGER.info(EELFLoggerDelegate.applicationLogger, "Ping ok");
			}
			return ResponseEntity.ok(pingResponse.toJSONString());
		}
		LOGGER.error(EELFLoggerDelegate.errorLogger,"Ping failed!");
		return ResponseEntity.status(503).body(pingResponse.toJSONString());
		
	}

	@SuppressWarnings("unchecked")

	@RequestMapping(value = "/healthcheck", method = RequestMethod.GET)
	
	public ResponseEntity<String> healthcheck() {

		ValetServicePlacementDAO valetServicePlacementDAO = new ValetServicePlacementDAO();

		Schema schema = new Schema();

		JSONObject pingResponse = new JSONObject();

		JSONObject valetStatus = new JSONObject();

		valetStatus.put("valet_service", "ok");
		boolean allOk = true;

		try {

			JSONObject jObj = new JSONObject();

			Properties props = new Properties();

			String propFileName = "resources.properties";

			InputStream inputStream = getClass().getClassLoader().getResourceAsStream(propFileName);
			if (inputStream != null) {

				props.load(inputStream);

			} else {

				LOGGER.info(EELFLoggerDelegate.applicationLogger,"DBProxy : inputstream is not");

			}
			String timeStamp = System.currentTimeMillis() + "";
			jObj.put("id", UserUtils.htmlEscape(props.getProperty("instanceId")) );
			String dbRequest = schema.formHealthCheckRequest(timeStamp, "ping", jObj.toJSONString());

			String insertRow = valetServicePlacementDAO.insertRow(dbRequest);
			boolean status = pollForResult(jObj, "ping-" + timeStamp, Constants.WAIT_UNITL_SECONDS,

					Constants.POLL_EVERY_SECONDS);
			if (!status) allOk = false;

			valetStatus.put("DB_Service", "ok");

			valetStatus.put("valet_engine", status ? "ok" : "not ok");

		} catch (Exception e) {

			valetStatus.put("DB_Service", "not ok");
			allOk = false;
		}

		pingResponse.put("status", valetStatus);

		if (allOk) return ResponseEntity.ok(pingResponse.toJSONString());
		return ResponseEntity.status(503).body(pingResponse.toJSONString());
	}

	public static JSONObject parseToJSON(String jsonString) {
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"parseToJSON : parsing json");
		JSONParser parser = new JSONParser();
		try {
			JSONObject json = (JSONObject) parser.parse(jsonString);
			return json;
		} catch (ParseException e) {
			e.printStackTrace();
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"parseToJSON: Error details: "+ e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"parseToJSON: Error details: "+ e.getMessage());
			return null;
		}
	}

	public boolean pollForResult(JSONObject values, String requestId, int waitUntilSeconds, int pollEverySeconds) {
		LOGGER.info("pollForResult : called", requestId);
		ValetServicePlacementDAO valetServicePlacementDAO = new ValetServicePlacementDAO();
		Schema schema = new Schema();

		String result = null;
		long waitUntil = System.currentTimeMillis() + (1000 * waitUntilSeconds);
		int counter = 1;

		JSONObject response = new JSONObject();
		while (true) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"pollForResult : polling database - ", counter++);

			result = valetServicePlacementDAO.getRowFromResults(requestId);
			System.out.println("getRowFromResults called count:" + counter);
			response = result != null ? parseToJSON(result) : null;

			if (response != null && ((JSONObject) response.get("result")).get("row 0") != null) {
				LOGGER.debug(EELFLoggerDelegate.debugLogger,"pollForResult : response recieved", result);
				System.out.println("deleteRowFromResults called");
				valetServicePlacementDAO.deleteRowFromResults(requestId, schema.formMsoDeleteRequest());

			}
			if (System.currentTimeMillis() < waitUntil && response == null
					|| ((JSONObject) response.get("result")).get("row 0") == null) {
				try {
					Thread.sleep(1000 * pollEverySeconds);
				} catch (InterruptedException e) {
					e.printStackTrace();
					LOGGER.error(EELFLoggerDelegate.errorLogger,"pollForResult: Error details: "+ e.getMessage());
				}
			} else {
				break;
			}
		}
		if (System.currentTimeMillis() > waitUntil) {
			return false;
		}

		return true;
	}

	@AafRoleRequired(roleRequired = "org.onap.portal.valet.admin")
	@RequestMapping(value = "/sample", produces = "application/json")
	public String sample(HttpServletRequest request, HttpServletResponse response) {
		return okMessage("Sample page doesn't do anything.");
	}
	
	@AafRoleRequired(roleProperty = "portal.admin.role")
	@RequestMapping(value = "/sample1", produces = "application/json")
	public String sample1(HttpServletRequest request, HttpServletResponse response) {
		return okMessage("Sample page does not do anything.");
	}

	@BasicAuthRequired(authRequired = "portal")
	@RequestMapping(value = "/sample2", produces = "application/json")
	public String sample2(HttpServletRequest request, HttpServletResponse response) {
		return okMessage("Sample page doesn't do a thing.");
	}

	@PropertyBasedAuthorization("sample3")
	@RequestMapping(value = "/sample3", produces = "application/json")
	public String sample3(HttpServletRequest request, HttpServletResponse response) {
		return okMessage("Sample page does nothing.");
	}
	
	@RequestMapping(value = "/dark", produces = "application/json")
	public String darkMessage(HttpServletRequest request, HttpServletResponse response) {
		response.setStatus(400);
		return failureMessage("Valet is running dark.");
	}

	@RequestMapping(value = "/authfail", produces = "application/json")
	public String authFail(HttpServletRequest request, HttpServletResponse response) {
		response.setStatus(401);
		return failureMessage(request.getAttribute("fail"));
	}

	private String okMessage(Object message) {
		return returnMessage("ok", message);
	}

	private String failureMessage(Object message) {
		return returnMessage("failed", message);
	}

	private String returnMessage(String status, Object message) {
		Status s = null;
		if (message == null) {
			s = new Status(status, "No failure message.");
		} else {
			s = new Status(status, message.toString());
		}

		ObjectMapper mapper = new ObjectMapper();
		mapper.configure(SerializationFeature.WRAP_ROOT_VALUE, true);
		try {
			return mapper.writeValueAsString(s);
		} catch (JsonProcessingException e) {
			return "{\"status\": {\"status_code\": \"failed\", \"status_message\": \"Failed to generate failure string?!?\"} }";
		}
	}

}
