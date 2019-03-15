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
package org.onap.fgps.api.service;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Set;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import org.onap.fgps.api.beans.schema.Schema;
import org.onap.fgps.api.dao.ValetServicePlacementDAO;
import org.onap.fgps.api.logging.EELFLoggerDelegate;
import org.onap.fgps.api.utils.Constants;
import org.onap.fgps.api.utils.YamlToJsonConverter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

@Service
public class ValetPlacementService {
	String[] requiredFields = {"region_id","keystone_url","tenant_id","service_instance_id","vnf_id","vnf_name","vf_module_id","vf_module_name"};
	private ValetServicePlacementDAO valetServicePlacementDAO;
	private Schema schema;
	private static final EELFLoggerDelegate LOGGER = EELFLoggerDelegate.getLogger(ValetPlacementService.class);
	

	@Autowired
	public ValetPlacementService(ValetServicePlacementDAO valetServicePlacementDAO, Schema schema) {
		super();
		this.valetServicePlacementDAO = valetServicePlacementDAO;
		this.schema = schema;
	}
	
	private boolean isBlankArray(Object object) {
		if (object instanceof ArrayList == false) {
			return false;
		}else {
			ArrayList ja = (ArrayList)object;
			for(int i = 0; i < ja.size(); i ++) {
				if (!"".equals(ja.get(i).toString())) {
					return false;
				}
			}
			return true;
		}
	}

