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
package org.onap.fgps.api.utils;

public class Constants {
	public static final String HEAT_REQUEST = "heat_request";
	public static final String HEAT_REQUEST_TEMPLATE = "template";
	public static final String VALET_ENGINE_KEY = "stack";
	public static final String VALET_REQUEST_RESOURCES = "resources";
	public static final String HEAT_REQUEST_FILES = "files";
	public static final String HEAT_RESOURCE_PROPERTIES = "properties";
	public static final String HEAT_REQUEST_RESOURCES_DEF = "resource_def";
	public static final String HEAT_REQUEST_RESOURCES_TYPE = "type";
	public static final String HEAT_REQUEST_ENVIRONMENT = "environment";
	public static final String HEAT_REQUEST_PARAMETERS = "parameters";
	public static final String HEAT_REQUEST_PROPERTIES_COUNT = "count";
	public static final String HEAT_REQUEST_DATACENTER = "datacenter";
	public static final String HEAT_REQUEST_REGION_ID = "region_id";
	public static final String HEAT_REQUEST_KEYSTONE_ID = "keystone_url";
	public static final String HEAT_REQUEST_KEYSTONE_NETWORKS = "networks";
	public static final String HEAT_REQUEST_AVAILABILITY_ZONE = "availability_zone";
	public static final String HEAT_REQUEST_SCHEDULER_HINTS = "scheduler_hints";
	public static final String HEAT_REQUEST_METADATA = "metadata";
	public static final String HEAT_REQUEST_VALET_HOST_ASSIGNMENT = "$VALET_HOST_ASSIGNMENT";
	public static final String HEAT_REQUEST_AZ = "$AZ";
	public static final String HEAT_REQUEST_PROPERTIES = "properties";
	public static final String HEAT_REQUEST_NAMES = "name";
	public static final String HEAT_REQUEST_IMAGE = "image";
	public static final String HEAT_REQUEST_FLAVOR = "flavor";

	
	// MSO Request constants
	public static final String HEAT_REQUEST_REQUEST_ID = "request_id";
	public static final String HEAT_REQUEST_TIMESTAMP = "timestamp";
	public static final String HEAT_REQUEST_OPERATION = "operation";
	public static final String HEAT_REQUEST_STATUS = "status";

	// tables names
	public static final String HEAT_REQUEST_REQUEST = "request";

	// tables names
	public static final String SERVICE_PLACEMENTS_REQUEST_TABLE = "requests";
	public static final String SERVICE_PLACEMENTS_RESULTS_TABLE = "results";
	public static final String TABLE_RESULT = "results";
	public static final String TABLE_GROUP_RULES = "group_rules";
	public static final String TABLE_STACKS = "stacks";
	public static final String TABLE_STACKS_ID_MAP = "stack_id_map";
	public static final String TABLE_RESOURCES = "resources";
	public static final String TABLE_REGIONS = "regions";
	public static final String TABLE_Groups = "groups";

	public static final String GROUPS_TABLE = "groups";
	public static final String GROUP_PLACEMENTS_TABLE = "group_placements";

	// parsing constants
	public static final String OS_NOVA_SERVER_ROOT = "OS::Nova::Server";
	public static final String OS_NOVA_SERVERGROUP_ROOT = "OS::Nova::ServerGroup";
	public static final String OS_HEAT_RESOURCEGROUP = "OS::Heat::ResourceGroup";

	public static final int WAIT_UNITL_SECONDS = 300;
	
	public static final int POLL_EVERY_SECONDS = 5;
	

}
