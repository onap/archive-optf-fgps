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

import javax.servlet.http.HttpServletRequest;

import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.springframework.web.util.HtmlUtils;

@SuppressWarnings("rawtypes")
public class UserUtils {

	private static final EELFLoggerDelegate logger = EELFLoggerDelegate.getLogger(UserUtils.class);

	public static final String KEY_USER_ROLES_CACHE = "userRoles";

	/**
	 * Gets the full URL of the request by joining the request and any query string.
	 * 
	 * @param request
	 * @return Full URL of the request including query parameters
	 */
	public static String getFullURL(HttpServletRequest request) {
		if (request != null) {
			StringBuffer requestURL = request.getRequestURL();
			String queryString = request.getQueryString();

			if (queryString == null) {
				return requestURL.toString();
			} else {
				return requestURL.append('?').append(queryString).toString();
			}
		}
		return "";
	}
	
	public static String htmlEscape(String input) {
		if (input==null) return null;
		return HtmlUtils.htmlEscape(input);
	}
}
