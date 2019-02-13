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
package org.onap.fgps.api.proxy;

import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import javax.servlet.http.HttpServletRequest;

import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.onap.fgps.api.utils.CipherUtil;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;

public class AAFProxy {
	public static class Auth {
		public String id;
		public String password;
	}
	
	public static class Item {
		public String id;
		public String expires;
	}
	
	public static class User {
		public List<Item> user;
	}
	
	private static final EELFLoggerDelegate LOGGER = EELFLoggerDelegate.getLogger(AAFProxy.class);
	private static final SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSXXX");

	private String aafUrlBase;
	private String encodedPassword = null;

	public AAFProxy(String aafUrlBase) {
		this.aafUrlBase = aafUrlBase;
	}

	public boolean userAuthenticated(HttpServletRequest request) {
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"In AAFProxy.userAutheniticated");
		String user = request.getHeader("mechId");
		if (user==null || user.length()==0) {
			request.setAttribute("fail", "AAF failed: mechId header not present.");
			return false;
		}

		String encpassword = request.getHeader("password");
		if (encpassword==null || encpassword.length()==0) {
			request.setAttribute("fail", "AAF failed: password header not present.");
			return false;
		}
		String password = CipherUtil.decryptPKC(encpassword);
		
		String urlStr = aafUrlBase + "/authn/validate";
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"Going to call AAF, url = " + urlStr);
		
		try {
			RestTemplate restTemplate = new RestTemplate(); 

			HttpHeaders headers = new HttpHeaders();
	        headers.add("Authorization", "Basic " + encodedPassword);
	        headers.add("Accept", "application/Users+json;q=1.0;charset=utf-8;version=2.0,application/json;q=1.0;version=2.0,*/*;q=1.0");
	        headers.add("Content-Type", "application/json");
	        LOGGER.info(EELFLoggerDelegate.applicationLogger,"Headers = " + headers);
	        
	        Auth auth = new Auth();
	        auth.id = user;
	        auth.password = password;
	        ObjectMapper mapper = new ObjectMapper();
	        String body = mapper.writeValueAsString(auth);
	        LOGGER.info(EELFLoggerDelegate.applicationLogger,"Call body = " + body.replaceAll("\"password\": ?\".*?\"", "\"password\": \"*****\""));
	        
	        HttpEntity<String> aafRequest = new HttpEntity<String>(body, headers);

	        ResponseEntity<String> response = restTemplate.exchange(urlStr, HttpMethod.POST, aafRequest, String.class);
	        if (response.getStatusCode().equals(HttpStatus.OK)) {
	        	LOGGER.info(EELFLoggerDelegate.applicationLogger,"AAF returned 200 OK");
	        	return true;
	        } else {
	        	LOGGER.info(EELFLoggerDelegate.applicationLogger,"Unexpected status code returned from AAF? " + response.getStatusCode());
	        	if (response.getStatusCodeValue()>=200 && response.getStatusCodeValue()<=299) {
		        	LOGGER.info(EELFLoggerDelegate.applicationLogger,"Status code is 2XX, assuming OK");
	        		return true;
	        	} else {
	        		LOGGER.warn(EELFLoggerDelegate.applicationLogger,"Status code is not 2XX (" + response.getStatusCode() + "), assuming failed.");
	        		request.setAttribute("fail", "AAF failed: AAF returned status code " + response.getStatusCode());
	        		return false;
	        	}
	        }
			
		} catch (HttpClientErrorException e) {
			if (e.getStatusCode().equals(HttpStatus.FORBIDDEN)) {
				LOGGER.warn(EELFLoggerDelegate.applicationLogger,"AAF returned 403 Forbidden");
				request.setAttribute("fail", "AAF failed: user not authenticated.");
				return false;
			} else {
        		LOGGER.warn(EELFLoggerDelegate.applicationLogger,"Status code is not 2XX (" + e.getStatusCode() + "), assuming failed.");
        		request.setAttribute("fail", "AAF failed: AAF returned status code " + e.getStatusCode());
        		return false;
			}
		} catch (JsonProcessingException e) {
			LOGGER.error(EELFLoggerDelegate.errorLogger,"Call to AAF threw an exception: " + e);
    		request.setAttribute("fail", "AAF failed: Couldn't convert call body? " + e);
    		return false;
		} catch (RestClientException e) {
			LOGGER.error(EELFLoggerDelegate.errorLogger,"Call to AAF threw an exception: " + e);
    		request.setAttribute("fail", "AAF failed: call to AAF threw an exception " + e);
    		return false;
		}
	}

	public boolean userAuthorized(HttpServletRequest request, String roleRequired) {
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"In AAFProxy.userAuthorized");
		String user = request.getHeader("mechId");
		if (user==null || user.length()==0) {
			request.setAttribute("fail", "AAF failed: mechId header not present.");
			return false;
		}
		String urlStr = aafUrlBase + "/authz/users/" + user + "/" + roleRequired;
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"Going to call AAF, url = " + urlStr);

		try {
			RestTemplate restTemplate = new RestTemplate(); 

			HttpHeaders headers = new HttpHeaders();
	        headers.add("Authorization", "Basic " + encodedPassword);
	        headers.add("Accept", "application/Users+json;q=1.0;charset=utf-8;version=2.0,application/json;q=1.0;version=2.0,*/*;q=1.0");
	        
	        HttpEntity<String> aafRequest = new HttpEntity<String>(null, headers);

	        ResponseEntity<String> response = restTemplate.exchange(urlStr, HttpMethod.GET, aafRequest, String.class);

	        LOGGER.info(EELFLoggerDelegate.applicationLogger,"Received from AAF: " + response.getBody());
			ObjectMapper mapper = new ObjectMapper();
			User aafuser;
			aafuser = mapper.readValue(response.getBody(), User.class);
			if (aafuser.user==null) aafuser.user = new ArrayList<Item>();
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"User is a " + aafuser + " with " + aafuser.user.size() + (aafuser.user.size()==0?"":(" items; " + aafuser.user.get(0).id + ", " + aafuser.user.get(0).expires)) );
			
			Date now = new Date();
			for (Item item : aafuser.user) {
				Date expiryDate = sdf.parse(item.expires);
				LOGGER.info(EELFLoggerDelegate.applicationLogger,"Comparing " + item.id  +" to " + user);
				if (!item.id.equals(user)) continue;
				LOGGER.info(EELFLoggerDelegate.applicationLogger,"Comparing " + now + " to " + expiryDate);
				if (now.compareTo(expiryDate)>0) {
					request.setAttribute("fail", "AAF failed: user role is expired.");
					return false;
				}
				LOGGER.info(EELFLoggerDelegate.applicationLogger,"Success! User authorized.");
				return true;
			}
		} catch (JsonParseException | JsonMappingException e) {
			e.printStackTrace();
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"Exception while calling AAF: " + e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"Exception while calling AAF: " + e);
			request.setAttribute("fail", "AAF failed: invalid JSON returned from AAF? (" + e + ")");
			return false;
		} catch (RuntimeException | IOException e) {
			e.printStackTrace();
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"Exception while calling AAF: " + e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"Exception while calling AAF: " + e);
			request.setAttribute("fail", "AAF failed: exception in call to AAF (" + e + ")");
			return false;
		} catch (ParseException e) {
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"Exception while calling AAF: " + e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"Exception while calling AAF: " + e);
			e.printStackTrace();
			request.setAttribute("fail", "AAF failed: invalid date format returned from AAF? (" + e + ")");
			return false;
		}
		
		request.setAttribute("fail", "AAF failed: user does not have role.");
		return false;
	}

	public void setCredentials(String encodedPassword) {
		if (encodedPassword!=null) this.encodedPassword = encodedPassword;
	}

}
