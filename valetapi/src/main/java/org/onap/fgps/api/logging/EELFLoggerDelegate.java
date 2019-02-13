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
package org.onap.fgps.api.logging;

import static org.onap.fgps.api.eelf.configuration.Configuration.MDC_ALERT_SEVERITY;
import static org.onap.fgps.api.eelf.configuration.Configuration.MDC_INSTANCE_UUID;
import static org.onap.fgps.api.eelf.configuration.Configuration.MDC_SERVER_FQDN;
import static org.onap.fgps.api.eelf.configuration.Configuration.MDC_SERVER_IP_ADDRESS;
import static org.onap.fgps.api.eelf.configuration.Configuration.MDC_SERVICE_INSTANCE_ID;
import static org.onap.fgps.api.eelf.configuration.Configuration.MDC_SERVICE_NAME;

import java.net.InetAddress;
import java.text.MessageFormat;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

import javax.servlet.http.HttpServletRequest;

import org.onap.fgps.api.eelf.configuration.EELFLogger;
import org.onap.fgps.api.eelf.configuration.EELFManager;
import org.onap.fgps.api.eelf.configuration.SLF4jWrapper;
import org.onap.fgps.api.logging.aspect.EELFLoggerAdvice;
import org.onap.fgps.api.logging.format.AlarmSeverityEnum;
//import org.onap.portalsdk.core.domain.User;
import org.onap.fgps.api.utils.SystemProperties;
import org.onap.fgps.api.utils.UserUtils;;
import org.slf4j.MDC;


public class EELFLoggerDelegate extends SLF4jWrapper implements EELFLogger {


	public static final EELFLogger errorLogger = EELFManager.getInstance().getErrorLogger();
	public static final EELFLogger applicationLogger = EELFManager.getInstance().getApplicationLogger();
	public static final EELFLogger auditLogger = EELFManager.getInstance().getAuditLogger();
	public static final EELFLogger metricsLogger = EELFManager.getInstance().getMetricsLogger();
	public static final EELFLogger debugLogger = EELFManager.getInstance().getDebugLogger();

	private String className;
	private static ConcurrentMap<String, EELFLoggerDelegate> classMap = new ConcurrentHashMap<>();

	public EELFLoggerDelegate(final String className) {
		super(className);
		this.className = className;
	}

	/**
	 * Convenience method that gets a logger for the specified class.
	 * 
	 * @see #getLogger(String)
	 * 
	 * @param clazz
	 * @return Instance of EELFLoggerDelegate
	 */
	public static EELFLoggerDelegate getLogger(Class<?> clazz) {
		return getLogger(clazz.getName());
	}

	/**
	 * Gets a logger for the specified class name. If the logger does not already
	 * exist in the map, this creates a new logger.
	 * 
	 * @param className
	 *            If null or empty, uses EELFLoggerDelegate as the class name.
	 * @return Instance of EELFLoggerDelegate
	 */
	public static EELFLoggerDelegate getLogger(final String className) {
		String classNameNeverNull = className == null || "".equals(className) ? EELFLoggerDelegate.class.getName()
				: className;
		EELFLoggerDelegate delegate = classMap.get(classNameNeverNull);
		if (delegate == null) {
			delegate = new EELFLoggerDelegate(className);
			classMap.put(className, delegate);
		}
		return delegate;
	}

	/**
	 * Logs a message at the lowest level: trace.
	 * 
	 * @param logger
	 * @param msg
	 */
	public void trace(EELFLogger logger, String msg) {
		if (logger.isTraceEnabled()) {
			MDC.put(SystemProperties.MDC_CLASS_NAME, className);
			logger.trace(msg);
			MDC.remove(SystemProperties.MDC_CLASS_NAME);
		}
	}

	/**
	 * Logs a message with parameters at the lowest level: trace.
	 * 
	 * @param logger
	 * @param msg
	 * @param arguments
	 */
	public void trace(EELFLogger logger, String msg, Object... arguments) {
		if (logger.isTraceEnabled()) {
			MDC.put(SystemProperties.MDC_CLASS_NAME, className);
			logger.trace(msg, arguments);
			MDC.remove(SystemProperties.MDC_CLASS_NAME);
		}
	}

	/**
	 * Logs a message and throwable at the lowest level: trace.
	 * 
	 * @param logger
	 * @param msg
	 * @param th
	 */
	public void trace(EELFLogger logger, String msg, Throwable th) {
		if (logger.isTraceEnabled()) {
			MDC.put(SystemProperties.MDC_CLASS_NAME, className);
			logger.trace(msg, th);
			MDC.remove(SystemProperties.MDC_CLASS_NAME);
		}
	}

	/**
	 * Logs a message at the second-lowest level: debug.
	 * 
	 * @param logger
	 * @param msg
	 */
	public void debug(EELFLogger logger, String msg) {
		if (logger.isDebugEnabled()) {
			MDC.put(SystemProperties.MDC_CLASS_NAME, className);
			logger.debug(msg);
			MDC.remove(SystemProperties.MDC_CLASS_NAME);
		}
	}

