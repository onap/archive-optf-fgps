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
package org.onap.fgps.api.logging.aspect;

import static org.onap.fgps.api.eelf.configuration.Configuration.MDC_KEY_REQUEST_ID;

import java.text.SimpleDateFormat;
import java.util.Date;

import javax.servlet.http.HttpServletRequest;

import org.onap.fgps.api.eelf.configuration.Configuration;
import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.onap.fgps.api.logging.format.AuditLogFormatter;
import org.onap.fgps.api.utils.SystemProperties;
import org.onap.fgps.api.utils.SystemProperties.SecurityEventTypeEnum;
import org.slf4j.MDC;

@org.springframework.context.annotation.Configuration
public class EELFLoggerAdvice {

	private static final EELFLoggerDelegate adviceLogger = EELFLoggerDelegate.getLogger(EELFLoggerAdvice.class);

	// DateTime Format according to the  Application Logging Guidelines.
	private static final SimpleDateFormat logDateFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSXXX");

	/**
	 * Gets the current date and time in expected  log format.
	 * 
	 * @return Current date and time
	 */
	public static String getCurrentDateTimeUTC() {
		String currentDateTime = logDateFormat.format(new Date());
		return currentDateTime;
	}

	/**
	 * 
	 * @param securityEventType
	 * @param args
	 * @param passOnArgs
	 * @return One-element array containing an empty String object.
	 */
	public Object[] before(SecurityEventTypeEnum securityEventType, Object[] args, Object[] passOnArgs) {
		try {
			String className = "";
			if (passOnArgs[0] != null) {
				className = passOnArgs[0].toString();
			}

			String methodName = "";
			if (passOnArgs[1] != null) {
				methodName = passOnArgs[1].toString();
			}
			String appName = SystemProperties.APP_NAME;

			EELFLoggerDelegate logger = EELFLoggerDelegate.getLogger(className);

			// Initialize Request defaults only for controller methods.
			MDC.put(className + methodName + SystemProperties.METRICSLOG_BEGIN_TIMESTAMP, getCurrentDateTimeUTC());
			MDC.put(SystemProperties.TARGET_ENTITY, appName);
			MDC.put(SystemProperties.TARGET_SERVICE_NAME, methodName);
			if (securityEventType != null) {
				MDC.put(className + methodName + SystemProperties.AUDITLOG_BEGIN_TIMESTAMP, getCurrentDateTimeUTC());
				for(Object obj : args) {
					if (obj != null && obj instanceof HttpServletRequest) {
						HttpServletRequest req = (HttpServletRequest) obj;
						logger.setRequestBasedDefaultsIntoGlobalLoggingContext(req, appName);
					}else if (obj!= null && obj instanceof String) {
						MDC.put(MDC_KEY_REQUEST_ID, "requestId : "+(String)obj);
					}
				}
			}
			logger.debug(EELFLoggerDelegate.debugLogger, "{} was invoked.", methodName);
		} catch (Exception e) {
			adviceLogger.error(EELFLoggerDelegate.errorLogger, "before failed", e);
		}

		return new Object[] { "" };
	}

