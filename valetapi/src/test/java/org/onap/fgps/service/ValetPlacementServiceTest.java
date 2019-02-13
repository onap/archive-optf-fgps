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
package org.onap.fgps.service;
/*package com.valet.service;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;
import static org.mockito.Matchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.util.LinkedHashMap;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;

import com.valet.beans.schema.Schema;
import com.valet.dao.ValetServicePlacementDAO;
import com.valet.utils.Constants;

@RunWith(MockitoJUnitRunner.class)
public class ValetPlacementServiceTest {

	@Mock
	ValetServicePlacementDAO valetServicePlacementDAO;
	@Mock
	Schema schema;

	@InjectMocks
	ValetPlacementService valetPlacementService;

	@Test
	public void getParam_params_get_key_notnull() {
		String key = "key";
		JSONObject parameters = new JSONObject();
		Object expected = new String("test1");
		parameters.put("key", expected);
		JSONObject envPrams = new JSONObject();
		LinkedHashMap requestParameters = new LinkedHashMap<>();
		Object actual = valetPlacementService.getParam(key, parameters, envPrams, requestParameters);
		assertEquals(expected, actual);
	}

	@Test
	public void getParam_env_get_key_null() {
		String key = "key";
		JSONObject parameters = new JSONObject();
		Object expected = new String("test2");
		parameters.put("key1", "val1");
		JSONObject envPrams = new JSONObject();
		envPrams.put("diffKey", "diffVal");
		LinkedHashMap requestParameters = new LinkedHashMap<>();
		requestParameters.put("key", expected);
		Object actual = valetPlacementService.getParam(key, parameters, envPrams, requestParameters);
		assertEquals(expected, actual);
	}

	@Test
	public void getParam_env_get_key_notnull_length_0() {
		String key = "key";
		JSONObject parameters = new JSONObject();
		Object expected = new String("test3");
		parameters.put("key1", "val1");
		JSONObject envPrams = new JSONObject();
		envPrams.put("", "");
		LinkedHashMap requestParameters = new LinkedHashMap<>();
		requestParameters.put("key", expected);
		Object actual = valetPlacementService.getParam(key, parameters, envPrams, requestParameters);
		assertEquals(expected, actual);
	}

	@Test
	public void getParam_env_get_key_notnull_length_not_0() {
		String key = "key";
		JSONObject parameters = new JSONObject();
		Object expected = new String("test4");
		parameters.put("key1", "val1");
		JSONObject envPrams = new JSONObject();
		envPrams.put("key", expected);
		LinkedHashMap requestParameters = new LinkedHashMap<>();
		Object actual = valetPlacementService.getParam(key, parameters, envPrams, requestParameters);
		assertEquals(expected, actual);
	}

	@Test
	public void getAttr() {
		JSONArray key = new JSONArray();
		key.add("jsonArray");
		JSONObject resources = new JSONObject();
		Object expected = new String("test5");
		resources.put(key, expected);
		Object actual = valetPlacementService.getAttr(key, resources);
		assertEquals(expected, actual);
	}

	@Test
	public void processTemplate_env_notnull() {
		ValetPlacementService mockedValetPlacementService = mock(ValetPlacementService.class);
		JSONObject template = new JSONObject();
		JSONObject resources = new JSONObject();
		JSONObject resourceObject = new JSONObject();
		JSONObject properties = new JSONObject();
		resourceObject.put(Constants.HEAT_REQUEST_PROPERTIES, properties);
		resources.put("resourceObject", resourceObject);

		template.put(Constants.VALET_REQUEST_RESOURCES, resources);
		LinkedHashMap files = new LinkedHashMap<>();
		JSONObject environment = new JSONObject();
		JSONObject parameters = new JSONObject();
		environment.put("parameters", parameters);
		JSONObject parentProperties = new JSONObject();
		LinkedHashMap requestParameters = new LinkedHashMap<>();
		JSONObject expected = new JSONObject();
		when(mockedValetPlacementService.parseResourceObject(template, null, resourceObject, parameters, files,
				parentProperties, requestParameters)).thenReturn(expected);
		when(mockedValetPlacementService.processTemplate(template, files, environment, parentProperties,
				requestParameters)).thenCallRealMethod();

		JSONObject actual = mockedValetPlacementService.processTemplate(template, files, environment, parentProperties,
				requestParameters);
		assertEquals(expected, actual.get("resourceObject"));
	}

	@Test
	public void processTemplate_env_null() {
		ValetPlacementService mockedValetPlacementService = mock(ValetPlacementService.class);
		JSONObject template = new JSONObject();
		JSONObject resources = new JSONObject();
		JSONObject resourceObject = new JSONObject();
		JSONObject properties = new JSONObject();
		resourceObject.put(Constants.HEAT_REQUEST_PROPERTIES, properties);
		resources.put("resourceObject", resourceObject);

		template.put(Constants.VALET_REQUEST_RESOURCES, resources);
		JSONObject parameters = new JSONObject();
		template.put("parameters", parameters);
		LinkedHashMap files = new LinkedHashMap<>();
		JSONObject environment = null;
		JSONObject parentProperties = new JSONObject();
		LinkedHashMap requestParameters = new LinkedHashMap<>();
		JSONObject expected = new JSONObject();
		when(mockedValetPlacementService.parseResourceObject(template, null, resourceObject, parameters, files,
				parentProperties, requestParameters)).thenReturn(expected);
		when(mockedValetPlacementService.processTemplate(template, files, environment, parentProperties,
				requestParameters)).thenCallRealMethod();

		JSONObject actual = mockedValetPlacementService.processTemplate(template, files, environment, parentProperties,
				requestParameters);
		assertEquals(expected, actual.get("resourceObject"));
	}

	@Test
	public void parseLogicFinal() {
		assertNull(valetPlacementService.parseLogicFinal());
	}

	@Test
	public void processMSORequest1_requestParameters_notnull() {
		ValetPlacementService mockService = mock(ValetPlacementService.class);
		JSONObject request = new JSONObject();
		LinkedHashMap heat_request = new LinkedHashMap<>();
		JSONObject template = new JSONObject();
		template.put("templatekey", "templatevalue");
		heat_request.put(Constants.HEAT_REQUEST_TEMPLATE, template);
		LinkedHashMap files = new LinkedHashMap<>();
		heat_request.put(Constants.HEAT_REQUEST_FILES, files);
		JSONObject environment = new JSONObject();
		heat_request.put(Constants.HEAT_REQUEST_ENVIRONMENT, environment);
		LinkedHashMap requestParameters = new LinkedHashMap<>();
		heat_request.put("parameters", requestParameters);
		when(mockService.processMSORequest1(request)).thenCallRealMethod();
		when(mockService.convertToJson(template.toString())).thenCallRealMethod();
		when(mockService.convertToJson(environment.toString())).thenCallRealMethod();
		JSONObject expected = new JSONObject();
		expected.put("key", "value");
		when(mockService.processTemplate(template, files, environment, null, requestParameters)).thenReturn(expected);

		request.put(Constants.HEAT_REQUEST, heat_request);

		String actual = mockService.processMSORequest1(request);
		assertEquals(expected.toJSONString(), actual);
	}

	@Test
	public void processMSORequest1_requestParameters_null() {
		ValetPlacementService mockService = mock(ValetPlacementService.class);
		JSONObject request = new JSONObject();
		LinkedHashMap heat_request = new LinkedHashMap<>();
		JSONObject template = new JSONObject();
		template.put("templatekey", "templatevalue");
		heat_request.put(Constants.HEAT_REQUEST_TEMPLATE, template);
		LinkedHashMap files = new LinkedHashMap<>();
		heat_request.put(Constants.HEAT_REQUEST_FILES, files);
		JSONObject environment = new JSONObject();
		heat_request.put(Constants.HEAT_REQUEST_ENVIRONMENT, environment);
		LinkedHashMap requestParameters = null;
		heat_request.put("parameters", requestParameters);
		when(mockService.processMSORequest1(request)).thenCallRealMethod();
		when(mockService.convertToJson(template.toString())).thenCallRealMethod();
		when(mockService.convertToJson(environment.toString())).thenCallRealMethod();
		JSONObject expected = new JSONObject();
		expected.put("key", "value");
		org.mockito.Mockito.when(mockService.processTemplate(any(), any(), any(), any(), any())).thenReturn(expected);

		request.put(Constants.HEAT_REQUEST, heat_request);

		String actual = mockService.processMSORequest1(request);
		assertEquals(expected.toJSONString(), actual);
	}

	@Test
	public void processMSORequest1_exception() {
		ValetPlacementService mockService = mock(ValetPlacementService.class);
		JSONObject request = new JSONObject();
		LinkedHashMap heat_request = new LinkedHashMap<>();
		JSONObject template = new JSONObject();
		template.put("templatekey", "templatevalue");
		heat_request.put(Constants.HEAT_REQUEST_TEMPLATE, template);
		LinkedHashMap files = new LinkedHashMap<>();
		heat_request.put(Constants.HEAT_REQUEST_FILES, files);
		JSONObject environment = new JSONObject();
		heat_request.put(Constants.HEAT_REQUEST_ENVIRONMENT, environment);
		LinkedHashMap requestParameters = null;
		heat_request.put("parameters", requestParameters);
		when(mockService.processMSORequest1(request)).thenCallRealMethod();
		when(mockService.convertToJson(template.toString())).thenCallRealMethod();
		when(mockService.convertToJson(environment.toString())).thenCallRealMethod();
		JSONObject expected = new JSONObject();
		expected.put("key", "value");
		org.mockito.Mockito.when(mockService.processTemplate(any(), any(), any(), any(), any()))
				.thenThrow(Exception.class);

		request.put(Constants.HEAT_REQUEST, heat_request);

		String actual = mockService.processMSORequest1(request);
		assertNull(actual);
	}

	@Test
	public void convertToJson() {
		String data = "{\"key\":\"value\"}";
		JSONObject actual = valetPlacementService.convertToJson(data);
		assertEquals("value", actual.get("key"));
	}

	@Test
	public void convertToJson_exception() {
		String data = "{\"key\"::\"value\"}";
		JSONObject actual = valetPlacementService.convertToJson(data);
		assertNull(actual);
	}

	@Test
	public void processDeleteRequest() {
		String requestId = "req_id";
		JSONObject request = new JSONObject();
		String dbRequest = "dbRequest";
		when(schema.formMsoInsertUpdateRequest(requestId, "delete", request.toJSONString())).thenReturn(dbRequest);
		when(valetServicePlacementDAO.insertRow(dbRequest)).thenReturn(requestId);
		String actual = valetPlacementService.processDeleteRequest(request, requestId);
		assertEquals(requestId, actual);
	}

	@Test
	public void saveRequest() {
		String requestId = "req_id";
		JSONObject request = new JSONObject();
		String dbRequest = "dbRequest";
		String operation = "operation";
		when(schema.formMsoInsertUpdateRequest(requestId, operation, request.toJSONString())).thenReturn(dbRequest);
		when(valetServicePlacementDAO.insertRow(dbRequest)).thenReturn(requestId);
		when(valetServicePlacementDAO.getRowFromResults(requestId)).thenReturn("");
		when(valetServicePlacementDAO.deleteRowFromResults(requestId, operation)).thenReturn("");
		String actual = valetPlacementService.saveRequest(request, operation, requestId);
		assertEquals(requestId, actual);
	}

	@Test
	public void pollForResult_result_at_first() {
		JSONObject values = new JSONObject();
		String requestId = "req_id";
		when(valetServicePlacementDAO.getRowFromResults(requestId)).thenReturn("");
		when(valetServicePlacementDAO.deleteRowFromResults(requestId, requestId)).thenReturn("");
		valetPlacementService.pollForResult(values, requestId, 10, 1);
	}

	@Test
	public void pollForResult_result_not_got() {
		JSONObject values = new JSONObject();
		String requestId = "req_id";
		when(valetServicePlacementDAO.getRowFromResults(requestId)).thenReturn(null);
		valetPlacementService.pollForResult(values, requestId, 5, 1);
	}
}
*/