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
package org.onap.fgps.api.eelf.i18n;

public enum EELFMsgs implements EELFResolvableErrorEnum {

	 /**
     * Loading default logging configuration from system resource file "{0}"
     */
	LOADING_DEFAULT_LOG_CONFIGURATION,

	 /**
     * No log configuration could be found or defaulted!
     */
    NO_LOG_CONFIGURATION,
    
    /**
     * Logging has already been initialized, check the container logging definitions to ensure they represent your
     * desired logging configuration.
     */
    LOGGING_ALREADY_INITIALIZED,
    
    /**
     * Searching path "{0}" for log configuration file "{1}"
     */
    SEARCHING_LOG_CONFIGURATION,
    
    /**
     * Loading logging configuration from file "{0}"
     */
    LOADING_LOG_CONFIGURATION,
    
  
    /**
     * An unsupported logging framework is bound to SLF4J. 
     */
    UNSUPPORTED_LOGGING_FRAMEWORK;
    
	
	
    /**
     * Static initializer to ensure the resource bundles for this class are loaded...
     */
    static {
        EELFResourceManager.loadMessageBundle("org/onap/eelf/Resources");
   }
    

      
}
