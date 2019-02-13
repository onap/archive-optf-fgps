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

import javax.servlet.ServletContext;

import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.PropertySource;
import org.springframework.core.env.Environment;

/**
 * SystemProperties contains a list of constants used throughout portions of the
 * application. Populated by Spring from multiple configuration files.
 * 
 * Should be used like this:
 * 
 * <pre>
 * 
 * &#64;Autowired
 * SystemProperties systemProperties;
 * </pre>
 */
@Configuration
//@PropertySource(value = { "${container.classpath:}/system.properties" })
@PropertySource(value = { "file:opt/etc/config/system.properties" })
public class SystemProperties {

	private static final EELFLoggerDelegate logger = EELFLoggerDelegate.getLogger(SystemProperties.class);

	private static Environment environment;

	private ServletContext servletContext;

	public static final String APP_DISPLAY_NAME = "app_display_name";
	public static final String APPLICATION_NAME = "application_name";
	public static final String INSTANCE_UUID = "instance_uuid";
	public static final String MDC_CLASS_NAME = "ClassName";
	public static final String MDC_LOGIN_ID = "LoginId";
	public static final String MDC_TIMER = "Timer";
	public static final String APP_NAME = "VALET_API";
	public static final String VALET_REQUEST_ID = "X-VALET-API-RequestID";
	public static final String PARTNER_NAME = "PartnerName";
	public static final String FULL_URL = "Full-URL";
	public static final String AUDITLOG_BEGIN_TIMESTAMP = "AuditLogBeginTimestamp";
	public static final String AUDITLOG_END_TIMESTAMP = "AuditLogEndTimestamp";
	public static final String METRICSLOG_BEGIN_TIMESTAMP = "MetricsLogBeginTimestamp";
	public static final String METRICSLOG_END_TIMESTAMP = "MetricsLogEndTimestamp";
	public static final String CLIENT_IP_ADDRESS = "ClientIPAddress";
	public static final String STATUS_CODE = "StatusCode";
	public static final String RESPONSE_CODE = "ResponseCode";
	// Component or sub component name
	public static final String TARGET_ENTITY = "TargetEntity";
	// API or operation name
	public static final String TARGET_SERVICE_NAME = "TargetServiceName";

	// Logging Compliance
	public static final String SINGLE_QUOTE = "'";
	public static final String NA = "N/A";
	public static final String UNKNOWN = "Unknown";
	public static final String SECURITY_LOG_TEMPLATE = "Protocol:{0}  Security-Event-Type:{1}  Login-ID:{2}  {3}";
	public static final String PROTOCOL = "PROTOCOL";
	public static final String SECURIRY_EVENT_TYPE = "SECURIRY_EVENT_TYPE";
	public static final String LOGIN_ID = "LOGIN_ID";
	public static final String ADDITIONAL_INFO = "ADDITIONAL_INFO";
	public static final String USERAGENT_NAME = "user-agent";

	// Protocols
	public static final String HTTP = "HTTP";
	public static final String HTTPS = "HTTPS";

	public enum RESULT_ENUM {
		SUCCESS, FAILURE
	}

	public enum SecurityEventTypeEnum {
		 INCOMING_REST_MESSAGE, OUTGOING_REST_MESSAGE, REST_AUTHORIZATION_CREDENTIALS_MODIFIED
	}

	public SystemProperties() {
		super();
	}

	protected Environment getEnvironment() {
		return environment;
	}

	@Autowired
	public void setEnvironment(Environment environment) {
		SystemProperties.environment = environment;
	}

	public ServletContext getServletContext() {
		return servletContext;
	}

	public void setServletContext(ServletContext servletContext) {
		this.servletContext = servletContext;
	}

	/**
	 * Tests whether a property value is available for the specified key.
	 * 
	 * @param key
	 *            Property key
	 * @return True if the key is known, otherwise false.
	 */
	public static boolean containsProperty(String key) {
		return environment.containsProperty(key);
	}

	/**
	 * Returns the property value associated with the given key (never
	 * {@code null}), after trimming any trailing space.
	 * 
	 * @param key
	 *            Property key
	 * @return Property value; the empty string if the environment was not
	 *         autowired, which should never happen.
	 * @throws IllegalStateException
	 *             if the key is not found
	 */
	public static String getProperty(String key) {
		String value = "";
		if (environment == null) {
			logger.error(EELFLoggerDelegate.errorLogger, "getProperty: environment is null, should never happen!");
		} else {
			value = environment.getRequiredProperty(key);
			// java.util.Properties preserves trailing space
			if (value != null)
				value = value.trim();
		}
		return value;
	}

	/**
	 * Gets the property value for the key {@link #APPLICATION_NAME}.
	 * 
	 * method created to get around JSTL 1.0 limitation of not being able to access
	 * a static method of a bean
	 * 
	 * @return Application name
	 */
	public String getApplicationName() {
		return getProperty(APPLICATION_NAME);
	}

	/**
	 * Gets the property value for the key {@link #APP_DISPLAY_NAME}.
	 * 
	 * @return Application display name
	 */
	public String getAppDisplayName() {
		return getProperty(APP_DISPLAY_NAME);
	}

}
