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
import java.io.InputStream;
import java.util.Properties;

import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.onap.fgps.api.utils.CipherUtil;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;
import org.onap.fgps.api.utils.UserUtils;

public class DBProxy {
	private  String[] server;
	private RestTemplate rest;
	private HttpHeaders headers;
	private HttpStatus status;
	private String ipAddress;
	private boolean pingLogFlag;

	private static final EELFLoggerDelegate LOGGER = EELFLoggerDelegate.getLogger(DBProxy.class);
	InputStream inputStream;
	
	

	public DBProxy(boolean pingFlag) {
		this.pingLogFlag = pingFlag;
		this.rest = new RestTemplate();
		this.headers = new HttpHeaders();
		headers.add("Content-Type", "application/json");
		Properties props = new Properties();
		String propFileName = "resources.properties";
		inputStream = getClass().getClassLoader().getResourceAsStream(propFileName);
		try {
			if (inputStream != null) {
				props.load(inputStream);
			} else {
				if(pingLogFlag) {
					LOGGER.info(EELFLoggerDelegate.applicationLogger,"DBProxy : inputstream is not");
				}
			}
		} catch (IOException e) {
			e.printStackTrace();
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"DBProxy : Error details : "+ e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"DBProxy : Error details : "+ e.getMessage());
		}
		server = new String[3];
		server[0] = "http://" + UserUtils.htmlEscape(props.getProperty("musicdb.ip.1")) + ":" + UserUtils.htmlEscape(props.getProperty("music.MUSIC_DB_PORT"))
				+ UserUtils.htmlEscape(props.getProperty("music.MUSIC_DB_URL"));
		server[1] = "http://" + UserUtils.htmlEscape(props.getProperty("musicdb.ip.2")) + ":" + UserUtils.htmlEscape(props.getProperty("music.MUSIC_DB_PORT"))
				+ UserUtils.htmlEscape(props.getProperty("music.MUSIC_DB_URL"));
		server[2] = "http://" + UserUtils.htmlEscape(props.getProperty("musicdb.ip.3")) + ":" + UserUtils.htmlEscape(props.getProperty("music.MUSIC_DB_PORT"))
				+ UserUtils.htmlEscape(props.getProperty("music.MUSIC_DB_URL"));
		headers.add("ns", UserUtils.htmlEscape(props.getProperty("musicdb.namespace")));
		headers.add("userId", UserUtils.htmlEscape(props.getProperty("musicdb.userId")));
		headers.add("password", CipherUtil.decryptPKC(props.getProperty("musicdb.password")));
		//keep headers userID and password for now, it works with old version
		//new version of music(1810) needs userID and password as basic auth 
		headers.add("Authorization", CipherUtil.encodeBasicAuth(props.getProperty("musicdb.userId"), CipherUtil.decryptPKC(props.getProperty("musicdb.password"))));


	}

	public DBProxy() {
		this(true);
	}

	public String retryRequest(String uri, HttpMethod operation, HttpEntity<String> requestEntity, int n) {
		try {
			StringBuffer headerOut = new StringBuffer();
			HttpHeaders httpHeaders = requestEntity.getHeaders();
			for (String key: httpHeaders.keySet()) {
				headerOut.append(", ");
				if (key.toLowerCase().contains("pass") || key.equals("Authorization")) {
					headerOut.append(key + ": PASSWORD CENSORED");
				} else {
					headerOut.append(key + ": [" + httpHeaders.get(key) + "]");
				}
			}
			
			String finalUri = this.server[n] + uri;
			finalUri = finalUri.replaceAll("//", "/").replaceFirst("/", "//");
			if(pingLogFlag) {
				LOGGER.info(EELFLoggerDelegate.applicationLogger, "DBProxy: Sending request to DB : "+ finalUri + ", " + operation + headerOut.toString() );
			}
			// System.out.println();
			ResponseEntity<String> responseEntity = rest.exchange( finalUri, operation, requestEntity, String.class);
			this.setStatus(responseEntity.getStatusCode());
			if(pingLogFlag) {
				LOGGER.info(EELFLoggerDelegate.applicationLogger, "DBProxy: Received response from DB: " + responseEntity.toString() + ", " + responseEntity.getStatusCode());
			}
			return responseEntity.getBody();
		} catch (HttpClientErrorException e) {
			if(pingLogFlag) {
				LOGGER.info(EELFLoggerDelegate.applicationLogger,"DBProxy : HttpClientErrorException in received response: " + e.getResponseBodyAsString() + ", " + e.getStatusCode());
				LOGGER.debug(EELFLoggerDelegate.applicationLogger, " Response headers: " + e.getResponseHeaders());
			}
			LOGGER.info(EELFLoggerDelegate.errorLogger,"DBProxy : HttpClientErrorException in received response: " + e.getResponseBodyAsString() + ", " + e.getStatusCode());
			LOGGER.debug(EELFLoggerDelegate.errorLogger, " Response headers: " + e.getResponseHeaders());
			if (n < 2) {
				if(pingLogFlag) {
					LOGGER.info(EELFLoggerDelegate.applicationLogger, "Trying again");
				}
				return retryRequest(uri, operation, requestEntity, n + 1);
			} else {
				LOGGER.error(EELFLoggerDelegate.applicationLogger,"Error while accessing MUSIC: "+ e.getMessage());
				LOGGER.error(EELFLoggerDelegate.errorLogger,"Error while accessing MUSIC: ");
				LOGGER.error(EELFLoggerDelegate.errorLogger,"Error details: "+ e.getMessage());
				return "DBRequest Failed";
			}
		} catch (Exception e) {
			if (n < 2) {
				if(pingLogFlag) {
					LOGGER.info(EELFLoggerDelegate.applicationLogger,"DBProxy : Exception in received response :  "+ this.server[n] + ", " + e + ", retrying ...");
				}
				LOGGER.info(EELFLoggerDelegate.errorLogger,"DBProxy : Exception in received response :  "+ this.server[n] + ", " + e + ", retrying ...");
				return retryRequest(uri, operation, requestEntity, n + 1);
			} else {
				LOGGER.error(EELFLoggerDelegate.applicationLogger,"Error while accessing MUSIC: "+ e.getMessage());
				LOGGER.error(EELFLoggerDelegate.errorLogger,"Error while accessing MUSIC: ");
				LOGGER.error(EELFLoggerDelegate.errorLogger,"Error details: "+ e.getMessage());
				return "DBRequest Failed";
			}
		}
	}

	public String post(String uri, String json) {
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"DBProxy : Post request sent");

		HttpEntity<String> requestEntity = new HttpEntity<String>(json, headers);
		// System.out.println(headers);
		System.out.println("In DBProxy.post, Headers: " + requestEntity.getHeaders().toString().replaceAll("password=\\[.*?\\]", "password=CENSORED").replaceAll("Authorization=\\[Basic.*?\\]", "Authorization=Basic CENSORED"));
		System.out.println("In DBProxy.post, Body: " + requestEntity.getBody().toString());
		return retryRequest(uri, HttpMethod.POST, requestEntity, 0);
	}

	public String get(String uri) {
		if(pingLogFlag) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"DBProxy : Get request sent");
		}

		HttpEntity<String> requestEntity = new HttpEntity<String>("", headers);
		if(pingLogFlag) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"Requesting : "+server + uri);
		}
		
		return retryRequest(uri, HttpMethod.GET, requestEntity, 0);
	}

	public String put(String uri, String json) {
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"DBProxy : Put request sent");

		HttpEntity<String> requestEntity = new HttpEntity<String>(json, headers);
	
		return retryRequest(uri, HttpMethod.PUT, requestEntity, 0);
	}

	public String delete(String uri, String json) {
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"DBProxy : Delete request sent");

		HttpEntity<String> requestEntity = new HttpEntity<String>(json, headers);
		
		return retryRequest(uri, HttpMethod.DELETE, requestEntity, 0);
	}

	public HttpStatus getStatus() {
		return status;
	}

	public void setStatus(HttpStatus status) {
		this.status = status;
	}
}
