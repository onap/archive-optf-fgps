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
package org.onap.fgps.api.interceptor;

import java.util.Properties;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.web.servlet.ModelAndView;


public class VersioningInterceptor implements HandlerInterceptor {
	
	private static final EELFLoggerDelegate LOGGER = EELFLoggerDelegate.getLogger(VersioningInterceptor.class);
	private Properties versionProperties = null;
	
	@Override
	public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
		if (versionProperties==null) {
			versionProperties = new Properties();
			try {
				Resource fileResource = new ClassPathResource("version.properties");
				versionProperties.load(fileResource.getInputStream());
			} catch (NullPointerException e) {
				e.printStackTrace();
				LOGGER.error(EELFLoggerDelegate.applicationLogger," preHandle : Error details : "+ e.getMessage());
				LOGGER.error(EELFLoggerDelegate.errorLogger," preHandle : Error details : "+ e.getMessage());
			}
		}
		
		response.addHeader("X-MinorVersion", versionProperties.getProperty("version.minor"));
		response.addHeader("X-PatchVersion", versionProperties.getProperty("version.patch"));
		response.addHeader("X-LatestVersion", versionProperties.getProperty("version.full"));

		return true;
	}

	@Override
	public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) throws Exception {
		// noop
	}

	@Override
	public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
		// noop
	}

}
