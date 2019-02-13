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
package org.onap.fgps.api.dao;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import org.json.simple.JSONObject;
import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.onap.fgps.api.proxy.DBProxy;
import org.onap.fgps.api.utils.Constants;
import org.onap.fgps.api.utils.Helper;
import org.onap.fgps.api.utils.MusicDBConstants;
import org.springframework.stereotype.Component;
import org.onap.fgps.api.utils.UserUtils;

@Component
public class ValetServicePlacementDAO {
	//private static final Logger LOGGER = LoggerFactory.getLogger(ValetServiceApplication.class);
	private static EELFLoggerDelegate LOGGER = EELFLoggerDelegate.getLogger(SchemaDAO.class);
	private String keySpace;
	private boolean pingLogFlag;
	
	public ValetServicePlacementDAO(boolean pingFlag) {
		this.pingLogFlag = pingFlag;
		Properties props = new Properties();
		String propFileName = "resources.properties";
		InputStream inputStream = getClass().getClassLoader().getResourceAsStream(propFileName);
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
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"ValetServicePlacementDAO : Error details : "+ e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"ValetServicePlacementDAO : Error details : "+ e.getMessage());
		}
		if(pingLogFlag) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"SchemaDAO : initializeDatabase called");
		}
		this.keySpace = UserUtils.htmlEscape(props.getProperty("music.Keyspace"));
	}

	public ValetServicePlacementDAO() {
		this(true);
	}

	public String insertRow(String request)  {
	    LOGGER.info(EELFLoggerDelegate.applicationLogger,"ValetServicePlacementDAO : insertRow : inserting the row");

		DBProxy dbProxy = new DBProxy();
		Object[] params = { this.keySpace, Constants.SERVICE_PLACEMENTS_REQUEST_TABLE };
		String url = Helper.getURI(MusicDBConstants.INSERT_ROWS, params);
		return dbProxy.post(url, request);
	}

	public String deleteRow(String request_id, String json) {
	    LOGGER.info(EELFLoggerDelegate.applicationLogger,"ValetServicePlacementDAO : deleteRow : deleting the row");
		DBProxy dbProxy = new DBProxy();
		Object[] params = { this.keySpace, Constants.SERVICE_PLACEMENTS_REQUEST_TABLE };
		String url = Helper.getURI(MusicDBConstants.INSERT_ROWS, params);
		return dbProxy.delete(url + "?request_id=" + request_id, json);
	}

	@SuppressWarnings("unchecked")
	public String updateRow(JSONObject values) {
	    LOGGER.info(EELFLoggerDelegate.applicationLogger,"ValetServicePlacementDAO : updateRow : update the row");

		JSONObject request = new JSONObject();
		JSONObject consistencyInfo = new JSONObject();
		consistencyInfo.put("type", "eventual");
		request.put("values", values);
		request.put("consistencyInfo", consistencyInfo);
		DBProxy dbProxy = new DBProxy();
		Object[] params = { this.keySpace, Constants.SERVICE_PLACEMENTS_REQUEST_TABLE };
		String url = Helper.getURI(MusicDBConstants.INSERT_ROWS, params);
		return dbProxy.put(url, request.toJSONString());
	}

	public String getRow(String request_id) {
		if(pingLogFlag) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"ValetServicePlacementDAO : getRow : geting the row");
		}

		DBProxy dbProxy = new DBProxy(pingLogFlag);
		Object[] params = { this.keySpace, Constants.SERVICE_PLACEMENTS_REQUEST_TABLE };
		String url = Helper.getURI(MusicDBConstants.INSERT_ROWS, params);
		return dbProxy.get(url + "?request_id=" + request_id);
	}

	public String getRowFromResults(String request_id) {
	    LOGGER.info(EELFLoggerDelegate.applicationLogger,"ValetServicePlacementDAO : getRowFromResults : geting the row");

		DBProxy dbProxy = new DBProxy();
		Object[] params = { this.keySpace, Constants.SERVICE_PLACEMENTS_RESULTS_TABLE };
		String url = Helper.getURI(MusicDBConstants.INSERT_ROWS, params);
		System.out.println(url + "?request_id=" + request_id);
		String result = dbProxy.get(url + "?request_id=" + request_id);
		System.out.println(result);
		return result;

	}

	public String deleteRowFromResults(String request_id, String request) {
	    LOGGER.info(EELFLoggerDelegate.applicationLogger,"ValetServicePlacementDAO : deleteRowFromResults : deleting the row");

		DBProxy dbProxy = new DBProxy();
		Object[] params = { this.keySpace, Constants.SERVICE_PLACEMENTS_RESULTS_TABLE };
		String url = Helper.getURI(MusicDBConstants.INSERT_ROWS, params);
		System.out.println(url + "?request_id=" + request_id);
		String result = dbProxy.delete(url + "?request_id=" + request_id, request);
		System.out.println(result);
		return result;
	}
}
