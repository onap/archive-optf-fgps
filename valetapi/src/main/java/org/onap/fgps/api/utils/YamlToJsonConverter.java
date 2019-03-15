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

import org.onap.fgps.api.logging.EELFLoggerDelegate;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;

public class YamlToJsonConverter {
	private static final EELFLoggerDelegate LOGGER = EELFLoggerDelegate.getLogger(YamlToJsonConverter.class);
	public static String convertToJson(String data) {
		ObjectMapper mapper = new ObjectMapper(new YAMLFactory());
		try {
			Object obj = mapper.readValue(data, Object.class);
			ObjectMapper jsonWriter = new ObjectMapper();
			return jsonWriter.writeValueAsString(obj);
		} catch (Exception e) {
			e.printStackTrace();
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"convertToJson : Error details : "+ e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"convertToJson : Error details : "+ e.getMessage());
		}
		return "";
	}
}
