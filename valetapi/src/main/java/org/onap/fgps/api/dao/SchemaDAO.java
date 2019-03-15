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
import java.text.MessageFormat;
import java.util.Properties;

import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import org.onap.fgps.api.beans.schema.Schema;
import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.onap.fgps.api.proxy.DBProxy;
import org.onap.fgps.api.utils.Constants;
import org.onap.fgps.api.utils.DBInitializationRequests;
import org.onap.fgps.api.utils.MusicDBConstants;
import org.springframework.stereotype.Component;
import org.onap.fgps.api.utils.UserUtils;

@Component
public class SchemaDAO {
	private static EELFLoggerDelegate LOGGER = EELFLoggerDelegate.getLogger(SchemaDAO.class);
	InputStream inputStream;

	public String initializeDatabase() {
		Properties props = new Properties();
		String propFileName = "resources.properties";
		InputStream inputStream = getClass().getClassLoader().getResourceAsStream(propFileName);
		try {
			if (inputStream != null) {
				props.load(inputStream);
			} else {
				LOGGER.info(EELFLoggerDelegate.applicationLogger,"DBProxy : inputstream is not");
			}
		} catch (IOException e) {
		    e.printStackTrace();
		    LOGGER.error(EELFLoggerDelegate.applicationLogger,"initializeDatabase : Error while loading "+propFileName+", Error details : "+ e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"initializeDatabase : Error while loading "+propFileName+", Error details : "+ e.getMessage());
		}
	    LOGGER.info(EELFLoggerDelegate.applicationLogger,"SchemaDAO : initializeDatabase called");

	    String keyspace = UserUtils.htmlEscape(props.getProperty("music.Keyspace"));
	    LOGGER.info(EELFLoggerDelegate.applicationLogger, "keyspace: " + keyspace);
	    if (keyspace!=null && keyspace.length()>0 && !keyspace.equalsIgnoreCase("false")) {
	    	String dataCenterList = UserUtils.htmlEscape(props.getProperty("music.keyspace.data.centers"));
	    	if (dataCenterList==null || dataCenterList.length()==0) {
	    		// If music.keyspace.data.centers is not specified, use old behavior: data.center.one, .two, and .three get initialized with replication factor 3
	    		createKeySpace(keyspace, UserUtils.htmlEscape(props.getProperty("data.center.one")), UserUtils.htmlEscape(props.getProperty("data.center.two")), UserUtils.htmlEscape(props.getProperty("data.center.three")) );
	    	} else {
	    		// If music.keyspace.data.centers is specified, it must be a pipe separated list, and music.keyspace.replication.factor must be an integer which is the replication factor
	    		int replicationFactor = Integer.parseInt(props.getProperty("music.keyspace.replication.factor"));
	    		createKeyspaceWithReplicationFactor(keyspace, dataCenterList, replicationFactor);
	    	}
	    }
	    
		createTable(keyspace, Constants.SERVICE_PLACEMENTS_REQUEST_TABLE, Schema.getRequestTableSchema());
		createTable(keyspace, Constants.TABLE_RESULT, Schema.getResultsTableSchema());
		createTable(keyspace, Constants.TABLE_GROUP_RULES, Schema.getGroupsRulesTableSchema());
		createTable(keyspace, Constants.TABLE_STACKS, Schema.getStacksTableSchema());
		createTable(keyspace, Constants.TABLE_STACKS_ID_MAP, Schema.getStacksIdMapTableSchema());
		createTable(keyspace, Constants.TABLE_RESOURCES, Schema.getResourcesTableSchema());
		createTable(keyspace, Constants.TABLE_REGIONS, Schema.getRegionsTableSchema());
		createTable(keyspace, Constants.TABLE_Groups, Schema.getGroupsTableSchema());


		System.out.println("Tables created");
		return "";
	}

	/**
	 * 
	 * @param keyspace - music.Keyspace - name of the music keyspace
	 * @param dataCenterList - music.keyspace.data.centers - pipe separated list of data center names, e.g., "DC1|DC2|DC3|DC4"
	 * @param replicationFactor - music.keyspace.replication.factor - replication factor for each keyspace 
	 * @return a String representing the response from Music, or an error string if it fails
	 */
	private String createKeyspaceWithReplicationFactor(String keyspace, String dataCenterList, int replicationFactor) {
		LOGGER.info(EELFLoggerDelegate.applicationLogger, "SchemaDAO.createKeyspaceWithReplicationFactor");
		MessageFormat uri = new MessageFormat(MusicDBConstants.CREATE_KEYSPACE);

		Object data[] = { keyspace };
		String keyUrl = uri.format(data);
		DBProxy dbProxy = new DBProxy();

		String targetString = DBInitializationRequests.KEYSPACE_WITH_RF;
		StringBuffer sb = new StringBuffer();
		String sep = "";
		java.util.StringTokenizer st = new java.util.StringTokenizer(dataCenterList, "|");
		while (st.hasMoreTokens()) {
			String token = st.nextToken();
			sb.append(sep + "\"" + token + "\":" + replicationFactor);
			sep = ",";
		}
		targetString = targetString.replaceAll("DATA_CENTER_INFO", sb.toString());

		LOGGER.info(EELFLoggerDelegate.applicationLogger, "keyspace string = " + targetString);
		return dbProxy.post(keyUrl, targetString);
	}

	/**
	 * 
	 * @param keySpaceName
	 * @param DC1  Data Center Name
	 * @param DC2  Data Center Name
	 * @param DC3  Data Center Name
	 * @return
	 */
	public String createKeySpace(String keySpaceName,String DC1,String DC2,String DC3) {
	    LOGGER.info(EELFLoggerDelegate.applicationLogger,"SchemaDAO : createKeySpace called");	
		MessageFormat uri = new MessageFormat(MusicDBConstants.CREATE_KEYSPACE);
		JSONParser parser = new JSONParser();
		JSONObject jsonRequest = null;
		try {
			jsonRequest = (JSONObject) parser.parse(DBInitializationRequests.KEYSPACE_REQUEST);
			Object data[] = { keySpaceName };
			String keyUrl = uri.format(data);
			DBProxy dbProxy = new DBProxy();
			System.out.println(jsonRequest.toJSONString().replace("DC1", DC1).replace("DC2", DC2).replace("DC3", DC3));
			return dbProxy.post(keyUrl, jsonRequest.toJSONString().replace("DC1", DC1).replace("DC2", DC2).replace("DC3", DC3));
		} catch (ParseException e) {
			e.printStackTrace();
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"createKeySpace : Error details : "+ e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"createKeySpace : Error details : "+ e.getMessage());
			return "Error parsing the request.Refer logs for more insight";
		}
	}

	public String createTable(String keySpaceName, String tableName, String jsonRequest) {
	    LOGGER.info(EELFLoggerDelegate.applicationLogger,"SchemaDAO : createTable called");

		MessageFormat uri = new MessageFormat(MusicDBConstants.CREATE_TABLE);
		Object data[] = { keySpaceName, tableName };

		DBProxy dbProxy = new DBProxy();
		System.out.println(jsonRequest);
		System.out.println(uri.format(data));

		return dbProxy.post(uri.format(data), jsonRequest);
	}
}