	/**
	 * Logs a message with parameters at the second-lowest level: debug.
	 * 
	 * @param logger
	 * @param msg
	 * @param arguments
	 */
	public void debug(EELFLogger logger, String msg, Object... arguments) {
		if (logger.isDebugEnabled()) {
			MDC.put(SystemProperties.MDC_CLASS_NAME, className);
			logger.debug(msg, arguments);
			MDC.remove(SystemProperties.MDC_CLASS_NAME);
		}
	}

	/**
	 * Logs a message and throwable at the second-lowest level: debug.
	 * 
	 * @param logger
	 * @param msg
	 * @param th
	 */
	public void debug(EELFLogger logger, String msg, Throwable th) {
		if (logger.isDebugEnabled()) {
			MDC.put(SystemProperties.MDC_CLASS_NAME, className);
			logger.debug(msg, th);
			MDC.remove(SystemProperties.MDC_CLASS_NAME);
		}
	}

	/**
	 * Logs a message at info level.
	 * 
	 * @param logger
	 * @param msg
	 */
	public void info(EELFLogger logger, String msg) {
		MDC.put(SystemProperties.MDC_CLASS_NAME, className);
		logger.info(msg);
		MDC.remove(SystemProperties.MDC_CLASS_NAME);
	}

	/**
	 * Logs a message with parameters at info level.
	 *
	 * @param logger
	 * @param msg
	 * @param arguments
	 */
	public void info(EELFLogger logger, String msg, Object... arguments) {
		MDC.put(SystemProperties.MDC_CLASS_NAME, className);
		logger.info(msg, arguments);
		MDC.remove(SystemProperties.MDC_CLASS_NAME);
	}

	/**
	 * Logs a message and throwable at info level.
	 * 
	 * @param logger
	 * @param msg
	 * @param th
	 */
	public void info(EELFLogger logger, String msg, Throwable th) {
		MDC.put(SystemProperties.MDC_CLASS_NAME, className);
		logger.info(msg, th);
		MDC.remove(SystemProperties.MDC_CLASS_NAME);
	}

	/**
	 * Logs a message at warn level.
	 * 
	 * @param logger
	 * @param msg
	 */
	public void warn(EELFLogger logger, String msg) {
		MDC.put(SystemProperties.MDC_CLASS_NAME, className);
		logger.warn(msg);
		MDC.remove(SystemProperties.MDC_CLASS_NAME);
	}

	/**
	 * Logs a message with parameters at warn level.
	 * 
	 * @param logger
	 * @param msg
	 * @param arguments
	 */
	public void warn(EELFLogger logger, String msg, Object... arguments) {
		MDC.put(SystemProperties.MDC_CLASS_NAME, className);
		logger.warn(msg, arguments);
		MDC.remove(SystemProperties.MDC_CLASS_NAME);
	}

	/**
	 * Logs a message and throwable at warn level.
	 * 
	 * @param logger
	 * @param msg
	 * @param th
	 */
	public void warn(EELFLogger logger, String msg, Throwable th) {
		MDC.put(SystemProperties.MDC_CLASS_NAME, className);
		logger.warn(msg, th);
		MDC.remove(SystemProperties.MDC_CLASS_NAME);
	}

	/**
	 * Logs a message at error level.
	 * 
	 * @param logger
	 * @param msg
	 */
	public void error(EELFLogger logger, String msg) {
		MDC.put(SystemProperties.MDC_CLASS_NAME, className);
		logger.error(msg);
		MDC.remove(SystemProperties.MDC_CLASS_NAME);
	}

	/**
	 * Logs a message with parameters at error level.
	 * 
	 * @param logger
	 * @param msg
	 * @param arguments
	 */
	public void error(EELFLogger logger, String msg, Object... arguments) {
		MDC.put(SystemProperties.MDC_CLASS_NAME, className);
		logger.warn(msg, arguments);
		MDC.remove(SystemProperties.MDC_CLASS_NAME);
	}

	/**
	 * Logs a message and throwable at error level.
	 * 
	 * @param logger
	 * @param msg
	 * @param th
	 */
	public void error(EELFLogger logger, String msg, Throwable th) {
		MDC.put(SystemProperties.MDC_CLASS_NAME, className);
		logger.warn(msg, th);
		MDC.remove(SystemProperties.MDC_CLASS_NAME);
	}

	/**
	 * Logs a message with the associated alarm severity at error level.
	 * 
	 * @param logger
	 * @param msg
	 * @param severtiy
	 */
	public void error(EELFLogger logger, String msg, AlarmSeverityEnum severtiy) {
		MDC.put(MDC_ALERT_SEVERITY, severtiy.name());
		MDC.put(SystemProperties.MDC_CLASS_NAME, className);
		logger.error(msg);
		MDC.remove(MDC_ALERT_SEVERITY);
		MDC.remove(SystemProperties.MDC_CLASS_NAME);
	}

