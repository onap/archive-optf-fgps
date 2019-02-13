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


public class ValetServicePlacementControllerTest {

	@Test
	public void testCreateVM2() throws Exception {
		try(BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream("\\testing\\createoperationandupdate\\diversitynested\\create_req_ValetHostDiversityNest_20180509e.txt")))) {
			try(BufferedReader brOutput = new BufferedReader(new InputStreamReader(new FileInputStream("\\testing\\createoperationandupdate\\diversitynested\\diversitynestedoutput.txt")))) {
				JSONObject input = (JSONObject)new JSONParser().parse(br);
				String expectedOutput = brOutput.readLine();
				JSONObject expectedOuptutJSON = (JSONObject)new JSONParser().parse(expectedOutput);
				//	Do a REST call
				ResteasyClient client = new ResteasyClientBuilder().build();
				ResteasyWebTarget target = client.target("http://localhost:8080/api/valet/placement/v1/createVM2?requestId=create-123");
				Response response = target.request().post(Entity.entity(input.toJSONString(), MediaType.APPLICATION_JSON));
				String respnseData = response.readEntity(String.class);
				response.close();
				expectedOutput = ((JSONObject)((JSONObject)expectedOuptutJSON.get("values")).get("request")).toJSONString();
				System.out.println("Expected :");
				System.out.println(expectedOutput);
				System.out.println("Actual :");
				System.out.println(respnseData);
				//	Compare the outputs
				JSONAssert.assertEquals(expectedOutput, respnseData, false);
			}
		}catch(Exception e) {
			e.printStackTrace();
			fail(e.getMessage());
		}
	}
	@Test
	public void testupdateVm1() throws Exception {
		try(BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream("\\\\testing\\\\createoperationandupdate\\\\diversitynested\\\\create_req_ValetHostDiversityNest_20180509e.txt")))) {
			try(BufferedReader brOutput = new BufferedReader(new InputStreamReader(new FileInputStream("\\\\testing\\\\createoperationandupdate\\\\diversitynested\\\\diversitynestedoutput.txt")))) {
				JSONObject input = (JSONObject)new JSONParser().parse(br);
				String expectedOutput = brOutput.readLine();
				JSONObject expectedOuptutJSON = (JSONObject)new JSONParser().parse(expectedOutput);
				//	Do a REST call
				ResteasyClient client = new ResteasyClientBuilder().build();
				ResteasyWebTarget target = client.target("http://localhost:8080/api/valet/placement/v1/updateVm1?requestId=update-123");
				Response response = target.request().put(Entity.entity(input.toJSONString(), MediaType.APPLICATION_JSON));
				String respnseData = response.readEntity(String.class);
				response.close();
				expectedOutput = ((JSONObject)((JSONObject)expectedOuptutJSON.get("values")).get("request")).toJSONString();
				System.out.println("Expected :");
				System.out.println(expectedOutput);
				System.out.println("Actual :");
				System.out.println(respnseData);
				//	Compare the outputs
				JSONAssert.assertEquals(expectedOutput, respnseData, false);
			}
		}catch(Exception e) {
			e.printStackTrace();
			fail(e.getMessage());
		}
	}
	@Test
	public void testdeleteVm1() throws Exception {
		try(BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream("\\testing\\Deleteoperation\\deleteinput.txt")))) {
			try(BufferedReader brOutput = new BufferedReader(new InputStreamReader(new FileInputStream("\\\\testing\\\\Deleteoperation\\\\deleteoutput.txt")))) {
				JSONObject input = (JSONObject)new JSONParser().parse(br);
				String expectedOutput = brOutput.readLine();
				JSONObject expectedOuptutJSON = (JSONObject)new JSONParser().parse(expectedOutput);
				//	Do a REST call
				ResteasyClient client = new ResteasyClientBuilder().build();
				ResteasyWebTarget target = client.target("http://localhost:8080/api/valet/placement/v1/deleteVm1?requestId=delete-123");
				Response response = target.request().build("DELETE", Entity.entity(input.toJSONString(), MediaType.APPLICATION_JSON)).invoke();
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
				JSONAssert.assertEquals(expectedOutput, respnseData, false);
			}
		}catch(Exception e) {
			e.printStackTrace();
			fail(e.getMessage());
		}
	}
	@Test
	public void testconfirm1() throws Exception {
		try(BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream("\\testing\\Confirm\\confriminput.txt")))) {
			try(BufferedReader brOutput = new BufferedReader(new InputStreamReader(new FileInputStream("\\testing\\Confirm\\confrimoutput.txt")))) {
				JSONObject input = (JSONObject)new JSONParser().parse(br);
				String expectedOutput = brOutput.readLine();
				JSONObject expectedOuptutJSON = (JSONObject)new JSONParser().parse(expectedOutput);
				//	Do a REST call
				ResteasyClient client = new ResteasyClientBuilder().build();
				ResteasyWebTarget target = client.target("http://localhost:8080/api/valet/placement/v1/confirm-123/confirm1");
				Response response = target.request().put(Entity.entity(input.toJSONString(), MediaType.APPLICATION_JSON));
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
				JSONAssert.assertEquals(expectedOutput, respnseData, false);
			}
		}catch(Exception e) {
			e.printStackTrace();
			fail(e.getMessage());
		}
	}
	@Test
	public void testrollback1() throws Exception {
		try(BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream("\\testing\\Rollback\\rollbackinput.txt")))) {
			try(BufferedReader brOutput = new BufferedReader(new InputStreamReader(new FileInputStream("\\testing\\Rollback\\rollbackoutput.txt")))) {
				JSONObject input = (JSONObject)new JSONParser().parse(br);
				String expectedOutput = brOutput.readLine();
				JSONObject expectedOuptutJSON = (JSONObject)new JSONParser().parse(expectedOutput);
				//	Do a REST call
				ResteasyClient client = new ResteasyClientBuilder().build();
				ResteasyWebTarget target = client.target("http://localhost:8080/api/valet/placement/v1/rollback-123/rollback1");
				Response response = target.request().put(Entity.entity(input.toJSONString(), MediaType.APPLICATION_JSON));
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
				JSONAssert.assertEquals(expectedOutput, respnseData, false);
			}
		}catch(Exception e) {
			e.printStackTrace();
			fail(e.getMessage());
		}
	}
	@Test
	public void testBodyVM2() throws Exception {
		try(BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream("")))) {
			JSONObject input = (JSONObject)new JSONParser().parse(br);
			String expectedOutput = "[Expected output]";
			//	Do a REST call
			ResteasyClient client = new ResteasyClientBuilder().build();
			ResteasyWebTarget target = client.target("http://localhost:8080/api/valet/placement/v1/createVM2?requestId=12345");
			Response response = target.request().post(Entity.entity(input.toJSONString(), MediaType.APPLICATION_JSON));
			String respnseData = response.readEntity(String.class);
			response.close();
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