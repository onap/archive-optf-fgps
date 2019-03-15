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
package org.onap.fgps.api.annotation;

import static java.lang.annotation.ElementType.METHOD;
import static java.lang.annotation.RetentionPolicy.RUNTIME;

import java.lang.annotation.Retention;
import java.lang.annotation.Target;

@Retention(RUNTIME)
@Target(METHOD)
public @interface PropertyBasedAuthorization {
	/** 
	 *  Annotates a method whose authorization requirements are defined in a property file.
	 *  
	 *  The auth.properties file should contain one or more lines for each method annotated with this annotation.
	 *  If the annotation value is "x", auth.properties should contain either "x.aaf" or "x.basic".
	 *  If "x.aaf" is present, the user will be authenticated using AAF and authorized if they have the role which is value of x.aaf.
	 *    (See also @AafRoleRequired .)
	 *  If "x.basic" is present, with a value of "y", the user will be authorized using Basicauth with username of "y.name" and (encrypted) password of "y.pass".
	 *    (See also @BasicAuthRequired .)
	 *
	 * If AAF authentication is used, auth.properties must contain valet.aaf.name and valet.aaf.pass, which contains this application's
	 * AAF credentials.
	 * 
	 */
	String value();
}
