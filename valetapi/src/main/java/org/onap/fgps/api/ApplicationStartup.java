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
package org.onap.fgps.api;

import java.io.InputStream;
import java.util.Properties;

import org.onap.fgps.api.dao.SchemaDAO;
import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.ApplicationListener;
import org.springframework.stereotype.Component;
import org.onap.fgps.api.utils.UserUtils;

@Component
public class ApplicationStartup implements ApplicationListener<ApplicationReadyEvent> {

	private SchemaDAO schemaDAO;
	//private static final Logger LOGGER = LoggerFactory.getLogger(ValetServiceApplication.class);
	private EELFLoggerDelegate LOGGER = EELFLoggerDelegate.getLogger(ApplicationStartup.class);


	@Autowired
	public ApplicationStartup(SchemaDAO schemaDAO) {
		super();
		this.schemaDAO = schemaDAO;
	}

	/**
	 * This event is executed as late as conceivably possible to indicate that
	 * the application is ready to service requests.
	 */
	@Override
	public void onApplicationEvent(final ApplicationReadyEvent event) {
		Properties props = new Properties();
		String propFileName = "resources.properties";
		InputStream inputStream = getClass().getClassLoader().getResourceAsStream(propFileName);
		try {
			if (inputStream != null) {
				props.load(inputStream);
			} else {
				LOGGER.info(EELFLoggerDelegate.applicationLogger,"DBProxy : inputstream is not");
			}
			String dbCreate = UserUtils.htmlEscape(props.getProperty("db.create"));
			System.out.println( dbCreate );
			if( dbCreate!=null && dbCreate.equals( "true")) {
				schemaDAO.initializeDatabase();
			}
		} catch (Exception e) {
			e.printStackTrace();
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"onApplicationEvent : Error details : "+ e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"onApplicationEvent : Error details : "+ e.getMessage());
		}
		return;
	}
}
