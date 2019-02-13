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

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface AafRoleRequired {
	/** 
	 * Annotates a method to indicate that AAF authorization is required to execute.  
	 * 
	 * If AAF authentication is used, auth.properties must contain valet.aaf.name and valet.aaf.pass, which contains this application's
	 * AAF credentials.
	 * 
	 * See also @PropertyBasedAuthorization.
	 */
	
	/**
	 * Marks the role required in AAF.
	 * For example, @AafRoleRequired(roleRequired="portal.admin") will check AAF for the "portal.admin" role.
	 */
	String roleRequired() default "";
	
	/**
	 * If roleRequired is null or blank, marks the property in auth.properties which contains the role required by AAF.
	 * The property in auth.properties must end with ".role".  The property specified in the annotation may omit that suffix.
	 * 
	 * For example, if auth.properties contains "portal.admin.role=portal.admin", then either @AafRoleRequired(roleProperty="portal.admin.role")
	 * or @AafRoleRequired(roleProperty="portal.admin") will check AAF for the "portal.admin" role.
	 * 
	 * If a roleProperty is specified in an AafRoleRequired annotation and the corresponding role (with or without ".role") is not 
	 * present in auth.properties, a MissingRoleException will be thrown.
	 */
	String roleProperty() default "";
}
