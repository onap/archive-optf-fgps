/* 
 * ============LICENSE_START========================================== 
 * ONAP - F-GPS API 
 * =================================================================== 
 * Copyright © 2019 AT&T Intellectual Property. All rights reserved. 
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
package org.onap.fgps.api.beans.schema;

import org.json.simple.JSONObject;
import org.onap.fgps.api.utils.Constants;
import org.springframework.stereotype.Component;

import com.fasterxml.uuid.Generators;

@Component
public class Schema {
	@SuppressWarnings("unchecked")
	public static JSONObject getCommonTableSchema() {
		JSONObject jsonRequest = new JSONObject();
		JSONObject properties = new JSONObject();
		JSONObject compression = new JSONObject();
		JSONObject compaction = new JSONObject();
		JSONObject consistencyInfo = new JSONObject();

		compression.put("sstable_compression", "DeflateCompressor");
		compression.put("chunk_length_kb", 64);

		compaction.put("class", "SizeTieredCompactionStrategy");
		compaction.put("min_threshold", 6);

		properties.put("compression", compression);
		properties.put("compaction", compaction);

		consistencyInfo.put("type", "eventual");

		jsonRequest.put("properties", properties);
		jsonRequest.put("consistencyInfo", consistencyInfo);
		return jsonRequest;
	}

	@SuppressWarnings("unchecked")
	public static String getRequestTableSchema() {
		JSONObject fields = new JSONObject();

		fields.put("request_id", "varchar");
		fields.put("timestamp", "varchar");
		fields.put("request", "varchar");
		fields.put("PRIMARY KEY", "(request_id)");

		JSONObject jsonRequest = getCommonTableSchema();
		jsonRequest.put("fields", fields);
		return jsonRequest.toJSONString();
	}

	@SuppressWarnings("unchecked")
	public static String getResultsTableSchema() {
		JSONObject fields = new JSONObject();

		fields.put("request_id", "varchar");
		fields.put("status", "varchar");
		fields.put("timestamp", "varchar");
		fields.put("result", "varchar");
		fields.put("PRIMARY KEY", "(request_id)");

		JSONObject jsonRequest = getCommonTableSchema();
		jsonRequest.put("fields", fields);
		return jsonRequest.toJSONString();
	}

	@SuppressWarnings("unchecked")
	public static String getGroupsRulesTableSchema() {
		JSONObject fields = new JSONObject();

		fields.put("id", "varchar");
		fields.put("app_scope", "varchar");
		fields.put("type", "varchar");
		fields.put("level", "varchar");
		fields.put("members", "varchar");
		fields.put("description", "varchar");
		fields.put("groups", "varchar");
		fields.put("status", "varchar");
		fields.put("timestamp", "varchar");
		fields.put("PRIMARY KEY", "(id)");

		JSONObject jsonRequest = getCommonTableSchema();
		jsonRequest.put("fields", fields);
		return jsonRequest.toJSONString();

	}

	@SuppressWarnings("unchecked")
	public static String getStacksTableSchema() {
		JSONObject fields = new JSONObject();

		fields.put("id", "varchar");
		fields.put("last_status", "varchar");
		fields.put("datacenter", "varchar");
		fields.put("stack_name", "varchar");
		fields.put("uuid", "varchar");
		fields.put("tenant_id", "varchar");
		fields.put("metadata", "varchar");
		fields.put("servers", "varchar");
		fields.put("prior_servers", "varchar");
		fields.put("state", "varchar");
		fields.put("prior_State", "varchar");
		fields.put("timestamp", "varchar");
		fields.put("PRIMARY KEY", "(id)");

		JSONObject jsonRequest = getCommonTableSchema();
		jsonRequest.put("fields", fields);
		return jsonRequest.toJSONString();
	}

	@SuppressWarnings("unchecked")
	public static String getStacksIdMapTableSchema() {
		JSONObject fields = new JSONObject();

		fields.put("request_id", "varchar");
		fields.put("stack_id", "varchar");
		fields.put("timestamp", "varchar");
		fields.put("PRIMARY KEY", "(request_id)");
		JSONObject jsonRequest = getCommonTableSchema();
		jsonRequest.put("fields", fields);
		return jsonRequest.toJSONString();
	}

	@SuppressWarnings("unchecked")
	public static String getResourcesTableSchema() {
		JSONObject fields = new JSONObject();

		fields.put("id", "varchar");
		fields.put("url", "varchar");
		fields.put("resource", "varchar");
		fields.put("timestamp", "varchar");
		fields.put("PRIMARY KEY", "(id)");
		fields.put("requests", "varchar");

		JSONObject jsonRequest = getCommonTableSchema();
		jsonRequest.put("fields", fields);
		return jsonRequest.toJSONString();
	}
	@SuppressWarnings("unchecked")
	public static String getRegionsTableSchema() {
		JSONObject fields = new JSONObject();

		fields.put("region_id ", "varchar");
		fields.put("PRIMARY KEY", "(region_id)");
		fields.put("timestamp", "varchar");
		fields.put("last_updated ", "varchar");
		fields.put("keystone_url", "varchar");
		fields.put("locked_by", "varchar");
		fields.put("locked_time ", "varchar");
		//fields.put("locked_time ", "varchar");
		fields.put("expire_time", "varchar");

		JSONObject jsonRequest = getCommonTableSchema();
		jsonRequest.put("fields", fields);
		return jsonRequest.toJSONString();
	}

	@SuppressWarnings("unchecked")
	public static String getGroupsTableSchema() {
		JSONObject fields = new JSONObject();

		fields.put("id ", "varchar");
		fields.put("PRIMARY KEY", "id");
		fields.put("uuid", "varchar");
		fields.put("type ", "varchar");
		fields.put("level", "varchar");
		fields.put("factory", "varchar");
		fields.put("rule_id ", "varchar");
		fields.put("metadata ", "varchar");
		fields.put("server_list", "varchar");
		fields.put("member_hosts", "varchar");
		fields.put("status", "varchar");
		

		JSONObject jsonRequest = getCommonTableSchema();
		jsonRequest.put("fields", fields);
		return jsonRequest.toJSONString();
	}
	@SuppressWarnings("unchecked")
	public String formMsoInsertUpdateRequest(String requestId, String operation, String request) {
		JSONObject jsonRequest = new JSONObject();
		JSONObject values = new JSONObject();
		JSONObject consistencyInfo = new JSONObject();
		String request_id = requestId == null ? Generators.timeBasedGenerator().generate().toString()
				: operation + '-' + requestId;

		values.put(Constants.HEAT_REQUEST_REQUEST_ID, request_id);
		values.put(Constants.HEAT_REQUEST_TIMESTAMP, System.currentTimeMillis());
		values.put(Constants.HEAT_REQUEST_REQUEST, request);
		consistencyInfo.put("type", "eventual");

		jsonRequest.put("values", values);
		jsonRequest.put("consistencyInfo", consistencyInfo);

		return jsonRequest.toJSONString();
	}
	@SuppressWarnings("unchecked")
	public String formHealthCheckRequest(String requestId, String operation, String request) {
		JSONObject jsonRequest = new JSONObject();
		JSONObject values = new JSONObject();
		JSONObject consistencyInfo = new JSONObject();
		String request_id = requestId == null ? Generators.timeBasedGenerator().generate().toString()
				: operation + '-' + requestId;

		values.put(Constants.HEAT_REQUEST_REQUEST_ID, request_id);
		values.put(Constants.HEAT_REQUEST_TIMESTAMP, -1);
		values.put(Constants.HEAT_REQUEST_REQUEST, request);
		consistencyInfo.put("type", "eventual");

		jsonRequest.put("values", values);
		jsonRequest.put("consistencyInfo", consistencyInfo);

		return jsonRequest.toJSONString();
	}


	@SuppressWarnings("unchecked")
	public String formMsoDeleteRequest() {
		JSONObject jsonRequest = new JSONObject();
		JSONObject consistencyInfo = new JSONObject();

		consistencyInfo.put("type", "eventual");
		jsonRequest.put("consistencyInfo", consistencyInfo);

		return jsonRequest.toJSONString();
	}
}

