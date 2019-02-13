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
package org.onap.fgps.api.config;

import org.onap.fgps.api.interceptor.AuthorizationInterceptor;
import org.onap.fgps.api.interceptor.DarknessInterceptor;
import org.onap.fgps.api.interceptor.VersioningInterceptor;
import org.onap.fgps.api.proxy.AAFProxy;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurerAdapter;

@Configuration
public class SpringServletConfig extends WebMvcConfigurerAdapter  {
	private final boolean valetDark;
	private final String aafUrl;
	private final boolean aafAuthFlag;
	private final boolean basicAuthFlag;

	@Autowired
	public SpringServletConfig(@Value("${valet.dark:false}") boolean valetDark, @Value("${aaf.url.base:}") String aafUrl, @Value("${authentication.aaf:true}") boolean aafAuthFlag, @Value("${authentication.basic:true}") boolean basicAuthFlag) {
		this.valetDark = valetDark;
		this.aafUrl = aafUrl;
		this.aafAuthFlag = aafAuthFlag;
		this.basicAuthFlag = basicAuthFlag;
	}

	@Override
	public void addInterceptors(InterceptorRegistry registry) {
		if (valetDark) registry.addInterceptor(new DarknessInterceptor());
		if (aafUrl!=null && aafUrl.length()>0) registry.addInterceptor(new AuthorizationInterceptor(new AAFProxy(aafUrl), aafAuthFlag, basicAuthFlag));
		registry.addInterceptor(new VersioningInterceptor());
	}
}