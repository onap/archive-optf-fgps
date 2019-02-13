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

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.tomcat.util.codec.binary.Base64;
import org.onap.fgps.api.annotation.AafRoleRequired;
import org.onap.fgps.api.annotation.BasicAuthRequired;
import org.onap.fgps.api.annotation.PropertyBasedAuthorization;
import org.onap.fgps.api.exception.MissingRoleException;
import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.onap.fgps.api.proxy.AAFProxy;
import org.onap.fgps.api.utils.CipherUtil;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.web.servlet.ModelAndView;

public class AuthorizationInterceptor implements HandlerInterceptor {
	private static final EELFLoggerDelegate LOGGER = EELFLoggerDelegate.getLogger(AuthorizationInterceptor.class);
	private boolean aafAuthFlag;
	private boolean basicAuthFlag;
	private AAFProxy aafProxy;
	private Map<String, String> credentials = new HashMap<String, String>();
	private Map<String, String> roles = new HashMap<String, String>();
	private Map<String, String> aafTags = new HashMap<String, String>();
	private Map<String, String> basicTags = new HashMap<String, String>();

	public AuthorizationInterceptor(AAFProxy aafProxy, boolean aafAuthFlag, boolean basicAuthFlag) {
		this.aafProxy = aafProxy;
		this.aafAuthFlag = aafAuthFlag;
		this.basicAuthFlag = basicAuthFlag;
		Properties authProperties = new Properties();
		try {
			Resource fileResource = new ClassPathResource("auth.properties");
			authProperties.load(fileResource.getInputStream());
		} catch (IOException e) {
			LOGGER.error(EELFLoggerDelegate.errorLogger,"Couldn't load auth.properties!");
		}
		
		for (Object o : authProperties.keySet()) {
			String key = (String)o;
			if (key.endsWith(".name")) {
				String propname = key.substring(0, key.length()-5);
				String user = authProperties.getProperty(key);
				String encpass = authProperties.getProperty(propname + ".pass");
				String pass = CipherUtil.decryptPKC(encpass);
				String plainCredentials = user + ":" + pass;
		        String base64Credentials = new String(Base64.encodeBase64(plainCredentials.getBytes()));
		        if (key.equals("valet.aaf.name")) {
			        aafProxy.setCredentials(base64Credentials);
		        } else {
		        	credentials.put(user, base64Credentials); 
		        }
			} else if (key.endsWith(".role")) {
				roles.put(key, authProperties.getProperty(key));
			} else if (key.endsWith(".aaf")) {
				aafTags.put(key, authProperties.getProperty(key));
			} else if (key.endsWith(".basic")) {
				basicTags.put(key, authProperties.getProperty(key));
			}
		}
	}
	
	private boolean aafOk(HttpServletRequest request, Object handler) throws Exception {
		String roleRequired = null;
		try {
			AafRoleRequired aafAnnotation = null;
			HandlerMethod hm = (HandlerMethod)handler;
			aafAnnotation = hm.getMethodAnnotation(AafRoleRequired.class);
			roleRequired = getRole(aafAnnotation);
		} catch (RuntimeException e) {
			try {
				PropertyBasedAuthorization pba = null;
				HandlerMethod hm = (HandlerMethod)handler;
				pba = hm.getMethodAnnotation(PropertyBasedAuthorization.class);
				roleRequired = aafTags.get(pba.value() + ".aaf");
			} catch (RuntimeException e2) {
				// noop
			}
		}
		
		if (roleRequired!=null && aafAuthFlag) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"AAF required: " + roleRequired);
			
			if (!aafProxy.userAuthenticated(request)) return false;
			if (!aafProxy.userAuthorized(request, roleRequired)) return false;
		}
		
		return true;
	}

	private String getRole(AafRoleRequired aafAnnotation) {
		if (aafAnnotation.roleRequired()!=null && aafAnnotation.roleRequired().length()>0) return aafAnnotation.roleRequired();
		if (roles.containsKey(aafAnnotation.roleProperty())) return roles.get(aafAnnotation.roleProperty());
		if (roles.containsKey(aafAnnotation.roleProperty() + ".role")) return roles.get(aafAnnotation.roleProperty() + ".role");
		throw new MissingRoleException("No role found for annotation: roleRequired = " + aafAnnotation.roleRequired() + ", roleProperty = " + aafAnnotation.roleProperty());
	}

	private boolean basicAuthOk(HttpServletRequest request, Object handler) {
		String authRequired = null;
		try {
			BasicAuthRequired basicAuthAnnotation = null;
			HandlerMethod hm = (HandlerMethod)handler;
			basicAuthAnnotation = hm.getMethodAnnotation(BasicAuthRequired.class);
			authRequired = basicAuthAnnotation.authRequired();
		} catch (RuntimeException e) {
			try {
				PropertyBasedAuthorization pba = null;
				HandlerMethod hm = (HandlerMethod)handler;
				pba = hm.getMethodAnnotation(PropertyBasedAuthorization.class);
				authRequired = basicTags.get(pba.value() + ".basic");
			} catch (RuntimeException e2) {
				// noop
			}
		}
		
		if (authRequired!=null && basicAuthFlag) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"Basic auth required: " + authRequired);

			if (credentials.containsKey(authRequired)) {
				if (request.getHeader("Authorization")!=null && request.getHeader("Authorization").equals("Basic " + credentials.get(authRequired))) return true;
				request.setAttribute("fail", "Basic auth failed  Auth for " + authRequired + ".");
			} else {
				request.setAttribute("fail", "Basic auth not enabled for " + authRequired);
			}
			
			return false;
		}
		
		return true;
	}

	@Override
	public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
		if (!aafOk(request, handler)) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"AAF isn't ok, reason: " + request.getAttribute("fail"));
			request.getRequestDispatcher("/authfail").forward(request, response);
			return false;
		}
		if (!basicAuthOk(request, handler)) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"Basic auth isn't ok, reason: " + request.getAttribute("fail"));
			request.getRequestDispatcher("/authfail").forward(request, response);
			return false;
		}
		
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