	public Object getParam(String key, JSONObject envParams, JSONObject parentProperties, LinkedHashMap requestParameters, String rootKey,Integer paramIndex) {
		if ("flavor".equals(key)) {
			System.out.println("");
		}
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"getParam : {}", key);
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"envParams : {}", envParams);
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"parentProperties : {}", parentProperties);
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"requestParameters : {}", requestParameters);
		if (rootKey.equals(Constants.HEAT_REQUEST_VALET_HOST_ASSIGNMENT)) {
			return key;
		} 
		else if (parentProperties != null && parentProperties.get(key) != null && !"".equals(parentProperties.get(key))) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"Found in parent properties : {}", parentProperties.get(key));
			if (parentProperties.get(key) instanceof JSONObject && ((JSONObject)parentProperties.get(key)).containsKey("get_param") && ((JSONObject)parentProperties.get(key)).get("get_param").equals(key)) {
				return getParam(key, envParams, null, requestParameters, rootKey,paramIndex);
			}
			if (paramIndex!=null && paramIndex>=0) {
				JSONArray toRet = (JSONArray)(parentProperties.get(key));
				return toRet.get(paramIndex);
			}
			return parentProperties.get(key);
		}else if (requestParameters != null && requestParameters.get(key) != null && !"".equals(requestParameters.get(key)) && !isBlankArray(requestParameters.get(key))) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"Found in request params : {}", requestParameters.get(key));
			if (paramIndex!=null && paramIndex>=0) {
				List toRet = (List)requestParameters.get(key);
				return toRet.get(paramIndex);
			}
			return requestParameters.get(key);	
		}else if (envParams != null && envParams.get(key) != null && !"".equals(envParams.get(key))) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"Found in environment params : {}", envParams.get(key));
			if (paramIndex!=null && paramIndex>=0) {
				JSONArray toRet = (JSONArray)(envParams.get(key));
				return toRet.get(paramIndex);
			}
			return envParams.get(key);
		} else if (rootKey.equals(Constants.HEAT_REQUEST_AZ)) {
			return "None";
		} 
		/*commented as part of code merge start
		else {
			if (rootKey.equals(Constants.HEAT_REQUEST_AZ)) {
				return "None";
			}else if(rootKey.equals(Constants.HEAT_REQUEST_VALET_HOST_ASSIGNMENT)) {
				return key;
			}
		} commented as part of code merge end*/
		/*else { if (parentProperties.containsKey(Constants.HEAT_RESOURCE_PROPERTIES)) {//	Sometimes there may be a inner properties which contains the key
			return getParam(key, (JSONObject)parentProperties.get(Constants.HEAT_RESOURCE_PROPERTIES), envParams, requestParameters, rootKey);
		} else if (!rootKey.equals(Constants.HEAT_REQUEST_AZ) && !rootKey.equals(Constants.HEAT_REQUEST_VALET_HOST_ASSIGNMENT) && (envParams == null || envParams.get(key) == null || ((String) envParams.get(key)).length() == 0)) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"Taking from  requestParameters : {}", requestParameters.get(key));
			return requestParameters.get(key);
		}
		if (rootKey.equals(Constants.HEAT_REQUEST_AZ) && (envParams.get(key) == null || "".equals(envParams.get(key).toString().trim()))) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"sending None");
			return "None";
		}else if(rootKey.equals(Constants.HEAT_REQUEST_VALET_HOST_ASSIGNMENT) && (envParams.get(key) == null || "".equals(envParams.get(key).toString().trim()))) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"sending same key : {}", key);
			return key;
		}
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"sending from envparams : {}", envParams.get(key));
		return envParams.get(key);*/
		return null;
	}
	public Object getParam(String key, JSONObject envParams, JSONObject parentProperties, LinkedHashMap requestParameters, String rootKey) {
		return getParam(key, envParams, parentProperties, requestParameters, rootKey, null);
	}
	
	public Object getParam(String key, JSONObject envParams,JSONObject parentProperties,  LinkedHashMap requestParameters) {
		if ("names".equals(key)) {
			System.out.println("");
		}
		return getParam(key, envParams, parentProperties, requestParameters, key);
	}

	public Object getAttr(JSONArray key, JSONObject resources, int index) {
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"key : {}", key);
		for (int resourcesListIndex = resourcesList.size() -1 ; resourcesListIndex >= 0; resourcesListIndex --) {
			Object obj = getAttr((String)key.get(index), resourcesList.get(resourcesListIndex));
			if (obj != null) {
				JSONArray arr = new JSONArray();
				arr.add(obj);
				arr.add((String)key.get(1));
				return arr;
			}
		}
		return null;
	}

	public Object getAttr(String key, JSONObject resources) {
		if (resources != null) {
			return resources.get(key);
		}
		return null;
	}
	private int resourceIndex = -1;
	@SuppressWarnings({ "rawtypes", "unchecked", "unused" })
	public JSONObject parseResourceObject(JSONObject parent, JSONObject returnObject, JSONObject resourceObject,
			JSONObject envParams, LinkedHashMap files, JSONObject parentProperties, LinkedHashMap requestParameters) {
		if (returnObject == null) {
			returnObject = new JSONObject();
		}
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"resourceObject : {}", resourceObject);
		JSONObject properties = (JSONObject) resourceObject.get(Constants.HEAT_RESOURCE_PROPERTIES);
		String resourceType = (String) resourceObject.get("type");
		JSONObject propertiesTemp = new JSONObject();
		if (resourceType != null && (resourceType.equals(Constants.OS_HEAT_RESOURCEGROUP) || resourceType.equals(Constants.OS_NOVA_SERVERGROUP_ROOT)) && properties.containsKey("resource_def")) {
			//	Check for a yaml file
			JSONObject resourceDef = (JSONObject)properties.get("resource_def");
			if (resourceDef != null && resourceDef.containsKey("type") && resourceDef.get("type").toString().endsWith(".yaml")) {
				//	Get the count
				String count = "1";
				if (properties.get("count") != null) {
					if (properties.get("count") instanceof String) {
						count = properties.get("count").toString();
					}else {
						Object countObj = getParam(((JSONObject)properties.get("count")).get("get_param").toString(), envParams, parentProperties, requestParameters);
						if (countObj instanceof String) {
							count = (String)countObj;
						}else if(countObj instanceof Integer) {
							count = ((Integer)countObj).toString();
						}
						if (count == null) {
							count = "1";
						}
					}
				}
				LOGGER.info(EELFLoggerDelegate.applicationLogger,"count : {}", count);
				for (resourceIndex = 0; resourceIndex < Integer.parseInt(count); resourceIndex ++) {
					//	Get the file
					String nestedYamlFile = (String) files.get(resourceDef.get("type").toString());
					//LOGGER.info(EELFLoggerDelegate.applicationLogger,"nestedYamlFile : {}", nestedYamlFile);
					JSONObject resourceProperties = processProperties(
							(JSONObject) resourceDef.get(Constants.HEAT_RESOURCE_PROPERTIES), parentProperties, parent,
							envParams, requestParameters);
					JSONObject nestedYamlJSON = null;
					try {
						if (nestedYamlFile != null) {
							LOGGER.info(EELFLoggerDelegate.applicationLogger,"nestedYamlFile : {}", nestedYamlFile);
							nestedYamlJSON = processTemplate(convertToJson(nestedYamlFile), files, envParams,
									resourceProperties, requestParameters);
							LOGGER.info(EELFLoggerDelegate.applicationLogger,"nestedYamlJSON : {}", nestedYamlJSON);
							String resourceName = nestedYamlJSON.keySet().toArray()[0].toString();
							JSONObject obj = (JSONObject)nestedYamlJSON.get(resourceName);
							JSONObject objReturn = new JSONObject();
							Set<String> objKeys = ((JSONObject)obj.get("properties")).keySet();
							for(String objKey : objKeys) {
								if (!Constants.HEAT_REQUEST_NAMES.equals(objKey) && 
										!Constants.HEAT_REQUEST_FLAVOR.equals(objKey) && !Constants.HEAT_REQUEST_IMAGE.equals(objKey) && !Constants.HEAT_REQUEST_METADATA.equals(objKey) && !Constants.HEAT_REQUEST_AVAILABILITY_ZONE.equals(objKey) && !Constants.HEAT_REQUEST_SCHEDULER_HINTS.equals(objKey)){
									
								}else {
									objReturn.put(objKey, ((JSONObject)obj.get(Constants.HEAT_REQUEST_PROPERTIES)).get(objKey));
								}
							}
							obj.put(Constants.HEAT_REQUEST_PROPERTIES , objReturn);
							returnObject.put(resourceName + "_" + resourceIndex, obj);
						}
					} catch (Exception e) {
						e.printStackTrace();
						LOGGER.error(EELFLoggerDelegate.applicationLogger," : parseResourceObject : Error details : "+ e.getMessage());
						LOGGER.error(EELFLoggerDelegate.errorLogger," : parseResourceObject : Error details : "+ e.getMessage());
					}
					resourceObject.put(Constants.HEAT_RESOURCE_PROPERTIES, resourceProperties);
					resourceObject.put("type", nestedYamlJSON);
				}
			}
			//	NO YAML file, no processing
			return returnObject;
		} else if (resourceType != null && resourceType.toString().endsWith(".yaml")) {
			//	Generally comes in availability zone
			//	Get the template
			JSONObject nestedYaml = convertToJson(files.get(resourceType.toString()).toString());
			return nestedYaml;
		} else {

			if (properties != null) {
				Set<String> propertiesKeySet = properties.keySet();
				for (String propertiesKey : propertiesKeySet) {
					Long get_param_count = (long) 1;
					if (propertiesKey.equals(Constants.HEAT_REQUEST_KEYSTONE_NETWORKS)) {
						continue;
					}
					if (propertiesKey.equals(Constants.HEAT_REQUEST_PROPERTIES_COUNT)) {
						JSONObject count = (JSONObject) properties.get(propertiesKey);
						String countParameter = (String) count.get("get_param");
						get_param_count = Long.parseLong(getParam(countParameter,envParams, null, requestParameters).toString());
						propertiesTemp.put(propertiesKey, get_param_count);

					} else if (propertiesKey.equals(Constants.HEAT_REQUEST_RESOURCES_DEF)) {
						JSONObject resource_def = (JSONObject) properties.get(propertiesKey);
						String nestedTemplateName = (String) resource_def.get(Constants.HEAT_REQUEST_RESOURCES_TYPE);
						JSONObject nestedYaml = null;

						JSONObject resourceProperties = processProperties(
								(JSONObject) resource_def.get(Constants.HEAT_RESOURCE_PROPERTIES), parentProperties,
								parent, envParams, requestParameters);

						if (nestedTemplateName != null) {
							if (files.get(nestedTemplateName) != null) {
								nestedYaml = processTemplate(convertToJson((String) files.get(nestedTemplateName)),
										files, envParams, resourceProperties, requestParameters);
							}
						}
						resource_def.put(Constants.HEAT_REQUEST_RESOURCES_TYPE, nestedYaml);
						resource_def.put(Constants.HEAT_RESOURCE_PROPERTIES, resourceProperties);
						propertiesTemp.put(propertiesKey, resource_def);
						resourceObject.put(Constants.HEAT_RESOURCE_PROPERTIES, propertiesTemp);

					} else if (propertiesKey.equals(Constants.HEAT_REQUEST_AVAILABILITY_ZONE)) {
						JSONObject azJSON = (JSONObject)properties.get(propertiesKey);
						if (azJSON.get("get_param") != null) {
							propertiesTemp.put(propertiesKey, getParam((String)azJSON.get("get_param"), envParams, parentProperties, requestParameters,Constants.HEAT_REQUEST_AZ));
						}else {
							JSONObject str_replace = (JSONObject)azJSON.get("str_replace");
							LOGGER.info(EELFLoggerDelegate.applicationLogger,"str_replace : {}", str_replace);
							JSONObject params = (JSONObject)str_replace.get("params");
							JSONObject az = (JSONObject)params.get(Constants.HEAT_REQUEST_AZ);
							Object az_value = null;
							if (az.containsKey("get_param")) {
								if (az.get("get_param") instanceof String) {
									az_value = getParam(az.get("get_param").toString(), envParams, parentProperties, requestParameters,Constants.HEAT_REQUEST_AZ);
								}else {
									//	It can be a JSONArray
									JSONArray az_getparam_array = (JSONArray)az.get("get_param");
									JSONArray az_resources = (JSONArray)getParam(az_getparam_array.get(0).toString(), envParams, parentProperties, requestParameters,Constants.HEAT_REQUEST_AZ, ((Long)az_getparam_array.get(1)).intValue());
									JSONObject az_resource = (JSONObject)az_resources.get(0);
									JSONObject nestedYaml = parseResourceObject(parent, returnObject, az_resource, envParams, files, parentProperties, requestParameters);
									JSONObject outputs = (JSONObject)nestedYaml.get("outputs");	
									JSONObject requiredJSON = (JSONObject)outputs.get(az_resources.get(1).toString());
									JSONArray values = (JSONArray)requiredJSON.get("value");
									JSONObject valueJSON = (JSONObject)values.get(resourceIndex);
									if (valueJSON.containsKey("get_param")) {
										az_value = getParam(valueJSON.get("get_param").toString(), envParams, null, requestParameters,Constants.HEAT_REQUEST_AZ);
									}else {
										az_value = valueJSON.toString();
									}
								}
							}
							JSONObject valet_host_assignment = (JSONObject)params.get(Constants.HEAT_REQUEST_VALET_HOST_ASSIGNMENT);
							Object valet_host_assignment_value = null;
							Object valet_host_assignment_second_arg = null;
							if (valet_host_assignment != null && valet_host_assignment.containsKey("get_param")) {
								//	This can be either a string OR an array
								if (valet_host_assignment.get("get_param") instanceof String) {
									valet_host_assignment_value = getParam(valet_host_assignment.get("get_param").toString(), envParams, parentProperties, requestParameters,Constants.HEAT_REQUEST_VALET_HOST_ASSIGNMENT);
								}else {
									//	Array
									JSONArray valet_host_assignment_arr = (JSONArray)valet_host_assignment.get("get_param");
									valet_host_assignment_value = getParam((String)valet_host_assignment_arr.get(0), envParams, parentProperties, requestParameters,Constants.HEAT_REQUEST_VALET_HOST_ASSIGNMENT,((Long)valet_host_assignment_arr.get(1)).intValue() );
									if (valet_host_assignment_arr.get(1) instanceof JSONObject) {
										JSONObject obj = (JSONObject)valet_host_assignment_arr.get(1);
										String val = obj.get("get_param").toString();
										if ("index".equals(val)) {
											valet_host_assignment_second_arg = String.valueOf(resourceIndex);
										}
									}else {
										valet_host_assignment_second_arg = valet_host_assignment_arr.get(1).toString();
									}
								}
							}
							//	Create JSONArray
							JSONArray arr = new JSONArray();
							arr.add(az_value);
							arr.add(valet_host_assignment_value);
							if (valet_host_assignment_second_arg != null) {
								arr.add(Integer.parseInt(valet_host_assignment_second_arg.toString()));
							}
							propertiesTemp.put(propertiesKey, arr);
						}
					} else if (propertiesKey.equals(Constants.HEAT_REQUEST_SCHEDULER_HINTS)) {
						//      scheduler_hints: { group: { get_resource: rdn_server_group } }
						JSONObject group = ((JSONObject)((JSONObject)properties.get(Constants.HEAT_REQUEST_SCHEDULER_HINTS)).get("group"));
						if (group.containsKey("get_resource")) {
							JSONObject resObj = new JSONObject();
							resObj.put(group.get("get_resource").toString(), parseResourceObject(parent, returnObject, (JSONObject)((JSONObject)parent.get("resources")).get(group.get("get_resource")), envParams, files, parentProperties, requestParameters));
							group.clear();
							group.put("group", resObj);
							propertiesTemp.put(propertiesKey, group);
						}else if (group.containsKey("get_param")) {
							JSONObject resObj = new JSONObject();
							//	Check if this exist in resources list
							boolean resourceFound = false;
							for (int resourcesListIndex = resourcesList.size() -1 ; resourcesListIndex >= 0; resourcesListIndex --) {
								if (resourcesList.get(resourcesListIndex).containsKey(group.get("get_param").toString())) {
									resourceFound = true;
									resObj.put(group.get("get_param").toString(), parseResourceObject(parent, returnObject, (JSONObject)resourcesList.get(resourcesListIndex).get(group.get("get_param")), envParams, files, parentProperties, requestParameters));
									group.clear();
									group.put("group", resObj);
									propertiesTemp.put(propertiesKey, group);
									break;
								}
							}
							if (!resourceFound) {
								resObj.put(group.get("get_param").toString(), getParam(group.get("get_param").toString(), envParams, parentProperties, requestParameters));
								group.clear();
								group.put("group", resObj);
								propertiesTemp.put(propertiesKey, group);
							}
						}else {
							JSONObject resObj = new JSONObject();
							resObj.put("group",  group);
							propertiesTemp.put(propertiesKey, resObj);
						}

					} else if (propertiesKey.equals(Constants.HEAT_REQUEST_METADATA)) {
						JSONObject metadata = (JSONObject)properties.get(propertiesKey);
						JSONObject metadataTemp = new JSONObject();
						boolean valetGroupsExist = false;
						
						for(Object key : metadata.keySet()) {
							if (!"valet_groups".equals(key)) {
								continue;
							}
							valetGroupsExist = true;
							String valet_groups = "";
							if (metadata.get(key) instanceof String) {
								valet_groups = metadata.get(key).toString();
							}else if (metadata.get(key) instanceof JSONArray) {
								/** Code to support array **/
								JSONArray valetGroupsArr = (JSONArray)metadata.get(key);
								for(int valetGroupIndex = 0; valetGroupIndex < valetGroupsArr.size(); valetGroupIndex ++) {
//									Get the key value
									if (valetGroupsArr.get(valetGroupIndex) instanceof String) {
										valet_groups += "," + valetGroupsArr.get(valetGroupIndex).toString();
										continue;
									}
									JSONObject keyValue = (JSONObject)valetGroupsArr.get(valetGroupIndex);
									//	If the value contains get_param key, call getParam
									if (keyValue.containsKey("get_param")) {
										valet_groups += "," + getParam((String)keyValue.get("get_param"), envParams, parentProperties, requestParameters).toString();
									}else {
									//	Else use the same key
										valet_groups += "," + keyValue.toJSONString();
									}
								}
								valet_groups = valet_groups.trim().substring(1);
							}else {
								//	Get the key value
								JSONObject keyValue = (JSONObject)metadata.get(key);
								//	If the value contains get_param key, call getParam
								if (keyValue.containsKey("get_param")) {
									valet_groups = getParam((String)keyValue.get("get_param"), envParams, parentProperties, requestParameters).toString();
								}else {
								//	Else use the same key
									valet_groups = keyValue.toJSONString();
								}
							}
							LOGGER.info(EELFLoggerDelegate.applicationLogger,"valet_groups : {}", valet_groups);
							valet_groups = valet_groups.replaceAll("\"\\s?,\\s?\"", ", ");
							LOGGER.info(EELFLoggerDelegate.applicationLogger,"valet_groups : {}", valet_groups);
							metadataTemp.put("valet_groups", valet_groups);
						}
						if (!valetGroupsExist) {
							//metadataTemp.put("valet_groups", "");
						}
						propertiesTemp.put(Constants.HEAT_REQUEST_METADATA, metadataTemp);
					}else {
						LOGGER.info(EELFLoggerDelegate.applicationLogger,"propertiesKey : {}", propertiesKey);
						if (properties.get(propertiesKey) instanceof JSONArray) {
							JSONArray property = (JSONArray) properties.get(propertiesKey);
							LOGGER.info(EELFLoggerDelegate.applicationLogger,"property.get(0) : {}", property.get(0));
							if (property.get(0) instanceof JSONObject) {
								propertiesTemp.put(propertiesKey, property);
							}else {
								String get_param = (String) property.get(0);
								if (get_param != null && "get_param".equals(get_param)) {
									propertiesTemp.put(propertiesKey,
											getParam(get_param, envParams, parentProperties, requestParameters));
								}else {
									propertiesTemp.put(propertiesKey, property);
								}
							}

						} else if (properties.get(propertiesKey) instanceof String) {
							propertiesTemp.put(propertiesKey, properties.get(propertiesKey));
						}  else if (properties.get(propertiesKey) instanceof ArrayList) {
							propertiesTemp.put(propertiesKey, ((ArrayList)properties.get(propertiesKey)).get(resourceIndex));
						}else {
							JSONObject property = (JSONObject) properties.get(propertiesKey);
							if (property != null) {
								String get_param = null;
								Integer param_index = null;
								if (property.get("get_param") instanceof JSONArray) {
									get_param = ((JSONArray)property.get("get_param")).get(0).toString();
									try {
										param_index = ((Long)((JSONArray)property.get("get_param")).get(1)).intValue();
									} catch (Exception e) {
										LOGGER.warn("Couldn't parse get_param index as in integer! " + property);
										param_index = null;
									}
								}else if (property.get("get_param") != null){
									get_param = (String) property.get("get_param");
								}
								JSONArray get_attr = (JSONArray) property.get("get_attr");
								JSONObject str_replace = (JSONObject) property.get("str_replace");
								String getResource = (String) property.get("get_resource");
								if (get_param != null) {
									if (resourceIndex == -1) {//	Base template
										propertiesTemp.put(propertiesKey,
												getParam(get_param, envParams, parentProperties, requestParameters,get_param, param_index));
									}else {//	Nested template.
										Object paramValue = getParam(get_param, envParams, parentProperties, requestParameters);
										if (paramValue instanceof String) {
											propertiesTemp.put(propertiesKey,
													paramValue);
										}else if (paramValue instanceof JSONArray) {
											JSONArray arr = (JSONArray)paramValue;
											propertiesTemp.put(propertiesKey,
													arr.get(resourceIndex));
										}else if (paramValue instanceof ArrayList) {
											ArrayList arr = (ArrayList)paramValue;
											propertiesTemp.put(propertiesKey,
													arr.get(resourceIndex));
										}else {
											propertiesTemp.put(propertiesKey,
													paramValue);
										}
									}
								}

								if (get_attr != null) {
									propertiesTemp.put(propertiesKey, getAttr(get_attr, parent, 0));
								}
								
								if (getResource != null) {
									propertiesTemp.put(propertiesKey, parent.get(getResource));
								}

								if (str_replace != null) {
									JSONObject str_replace_params = (JSONObject) str_replace.get("params");
									if ("name".equals(propertiesKey)) {
										//if (str_replace_params != null && str_replace_params.containsKey("$vnf_name")) {
										if (str_replace_params != null) {
											//Object vnf_name = str_replace_params.get("$vnf_name");
											Object vnf_name = str_replace_params.get(str_replace_params.keySet().toArray()[0]);
											if (vnf_name instanceof String) {
												propertiesTemp.put(propertiesKey, vnf_name);
											}else if (vnf_name instanceof JSONObject){
												JSONObject json_vnf_name = (JSONObject)vnf_name;
												if (json_vnf_name.containsKey("get_param")) {
													propertiesTemp.put(propertiesKey, getParam((String)json_vnf_name.get("get_param"), envParams, parentProperties, requestParameters));
												}
											}
										}
									}
									// propertiesTemp.put(propertiesKey, getAttr(str_replace, parent));
								}
							}
						}
						resourceObject.put(Constants.HEAT_RESOURCE_PROPERTIES, propertiesTemp);

					}

				}

			}
		}

		return resourceObject;
	}

	public JSONObject processProperties(JSONObject properties, JSONObject parentProperties, JSONObject parent,
			JSONObject parameters, LinkedHashMap requestParameters) {
		Set<String> propertiesKeySet = properties.keySet();
		JSONObject propertiesTemp = new JSONObject();

		for (String propertiesKey : propertiesKeySet) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"propertiesKey : {}", propertiesKey);
			if (properties.get(propertiesKey) instanceof String) {
				propertiesTemp.put(propertiesKey, properties.get(propertiesKey));

			} else if (properties.get(propertiesKey) instanceof JSONArray) {
				propertiesTemp.put(propertiesKey, properties.get(propertiesKey));

			} else if (properties.get(propertiesKey) instanceof Long) {
				propertiesTemp.put(propertiesKey, properties.get(propertiesKey));
			} else {
				JSONObject property = (JSONObject) properties.get(propertiesKey);
				JSONArray get_attr = (JSONArray) property.get("get_attr"), get_param_arr;
				JSONObject str_replace = (JSONObject) property.get("str_replace");
				String getResource = (String) property.get("get_resource");
				String get_param_str = "";
				if (property.get("get_param") instanceof String) {
					get_param_str = (String) property.get("get_param");
				} else {
					get_param_arr = (JSONArray) property.get("get_param");
				}

				if (get_param_str != null) {
					propertiesTemp.put(propertiesKey,
							getParam(get_param_str, parameters, parentProperties, requestParameters));
				}

				if (get_attr != null) {
					propertiesTemp.put(propertiesKey, getAttr(get_attr, (JSONObject)parent.get("resources"), 0));
				}

				if (getResource != null) {
					propertiesTemp.put(propertiesKey, parent.get(getResource));
				}
				if (str_replace != null) {
					// propertiesTemp.put(propertiesKey, str_replace(get_param,
					// parent));
				}
			}
		}
		return propertiesTemp;
	}
	List<JSONObject> resourcesList =  new ArrayList<>();
	@SuppressWarnings({ "unchecked", "rawtypes" })
	public JSONObject processTemplate(JSONObject template, LinkedHashMap files, JSONObject environment,
			JSONObject parentProperties, LinkedHashMap requestParameters) {
		JSONObject resources = (JSONObject) template.get(Constants.VALET_REQUEST_RESOURCES);
		resourcesList.add(resources);
		JSONObject returnObject = new JSONObject();
		Set<String> resourceKeySet = resources.keySet();
		for (String key : resourceKeySet) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"resource key : {}", key);
			JSONObject resourceObject = (JSONObject) resources.get(key);
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"resource resourceObject : {}", resourceObject);
			//	Consider only OS::Nova::Server resources
			if (!resourceObject.containsKey("type") || (!Constants.OS_NOVA_SERVER_ROOT.equals((String)resourceObject.get("type")) 
					&& !Constants.OS_NOVA_SERVERGROUP_ROOT.equals((String)resourceObject.get("type"))
					&& !Constants.OS_HEAT_RESOURCEGROUP.equals((String)resourceObject.get("type")))) {
				continue;
			}
			if (parentProperties == null && Constants.OS_NOVA_SERVERGROUP_ROOT.equals((String)resourceObject.get("type"))){
				continue;
			}
			JSONObject resourceProperties = (JSONObject) resourceObject.get(Constants.HEAT_RESOURCE_PROPERTIES);
			if (parentProperties != null) {
				//	Take parent properties into the nested template
				Set<Object> parentPropertyKeySet = parentProperties.keySet();
				for(Object parentProperty : parentPropertyKeySet) {
					if (!resourceProperties.containsKey(parentProperty)) {
						resourceProperties.put(parentProperty, parentProperties.get(parentProperty));
					}else {
						//	If resource property value is get param and the param value is a parent propery
						if (resourceProperties.get(parentProperty) instanceof JSONObject) {
							//	Check if it is get_param
							JSONObject jo = (JSONObject)resourceProperties.get(parentProperty);
							if (jo.containsKey("get_param") && jo.get("get_param").toString().equals(parentProperty)) {
								resourceProperties.put(parentProperty, parentProperties.get(parentProperty));
							}
						}
					}
				}
			}
			JSONObject envParams = (JSONObject) environment.get("parameters");

			
			if(key.equals("metadata")) {
				JSONObject metadata = (JSONObject) resources.get("metadata");
				if(metadata !=null) {
					resources.put("metadata", processProperties(
							metadata, parentProperties, resources,
							envParams, requestParameters));
				}
			}
			JSONObject resourceObj = parseResourceObject(template, null, resourceObject, envParams, files, resourceProperties,
					requestParameters);
			if (resourceObj.containsKey("type") && (Constants.OS_NOVA_SERVER_ROOT.equals((String)resourceObj.get("type")) 
					|| Constants.OS_NOVA_SERVERGROUP_ROOT.equals((String)resourceObj.get("type")) 
					|| Constants.OS_HEAT_RESOURCEGROUP.equals((String)resourceObj.get("type")))) {
				returnObject.put(key, resourceObj);
			}else {
				Set<String> resourceKeys = resourceObj.keySet();
				for(String resourceKey : resourceKeys) {
					if (resourceObj.get(resourceKey) instanceof JSONObject) {
						JSONObject obj = (JSONObject)resourceObj.get(resourceKey);
						if (obj.containsKey("type") && (Constants.OS_NOVA_SERVER_ROOT.equals((String)obj.get("type")) 
								|| Constants.OS_NOVA_SERVERGROUP_ROOT.equals((String)obj.get("type")) 
								|| Constants.OS_HEAT_RESOURCEGROUP.equals((String)obj.get("type")))) {
							returnObject.put(resourceKey, obj);
						}
					}else {
						break;
					}
				}
			}
		}
		if (resourcesList.size() > 1) {
			resourcesList.remove(resources);
		}
		return returnObject;
	}

	public JSONObject parseLogicFinal() {

		return null;
	}

	public ResponseEntity<String> processResponse(JSONObject response, LinkedHashMap requestParameters) {
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"response : "+response);
		JSONObject statusObj = null;
		String status = (String)response.get("status");
		statusObj = parseToJSON(status);
		status = (String) statusObj.get("status");
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"response : "+status);

		JSONObject statusObjReturn = new JSONObject();
		if (!"failed".equals(status)) {
			//if ("".equals(statusObj.get("message"))) {//Success
				//	Process the result object
				JSONObject result = null;
				try {
					result = (JSONObject)new JSONParser().parse((String)response.get("result"));
				} catch (ParseException e) {
					e.printStackTrace();
					LOGGER.error(EELFLoggerDelegate.applicationLogger,"processResponse : Error details : "+ e.getMessage());
                    LOGGER.error(EELFLoggerDelegate.errorLogger,"processResponse : Error details : "+ e.getMessage());
					return ResponseEntity.ok("Invalid response : " + response.toJSONString());
				}				
				Set<Object> resultKeys = result.keySet();
				JSONObject result_to_return = new JSONObject();
				for(Object resultKey : resultKeys) {
					requestParameters.put(resultKey, result.get(resultKey));
				}
				response.put("parameters", requestParameters);
				response.remove("timestamp");
				response.remove("result");
				response.remove("request_id");
				response.remove("status");
				JSONObject status_obj = new JSONObject();
				response.put("status", statusObj);
				return ResponseEntity.ok(response.toJSONString());
		//	}
		}
		JSONObject status_obj = new JSONObject();
		/*statusObjReturn.put("status", statusObj.get("status").toString());
		statusObjReturn.put("message", statusObj.get("message").toString());*/
		status_obj.put("status", statusObj);
		return ResponseEntity.ok(status_obj.toJSONString());
	}

	@SuppressWarnings("unchecked")
	public ResponseEntity<String> processMSORequest1(JSONObject request, String requestId , String operation) {
		try {
			ArrayList<String> missingfields = isValidateRequest(request);
			if(missingfields.size() >0) {
				return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY).body("RequiredFields : "+ missingfields.toString());
			}
			
			@SuppressWarnings("rawtypes")
			LinkedHashMap heat_request = (LinkedHashMap) request.get(Constants.HEAT_REQUEST);
			JSONObject template = convertToJson(heat_request.get(Constants.HEAT_REQUEST_TEMPLATE).toString());
			@SuppressWarnings("rawtypes")
			LinkedHashMap files = (LinkedHashMap) heat_request.get(Constants.HEAT_REQUEST_FILES);
			JSONObject environment = convertToJson(heat_request.get(Constants.HEAT_REQUEST_ENVIRONMENT).toString());
			LinkedHashMap requestParameters = (LinkedHashMap) heat_request.get(Constants.HEAT_REQUEST_PARAMETERS);
			if (requestParameters == null) {
				requestParameters = new LinkedHashMap();
			}
			JSONObject response = processTemplate(template, files, environment, null, requestParameters);
			return saveRequest(request, response, operation, requestId, requestParameters);
			//return response.toJSONString();
		} catch (Exception e) {
			e.printStackTrace();
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"processMSORequest1: Error details : "+ e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"processMSORequest1: Error details : "+ e.getMessage());
			return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
		}
	}
	
	//java junit test case purpose
	@SuppressWarnings("unchecked")
	public ResponseEntity<String> processMSORequest2(JSONObject request, String requestId) {
		try {
			LOGGER.debug(EELFLoggerDelegate.debugLogger,"in processMSORequest2");
			@SuppressWarnings("rawtypes")
			LinkedHashMap heat_request = (LinkedHashMap) request.get(Constants.HEAT_REQUEST);
			JSONObject template = convertToJson(heat_request.get(Constants.HEAT_REQUEST_TEMPLATE).toString());
			@SuppressWarnings("rawtypes")
			LinkedHashMap files = (LinkedHashMap) heat_request.get(Constants.HEAT_REQUEST_FILES);
			JSONObject environment = convertToJson(heat_request.get(Constants.HEAT_REQUEST_ENVIRONMENT).toString());
			LinkedHashMap requestParameters = (LinkedHashMap) heat_request.get(Constants.HEAT_REQUEST_PARAMETERS);
			if (requestParameters == null) {
				requestParameters = new LinkedHashMap();
			}
			JSONObject response = processTemplate(template, files, environment, null, requestParameters);
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"Result : {}", response.toJSONString());
			return saveRequest2(request, response, "create", requestId, requestParameters);
		} catch (Exception e) {
			e.printStackTrace();
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"processMSORequest2 : Error while processing MSO request for requestId : "+requestId+", Error details : "+ e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"processMSORequest2 : Error while processing MSO request for requestId : "+requestId+", Error details : "+ e.getMessage());
			return null;
		}
	}

	private ArrayList<String> isValidateRequest(JSONObject request) {
		// TODO Auto-generated method stub
		ArrayList<String> missingRequest = new ArrayList<>();
		int i=0;
		for(String field : requiredFields) {
			if(request.get(field)==null || (request.get(field) instanceof String && "".equals(request.get(field)) )) {
				missingRequest.add(field) ;
				i++;
			}		
		}
		return missingRequest;
	}

	public String processMSORequest(JSONObject request) {
		try {
			@SuppressWarnings("rawtypes")
			LinkedHashMap heat_request = (LinkedHashMap) request.get(Constants.HEAT_REQUEST);
			JSONObject template = convertToJson(heat_request.get(Constants.HEAT_REQUEST_TEMPLATE).toString());
			JSONObject resources = (JSONObject) template.get(Constants.VALET_REQUEST_RESOURCES);
			@SuppressWarnings("rawtypes")
			LinkedHashMap files = (LinkedHashMap) heat_request.get(Constants.HEAT_REQUEST_FILES);
			JSONObject environment = convertToJson(heat_request.get(Constants.HEAT_REQUEST_ENVIRONMENT).toString());
			JSONObject parameters = null;
			if (environment != null) {
				parameters = (JSONObject) environment.get("parameters");
			}
			LinkedHashMap requestParameters = (LinkedHashMap<?, ?>) heat_request.get("parameters");
			if (requestParameters == null) {
				requestParameters = new LinkedHashMap();
			}

			Set<String> resourceKeySet = resources.keySet();
			for (String key : resourceKeySet) {
				JSONObject resourceObject = (JSONObject) resources.get(key);
				JSONObject properties = (JSONObject) resourceObject.get(Constants.HEAT_RESOURCE_PROPERTIES);
				if (properties != null) {
					JSONObject resource_def = (JSONObject) properties.get(Constants.HEAT_REQUEST_RESOURCES_DEF);
					JSONObject count = (JSONObject) properties.get(Constants.HEAT_REQUEST_PROPERTIES_COUNT);
					Long get_param = (long) 1;
					if (count != null) {
						String countParameter = (String) count.get("get_param");
						get_param = (Long) parameters.get(countParameter);
					}
					if (resource_def != null) {
						String nestedTemplateName = (String) resource_def.get(Constants.HEAT_REQUEST_RESOURCES_TYPE);

						if (nestedTemplateName != null) {
							if (files.get(nestedTemplateName) != null) {
								JSONObject nestedYaml = convertToJson(files.get(nestedTemplateName).toString());
								JSONArray nestedArray = new JSONArray();
								System.out.println(get_param);
								for (int i = 0; i < get_param; i++) {
									nestedArray.add(nestedYaml);
								}
								resource_def.put(Constants.HEAT_REQUEST_RESOURCES_TYPE, nestedArray);
								properties.put(Constants.HEAT_REQUEST_RESOURCES_DEF, resource_def);
								resourceObject.put(Constants.HEAT_RESOURCE_PROPERTIES, properties);
								resources.put(key, resourceObject);
							}
						}
					}
				}
			}
			String region_id = (String) request.get(Constants.HEAT_REQUEST_REGION_ID);
			String keystone_url = (String) request.get(Constants.HEAT_REQUEST_KEYSTONE_ID);
			JSONObject datacenter = new JSONObject();

			if (region_id != null && keystone_url != null) {
				datacenter.put("id", region_id);
				datacenter.put("url", keystone_url);
			}
			request.put(Constants.HEAT_REQUEST_DATACENTER, datacenter);

			template.put(Constants.VALET_REQUEST_RESOURCES, resources);
			request.remove(Constants.HEAT_REQUEST);
			request.put(Constants.VALET_ENGINE_KEY, template);
			String dbRequest = schema.formMsoInsertUpdateRequest(null, "create", request.toJSONString());
			// return valetServicePlacementDAO.insertRow(dbRequest);
			return dbRequest;

		} catch (Exception e) {
			e.printStackTrace();
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"processMSORequest : Error details : "+ e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"processMSORequest : Error details : "+ e.getMessage());
			return "bad request";
		}
	}

	public JSONObject convertToJson(String data) {
		String jsonString = YamlToJsonConverter.convertToJson(data);
		JSONParser parser = new JSONParser();
		try {
			JSONObject json = (JSONObject) parser.parse(jsonString);
			return json;
		} catch (ParseException e) {
			e.printStackTrace();
			LOGGER.error(EELFLoggerDelegate.applicationLogger,"convertToJson : Error details : "+ e.getMessage());
			LOGGER.error(EELFLoggerDelegate.errorLogger,"convertToJson : Error details : "+ e.getMessage());
			return null;
		}
	}

	public static JSONObject parseToJSON(String jsonString) {
		JSONParser parser = new JSONParser();
		try {
			JSONObject json = (JSONObject) parser.parse(jsonString);
			return json;
		} catch (ParseException e) {
			e.printStackTrace();
			
			return null;
		}
	}

	public String processDeleteRequest(JSONObject request, String requestId) {
		String dbRequest = schema.formMsoInsertUpdateRequest(requestId, "delete", request.toJSONString());
		return valetServicePlacementDAO.insertRow(dbRequest);
	}
	
	
	
	public ResponseEntity<String> saveRequest(JSONObject request, JSONObject response, String operation, String requestId, LinkedHashMap requestParameters){
		JSONObject dataCenterObj = new JSONObject();
		dataCenterObj.put("id", request.get("region_id"));
		dataCenterObj.put("url", request.get("keystone_url"));
		JSONObject dbJSON = new JSONObject();
		dbJSON.put("datacenter", dataCenterObj);
    	dbJSON.put("tenant_id", request.get("tenant_id"));
    	dbJSON.put("service_instance_id", request.get("service_instance_id"));
    	dbJSON.put("vnf_instance_id", request.get("vnf_id"));
    	dbJSON.put("vnf_instance_name", request.get("vnf_name"));
    	dbJSON.put("vf_module_id", request.get("vf_module_id"));
    	dbJSON.put("vf_module_name", request.get("vf_module_name"));
		JSONObject resources= new JSONObject();
		resources.put("resources", response);
		dbJSON.put("stack", resources);    	
    	dbJSON.put("stack_name", ((LinkedHashMap)request.get("heat_request")).get("stack_name"));
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"dbJSON : {}", dbJSON);
		return saveCreateRequest(dbJSON, operation, requestId, requestParameters);
	}
	//java juint test case 
	public ResponseEntity<String> saveRequest2(JSONObject request, JSONObject response, String operation, String requestId, LinkedHashMap requestParameters){
		JSONObject dataCenterObj = new JSONObject();
		dataCenterObj.put("id", request.get("region_id"));
		dataCenterObj.put("url", request.get("keystone_url"));
		JSONObject dbJSON = new JSONObject();
		dbJSON.put("datacenter", dataCenterObj);
    	dbJSON.put("tenant_id", request.get("tenant_id"));
    	dbJSON.put("service_instance_id", request.get("service_instance_id"));
    	dbJSON.put("vnf_instance_id", request.get("vnf_id"));
    	dbJSON.put("vnf_instance_name", request.get("vnf_name"));
    	dbJSON.put("vf_module_id", request.get("vf_module_id"));
    	dbJSON.put("vf_module_name", request.get("vf_module_name"));
		JSONObject resources= new JSONObject();
		resources.put("resources", response);
		dbJSON.put("stack", resources);    	
    	dbJSON.put("stack_name", ((LinkedHashMap)request.get("heat_request")).get("stack_name"));
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"dbJSON : {}", dbJSON);
		return ResponseEntity.ok(dbJSON.toJSONString());
	}
	public ResponseEntity<String> saveCreateRequest(JSONObject request, String operation, String requestId, LinkedHashMap requestParameters) {
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"saveRequest : the request - ", requestId);
		String dbRequest = schema.formMsoInsertUpdateRequest(requestId, operation, request.toJSONString());
		String insertRow = valetServicePlacementDAO.insertRow(dbRequest);
		return pollForResult(request, operation + "-" + requestId, Constants.WAIT_UNITL_SECONDS,
				Constants.POLL_EVERY_SECONDS, requestParameters);

	}
