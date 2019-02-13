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
package org.onap.fgps.api.helpers;

import org.json.simple.JSONObject;

public class Helper {
	@SuppressWarnings("unchecked")
	public static JSONObject formatDeleteRequest(JSONObject request) {
		JSONObject req = new JSONObject(), datacenter = new JSONObject() ;
		datacenter.put("id", request.get("region_id"));
		//datacenter.put("url", request.get("keystone_url"));
		req.put("datacenter", datacenter);
		if (request.get("stack_name") != null){
			req.put("stack_name", request.get("stack_name"));
		}else  {
			req.put("stack_name", request.get("vf_module_name"));
		}
		if(request.get("tenant_id") != null) { req.put("tenant_id", request.get("tenant_id"));}
		return req;
		
	}
}