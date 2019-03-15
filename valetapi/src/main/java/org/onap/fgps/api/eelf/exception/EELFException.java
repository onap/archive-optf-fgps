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
package org.onap.fgps.api.eelf.exception;

public class EELFException extends Exception {
	/**
     * The serial version number for this class
     */
    private static final long serialVersionUID = 1L;

    /**
     * Create the exception, detailing the reason with a message
     * 
     * @param message
     *            The message that details the reason for the exception
     */
    public EELFException(String message) {
        super(message);
    }

    /**
     * Create an exception by wrapping another exception
     * 
     * @param message
     *            The message that details the exception
     * @param cause
     *            Any exception that was caught and was the reason for this failure
     */
    public EELFException(String message, Throwable cause) {
        super(message, cause);
    }

    /**
     * Create the exception by wrapping another exception
     * 
     * @param cause
     *            The cause of this exception
     */
    public EELFException(Throwable cause) {
        super(cause);
    }

}