//java test case request
	public ResponseEntity<String> saveRequesttest(JSONObject request, String operation, String requestId) {
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"saveRequest : the request - ", requestId);
		String dbRequest = schema.formMsoInsertUpdateRequest(requestId, operation, request.toJSONString());
		return ResponseEntity.ok(dbRequest);

	}

	
	public ResponseEntity<String> saveRequest(JSONObject request, String operation, String requestId) {
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"saveRequest : the request - ", requestId);
		String dbRequest = schema.formMsoInsertUpdateRequest(requestId, operation, request.toJSONString());
		String insertRow = valetServicePlacementDAO.insertRow(dbRequest);
		return pollForResult(request, operation + "-" + requestId, Constants.WAIT_UNITL_SECONDS,
				Constants.POLL_EVERY_SECONDS, null);

	}

	public ResponseEntity<String> pollForResult(JSONObject values, String requestId, int waitUntilSeconds,
			int pollEverySeconds, LinkedHashMap requestParameters) {
		LOGGER.info(EELFLoggerDelegate.applicationLogger,"pollForResult : called", requestId);

		String result = null;
		long waitUntil = System.currentTimeMillis() + (1000 * waitUntilSeconds);
		int counter = 1;

		JSONObject response = new JSONObject();
		boolean isTimedOut = false;
		while (true) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"pollForResult : polling database - ", counter++);

			result = valetServicePlacementDAO.getRowFromResults(requestId);
			System.out.println("getRowFromResults called count:" + counter);
			response = result != null ? parseToJSON(result) : null;

			if (response != null && ((JSONObject) response.get("result")).get("row 0") != null) {
				LOGGER.debug(EELFLoggerDelegate.debugLogger,"pollForResult : response recieved", result);
				System.out.println("deleteRowFromResults called");
				valetServicePlacementDAO.deleteRowFromResults(requestId, schema.formMsoDeleteRequest());

			}
			if (System.currentTimeMillis() < waitUntil && (response == null
					|| ((JSONObject) response.get("result")).get("row 0") == null)) {
				try {
					Thread.sleep(1000 * pollEverySeconds);
				} catch (InterruptedException e) {
					e.printStackTrace();
					LOGGER.error(EELFLoggerDelegate.applicationLogger,"pollForResult : Error while processing request with requestId : "+requestId+", Error details : "+ e.getMessage());
					LOGGER.error(EELFLoggerDelegate.errorLogger,"pollForResult : Error while processing request with requestId : "+requestId+", Error details : "+ e.getMessage());
				}
			} else {
				break;
			}
		}
		if (System.currentTimeMillis() > waitUntil) {
			return ResponseEntity.status(HttpStatus.GATEWAY_TIMEOUT).build();
		}
		if (requestParameters != null) {
			LOGGER.info(EELFLoggerDelegate.applicationLogger,"Result from DB : {}", ((JSONObject) ((JSONObject) response.get("result")).get("row 0")));
			return processResponse(((JSONObject) ((JSONObject) response.get("result")).get("row 0")), requestParameters);
		}else{
			//System.out.println("Response"+ ((JSONObject)((JSONObject) response.get("result")).get("row 0")).toJSONString());
			JSONObject obj = ((JSONObject)((JSONObject) response.get("result")).get("row 0"));
			/*obj.put("result",parseToJSON( (String) obj.get("result")));
			response.put("Status", parseToJSON(result));
			System.out.println("mso"+result);*/
			JSONObject res = new JSONObject();
			res.put("status",parseToJSON( (String) obj.get("status")));
			return ResponseEntity.ok(res.toJSONString());
		}
	}

}