	/**
	 * 
	 * @param securityEventType
	 * @param result
	 * @param args
	 * @param returnArgs
	 * @param passOnArgs
	 */
	public void after(SecurityEventTypeEnum securityEventType, String result, Object[] args, Object[] returnArgs,
			Object[] passOnArgs) {
		try {
			String className = "";
			if (passOnArgs[0] != null) {
				className = passOnArgs[0].toString();
			}

			String methodName = "";
			if (passOnArgs[1] != null) {
				methodName = passOnArgs[1].toString();
			}

			EELFLoggerDelegate logger = EELFLoggerDelegate.getLogger(className);

			String appName = SystemProperties.APP_NAME;
			
			if (MDC.get(SystemProperties.TARGET_SERVICE_NAME) == null
					|| MDC.get(SystemProperties.TARGET_SERVICE_NAME) == "") {
				MDC.put(SystemProperties.TARGET_SERVICE_NAME, methodName);
			}

			if (MDC.get(SystemProperties.TARGET_ENTITY) == null || MDC.get(SystemProperties.TARGET_ENTITY) == "") {
				MDC.put(SystemProperties.TARGET_ENTITY, appName);
			}
			
			MDC.put(SystemProperties.STATUS_CODE, result);

			
			MDC.put(SystemProperties.METRICSLOG_BEGIN_TIMESTAMP,
					MDC.get(className + methodName + SystemProperties.METRICSLOG_BEGIN_TIMESTAMP));
			MDC.put(SystemProperties.METRICSLOG_END_TIMESTAMP, getCurrentDateTimeUTC());

			this.calculateDateTimeDifference(MDC.get(SystemProperties.METRICSLOG_BEGIN_TIMESTAMP),
					MDC.get(SystemProperties.METRICSLOG_END_TIMESTAMP));

			logger.info(EELFLoggerDelegate.metricsLogger, methodName + " operation is completed.");
			logger.debug(EELFLoggerDelegate.debugLogger, "Finished executing " + methodName + ".");

			if (securityEventType != null) {

				MDC.put(SystemProperties.AUDITLOG_BEGIN_TIMESTAMP,
						MDC.get(className + methodName + SystemProperties.AUDITLOG_BEGIN_TIMESTAMP));
				MDC.put(SystemProperties.AUDITLOG_END_TIMESTAMP, getCurrentDateTimeUTC());
				this.calculateDateTimeDifference(MDC.get(SystemProperties.AUDITLOG_BEGIN_TIMESTAMP),
						MDC.get(SystemProperties.AUDITLOG_END_TIMESTAMP));

				this.logSecurityMessage(logger, securityEventType, result, methodName);

				// clear when finishes audit logging
				MDC.remove(Configuration.MDC_KEY_REQUEST_ID);
				MDC.remove(SystemProperties.PARTNER_NAME);
				MDC.remove(SystemProperties.MDC_LOGIN_ID);
				MDC.remove(SystemProperties.PROTOCOL);
				MDC.remove(SystemProperties.FULL_URL);
				MDC.remove(Configuration.MDC_SERVICE_NAME);
				MDC.remove(SystemProperties.RESPONSE_CODE);
				MDC.remove(SystemProperties.STATUS_CODE);
				MDC.remove(className + methodName + SystemProperties.AUDITLOG_BEGIN_TIMESTAMP);
				MDC.remove(SystemProperties.AUDITLOG_BEGIN_TIMESTAMP);
				MDC.remove(SystemProperties.AUDITLOG_END_TIMESTAMP);
			}else{
				MDC.put(SystemProperties.STATUS_CODE, "COMPLETE");
			}

			MDC.remove(className + methodName + SystemProperties.METRICSLOG_BEGIN_TIMESTAMP);
			MDC.remove(SystemProperties.METRICSLOG_BEGIN_TIMESTAMP);
			MDC.remove(SystemProperties.METRICSLOG_END_TIMESTAMP);
			MDC.remove(SystemProperties.MDC_TIMER);
			MDC.remove(SystemProperties.TARGET_ENTITY);
			MDC.remove(SystemProperties.TARGET_SERVICE_NAME);
			MDC.remove(SystemProperties.STATUS_CODE);

		} catch (Exception e) {
			adviceLogger.error(EELFLoggerDelegate.errorLogger, "after failed", e);
		}
	}

	/**
	 * 
	 * @param logger
	 * @param securityEventType
	 * @param result
	 * @param restMethod
	 */
	private void logSecurityMessage(EELFLoggerDelegate logger, SecurityEventTypeEnum securityEventType, String result,
			String restMethod) {
		StringBuilder additionalInfoAppender = new StringBuilder();

		additionalInfoAppender.append(String.format("%s request was received.", restMethod));

		// Status code
		MDC.put(SystemProperties.STATUS_CODE, result);

		String fullURL = MDC.get(SystemProperties.FULL_URL);
		if (fullURL != null && fullURL != "") {
			additionalInfoAppender.append(" Request-URL:" + MDC.get(SystemProperties.FULL_URL));
		}

		String auditMessage = AuditLogFormatter.getInstance().createMessage(MDC.get(SystemProperties.PROTOCOL),
				securityEventType.name(), MDC.get(SystemProperties.MDC_LOGIN_ID), additionalInfoAppender.toString());

		logger.info(EELFLoggerDelegate.auditLogger, auditMessage);
	}

	/**
	 * 
	 * @param beginDateTime
	 * @param endDateTime
	 */
	private void calculateDateTimeDifference(String beginDateTime, String endDateTime) {
		if (beginDateTime != null && endDateTime != null) {
			try {
				Date beginDate = logDateFormat.parse(beginDateTime);
				Date endDate = logDateFormat.parse(endDateTime);
				String timeDifference = String.format("%d", endDate.getTime() - beginDate.getTime());
				MDC.put(SystemProperties.MDC_TIMER, timeDifference);
			} catch (Exception e) {
				adviceLogger.error(EELFLoggerDelegate.errorLogger, "calculateDateTimeDifference failed", e);
			}
		}
	}
}
