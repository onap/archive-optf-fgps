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
package org.onap.fgps.api.eelf.configuration;

/**
 * This interface defines the configuration support and logger names in EELF.
 * It also defines the MDC key names.
 * 
 *
 */
public interface Configuration {
	

	 /**
	  * The name of the property used to define the filename for the logback configuration
	  */
	 public String PROPERTY_LOGGING_FILE_NAME = "org.onap.eelf.logging.file";
	 
	 /**
	  * The name of the property used to define the filename for the logback configuration
	  */
	 public String PROPERTY_LOGGING_FILE_PATH = "org.onap.eelf.logging.path";

	 /**
	  * Logger name to be used for application general logging
	  */
	public String GENERAL_LOGGER_NAME = "org.onap.eelf";

	 
	 /**
	  * Logger name to be used for application metrics logging
	  */
	public String METRICS_LOGGER_NAME = "org.onap.eelf.metrics";
	    

	 /**
	  * Logger name to be used for  application performance metrics
	  */
	public String PERF_LOGGER_NAME = "org.onap.eelf.perf";
	    

	 /**
	   * Logger name to be used for application policy logging
	   */
	public String POLICY_LOGGER_NAME = "org.onap.eelf.policy";
	    

	 /**
	   * Logger name to be used for  application security logging
	   */
	public String SECURITY_LOGGER_NAME = "org.onap.eelf.security";
	    

	  /**
	   * Logger name to be used for application server logging
	   */
	public String SERVER_LOGGER_NAME = "org.onap.eelf.server";
	    
	 /**
	  * Logger name to be used for  application audit logging
	  */
	public String AUDIT_LOGGER_NAME = "org.onap.eelf.audit";
	
	 /**
	  * Logger name to be used for  error logging
	  */
	 public String ERROR_LOGGER_NAME = "org.onap.eelf.error";
	 
	 /**
	  * Logger name to be used for  debug logging
	  */
	 public String DEBUG_LOGGER_NAME = "org.onap.eelf.debug";
	 
	 /**
	  * The requestID is primarily used to track the processing of a request referencing 
	  * a single instance of a service through the various sub-components.
	  */
	 public String MDC_KEY_REQUEST_ID = "RequestId";
	 
	 
	 /**
	  * The serviceInstanceID  can be used to uniquely identity a service instance.
	  */
	 public String MDC_SERVICE_INSTANCE_ID = "ServiceInstanceId";
	 
	 
	 /**
	  * The serviceName can be used  identify the name of the service.
	  */
	 public String MDC_SERVICE_NAME = "ServiceName";
	 
	 
	 /**
	  * The instanceUUID can be used to differentiate between multiple instances of the same (named), log writing service/application
	  */
	 public String MDC_INSTANCE_UUID= "InstanceUUID";
	 
	     /**
     * The serverIPAddress can be used to log the host server's IP address. (e.g. Jetty container's listening IP
     * address)
     */
	 public String MDC_SERVER_IP_ADDRESS = "ServerIPAddress";
	 
	 
	     /**
     * The serverFQDN can be used to log the host server's FQDN.
     */
	 public String MDC_SERVER_FQDN = "ServerFQDN";
	 
	 /**
	  * The remote host name/ip address making the request
	  */
	 public static final String MDC_REMOTE_HOST = "RemoteHost";
	 
	/**
	 * The severity can be used to map to severity in alert messages eg. nagios alerts
	 */
	 public String MDC_ALERT_SEVERITY = "AlertSeverity";
	 
	 



}
