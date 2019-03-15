/* 
 * ============LICENSE_START========================================== 
 * ONAP - F-GPS API 
 * =================================================================== 
 * Copyright - 2019 ATT Intellectual Property. All rights reserved. 
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
package org.onap.fgps.controller;
/*package com.valet.controller;

import static org.assertj.core.api.Assertions.fail;
import static org.junit.Assert.assertEquals;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStreamReader;

import javax.ws.rs.client.Entity;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import org.jboss.resteasy.client.jaxrs.ResteasyClient;
import org.jboss.resteasy.client.jaxrs.ResteasyClientBuilder;
import org.jboss.resteasy.client.jaxrs.ResteasyWebTarget;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.junit.Test;
import org.skyscreamer.jsonassert.JSONAssert;


public class ValetGroupsControllerTest {


	@Test
	public void testPotal1() throws Exception {
		String expectedOutput = "{}";
		//	Do a REST call
		ResteasyClient client = new ResteasyClientBuilder().build();
		ResteasyWebTarget target = client.target("http://localhost:8080/api/valet/groups/v1/portal?requestId=12345");
		Response response = target.request().get();
		String respnseData = response.readEntity(String.class);
		response.close();
		JSONObject responseDataJSON = (JSONObject)new JSONParser().parse(respnseData);
		respnseData = ((JSONObject)responseDataJSON.get("values")).get("request").toString();
		System.out.println("Expected :");
		System.out.println(expectedOutput);
		System.out.println("Actual :");
		System.out.println(respnseData);
		//	Compare the outputs
		assertEquals(expectedOutput, respnseData);
	}	
	@Test
	public void testPortal2() throws Exception {
		try(BufferedReader brOutput = new BufferedReader(new InputStreamReader(new FileInputStream("\\testing\\portal\\Advancedsearch\\advancedsearchoutput.txt")))) {
			String expectedOutput = brOutput.readLine();
			JSONObject expectedOuptutJSON = (JSONObject)new JSONParser().parse(expectedOutput);
			//	Do a REST call
			ResteasyClient client = new ResteasyClientBuilder().build();
			ResteasyWebTarget target = client.target("http://localhost:8080/api/valet/groups/v1/portal?requestId=12345&name=VALET_HOST_DIVERSITY_RULE&datacenter_id=mtn6");
			Response response = target.request().get();
			String respnseData = response.readEntity(String.class);
			response.close();
			expectedOutput = ((JSONObject)((JSONObject)expectedOuptutJSON.get("values")).get("request")).toJSONString();
			JSONObject responseDataJSON = (JSONObject)new JSONParser().parse(respnseData);
			respnseData = ((JSONObject)responseDataJSON.get("values")).get("request").toString();
			System.out.println("Expected :");
			System.out.println(expectedOutput);
			System.out.println("Actual :");
			System.out.println(respnseData);
			//	Compare the outputs
			assertEquals(expectedOutput, respnseData);
		}catch(Exception e) {
			e.printStackTrace();
			fail(e.getMessage());
		}
	}	
}*/