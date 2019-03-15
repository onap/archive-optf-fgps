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
import static org.mockito.Mockito.when;

import org.json.simple.JSONObject;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;

import com.valet.beans.schema.Schema;
import com.valet.dao.ValetServicePlacementDAO;

@RunWith(MockitoJUnitRunner.class)
public class ValetGroupsServiceTest {
	@Mock
	ValetServicePlacementDAO valetServicePlacementDAO;

	@Mock
	Schema schema;

	@InjectMocks
	ValetGroupsService valetGroupsService;

	int WAIT_UNITL_SECONDS = 10;
	int POLL_EVERY_SECONDS = 1;

	@Test
	public void saveGroupsRequest() {
		JSONObject request = new JSONObject();
		String operation = "test_operation";
		String requestId = "req_id";
		String expected = "test1";
		String dbRequest = "dbRequest";
		when(schema.formMsoInsertUpdateRequest(requestId, operation, operation + "-" + request.toJSONString()))
				.thenReturn(dbRequest);
		when(valetServicePlacementDAO.insertRow(dbRequest)).thenReturn(expected);
		when(valetServicePlacementDAO.getRowFromResults(requestId)).thenReturn("");
		when(valetServicePlacementDAO.deleteRowFromResults(requestId, dbRequest)).thenReturn("");

		String actual = valetGroupsService.saveGroupsRequest(request, operation, requestId);
		assertEquals(expected, actual);
	}

	@Test
	public void pollForResult_result_at_first() {
		JSONObject values = new JSONObject();
		String requestId = "req_id";
		when(valetServicePlacementDAO.getRowFromResults(requestId)).thenReturn("");
		when(valetServicePlacementDAO.deleteRowFromResults(requestId, requestId)).thenReturn("");
		valetGroupsService.pollForResult(values, requestId, WAIT_UNITL_SECONDS, POLL_EVERY_SECONDS);
	}

	@Test
	public void pollForResult_result_not_got() {
		JSONObject values = new JSONObject();
		String requestId = "req_id";
		when(valetServicePlacementDAO.getRowFromResults(requestId)).thenReturn(null);
		valetGroupsService.pollForResult(values, requestId, WAIT_UNITL_SECONDS, POLL_EVERY_SECONDS);
	}

}
*/