	/**
	 * Initializes the logger context.
	 */
	public void init() {
		setGlobalLoggingContext();
		final String msg = "############################ Logging is started. ############################";
		// These loggers emit the current date-time without being told.
		info(applicationLogger, msg);
		error(errorLogger, msg);
		debug(debugLogger, msg);
		// Audit and metrics logger must be told start AND stop times
		final String currentDateTime = EELFLoggerAdvice.getCurrentDateTimeUTC();
		// Set the MDC with audit properties
		MDC.put(SystemProperties.AUDITLOG_BEGIN_TIMESTAMP, currentDateTime);
		MDC.put(SystemProperties.AUDITLOG_END_TIMESTAMP, currentDateTime);
		info(auditLogger, msg);
		MDC.remove(SystemProperties.AUDITLOG_BEGIN_TIMESTAMP);
		MDC.remove(SystemProperties.AUDITLOG_END_TIMESTAMP);
		// Set the MDC with metrics properties
		MDC.put(SystemProperties.METRICSLOG_BEGIN_TIMESTAMP, currentDateTime);
		MDC.put(SystemProperties.METRICSLOG_END_TIMESTAMP, currentDateTime);
		info(metricsLogger, msg);
		MDC.remove(SystemProperties.METRICSLOG_BEGIN_TIMESTAMP);
		MDC.remove(SystemProperties.METRICSLOG_END_TIMESTAMP);
	}

	/**
	 * Builds a message using a template string and the arguments.
	 * 
	 * @param message
	 * @param args
	 * @return
	 */
	private String formatMessage(String message, Object... args) {
		StringBuilder sbFormattedMessage = new StringBuilder();
		if (args != null && args.length > 0 && message != null && message != "") {
			MessageFormat mf = new MessageFormat(message);
			sbFormattedMessage.append(mf.format(args));
		} else {
			sbFormattedMessage.append(message);
		}

		return sbFormattedMessage.toString();
	}

	/**
	 * Loads all the default logging fields into the MDC context.
	 */
	private void setGlobalLoggingContext() {
		MDC.put(MDC_SERVICE_INSTANCE_ID, "");
		MDC.put(MDC_ALERT_SEVERITY, AlarmSeverityEnum.INFORMATIONAL.toString());
		try {
			MDC.put(MDC_SERVER_FQDN, InetAddress.getLocalHost().getHostName());
			MDC.put(MDC_SERVER_IP_ADDRESS, InetAddress.getLocalHost().getHostAddress());
			MDC.put(MDC_INSTANCE_UUID, SystemProperties.getProperty(SystemProperties.INSTANCE_UUID));
		} catch (Exception e) {
			errorLogger.error("setGlobalLoggingContext failed", e);
		}
	}

	public static void mdcPut(String key, String value) {
		MDC.put(key, value);
	}

	public static String mdcGet(String key) {
		return MDC.get(key);
	}

	public static void mdcRemove(String key) {
		MDC.remove(key);
	}

	/**
	 * Loads the RequestId/TransactionId into the MDC which it should be receiving
	 * with an each incoming REST API request. Also, configures few other request
	 * based logging fields into the MDC context.
	 * 
	 * @param req
	 * @param appName
	 */
	public void setRequestBasedDefaultsIntoGlobalLoggingContext(HttpServletRequest req, String appName) {
		// Load the default fields
		setGlobalLoggingContext();

		// Load the request based fields
		if (req != null) {
			// Load user agent into MDC context, if available.
			String accessingClient = req.getHeader(SystemProperties.USERAGENT_NAME);
			if (accessingClient != null && !"".equals(accessingClient) && (accessingClient.contains("Mozilla")
					|| accessingClient.contains("Chrome") || accessingClient.contains("Safari"))) {
				accessingClient = appName + "_FE";
			}
			MDC.put(SystemProperties.PARTNER_NAME, accessingClient);

			// Protocol, Rest URL & Rest Path
			MDC.put(SystemProperties.FULL_URL, SystemProperties.UNKNOWN);
			MDC.put(SystemProperties.PROTOCOL, SystemProperties.HTTP);
			String restURL = UserUtils.getFullURL(req);
			if (restURL != null && restURL != "") {
				MDC.put(SystemProperties.FULL_URL, restURL);
				if (restURL.toLowerCase().contains("https")) {
					MDC.put(SystemProperties.PROTOCOL, SystemProperties.HTTPS);
				}
			}

			// Rest Path
			MDC.put(MDC_SERVICE_NAME, req.getServletPath());

			// Client IPAddress i.e. IPAddress of the remote host who is making
			// this request.
			String clientIPAddress = req.getHeader("X-FORWARDED-FOR");
			if (clientIPAddress == null) {
				clientIPAddress = req.getRemoteAddr();
			}
			MDC.put(SystemProperties.CLIENT_IP_ADDRESS, clientIPAddress);
		}
	}
}
