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

import java.security.Provider;
import java.security.SecureRandom;
import java.security.Security;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

import org.apache.commons.codec.binary.Base64;
import org.apache.commons.lang.ArrayUtils;
import org.onap.fgps.api.exception.CipherUtilException;
import org.onap.fgps.api.logging.EELFLoggerDelegate;

public class CipherUtil {

	private static final EELFLoggerDelegate LOGGER = EELFLoggerDelegate.getLogger(CipherUtil.class);

	/**
	 * Default key.
	 */
	private static final String keyString = KeyProperties.getProperty("cipher.enc.key");

	private static final String ALGORITHM = "AES";
	private static final String ALGORYTHM_DETAILS = ALGORITHM + "/CBC/PKCS5PADDING";
	private static final int BLOCK_SIZE = 128;
	@SuppressWarnings("unused")
	private static SecretKeySpec secretKeySpec;
	private static IvParameterSpec ivspec;

	/**
	 * Encrypts the text using a secret key.
	 * 
	 * @param plainText
	 *            Text to encrypt
	 * @return Encrypted Text
	 * @throws CipherUtilException
	 *             if any decryption step fails
	 */
	public static String encryptPKC(String plainText) throws CipherUtilException {
		return CipherUtil.encryptPKC(plainText, keyString);
	}

	private static SecretKeySpec getSecretKeySpec() {
		byte[] key = Base64.decodeBase64(keyString);
		return new SecretKeySpec(key, ALGORITHM);
	}

	private static SecretKeySpec getSecretKeySpec(String keyString) {
		byte[] key = Base64.decodeBase64(keyString);
		return new SecretKeySpec(key, ALGORITHM);
	}

	/**
	 * Encrypt the text using the secret key in key.properties file
	 * 
	 * @param value
	 * @return The encrypted string
	 * @throws BadPaddingException
	 * @throws CipherUtilException
	 *             In case of issue with the encryption
	 */
	public static String encryptPKC(String value, String skey) throws CipherUtilException {
		Cipher cipher = null;
		byte[] iv = null, finalByte = null;

		try {
			cipher = Cipher.getInstance(ALGORYTHM_DETAILS, "SunJCE");

			SecureRandom r = SecureRandom.getInstance("SHA1PRNG");
			iv = new byte[BLOCK_SIZE / 8];
			r.nextBytes(iv);
			ivspec = new IvParameterSpec(iv);
			cipher.init(Cipher.ENCRYPT_MODE, getSecretKeySpec(skey), ivspec);
			finalByte = cipher.doFinal(value.getBytes());

		} catch (Exception ex) {
			LOGGER.error(EELFLoggerDelegate.errorLogger,"encrypt failed", ex);
			throw new CipherUtilException(ex);
		}
		return Base64.encodeBase64String(ArrayUtils.addAll(iv, finalByte));
	}

	/**
	 * Decrypts the text using the secret key in key.properties file.
	 * 
	 * @param message
	 *            The encrypted string that must be decrypted using the ecomp
	 *            Encryption Key
	 * @return The String decrypted
	 * @throws CipherUtilException
	 *             if any decryption step fails
	 */
	public static String decryptPKC(String message, String skey) throws CipherUtilException {
		byte[] encryptedMessage = Base64.decodeBase64(message);
		Cipher cipher;
		byte[] decrypted = null;
		try {
			cipher = Cipher.getInstance(ALGORYTHM_DETAILS, "SunJCE");
			ivspec = new IvParameterSpec(ArrayUtils.subarray(encryptedMessage, 0, BLOCK_SIZE / 8));
			byte[] realData = ArrayUtils.subarray(encryptedMessage, BLOCK_SIZE / 8, encryptedMessage.length);
			cipher.init(Cipher.DECRYPT_MODE, getSecretKeySpec(skey), ivspec);
			decrypted = cipher.doFinal(realData);

		} catch (Exception ex) {
			LOGGER.error(EELFLoggerDelegate.errorLogger,"decrypt failed", ex);
			throw new CipherUtilException(ex);
		}

		return new String(decrypted);
	}

	/**
	 * 
	 * Decrypts the text using the secret key in key.properties file.
	 * 
	 * @param encryptedText
	 *            Text to decrypt
	 * @return Decrypted text
	 * @throws CipherUtilException
	 *             if any decryption step fails
	 */
	public static String decryptPKC(String encryptedText) throws CipherUtilException {
		return CipherUtil.decryptPKC(encryptedText, keyString);
	}

	public static void maine(String[] args) throws CipherUtilException {
		String testValue = "vmNKzC1wHH7w8PiZf7iPTTwq4iaAJn3dRlVK1YLvwgFESCqNPj3azGvRgNpR8tx+2p+o346C9PMip8SJyle/rw==";
		String encrypted;

		String decrypted;

		encrypted=encryptPKC(testValue);
		System.out.println("encrypted"+encrypted);
		
		decrypted=decryptPKC(testValue);
		System.out.println("decrypted"+ decrypted);

	}

	public static void main (String[] args) {
		Provider[] pa = Security.getProviders();
		for (Provider p : pa) {
			System.out.println("Provider: " + p + ", " + p.getInfo() );
		}

		/*
		String encoded = "vmNKzC1wHH7w8PiZf7iPTTwq4iaAJn3dRlVK1YLvwgFESCqNPj3azGvRgNpR8tx+2p+o346C9PMip8SJyle/rw==";
		String decoded = decryptPKC(encoded);
		String reencoded = encryptPKC(decoded);
		System.out.println(encoded);
		System.out.println(decoded);
		System.out.println(reencoded);
		*/
		
		String plainText = "Jackdaws love my big sphinx of quartz.";
		String encoded = encryptPKC(plainText);
		String decoded = decryptPKC(encoded);
		System.out.println(plainText);
		System.out.println(encoded);
		System.out.println(decoded);
		
	}
	
	public static String encodeBasicAuth(String userId, String password) {

		String plainCreds = userId + ":" + password;
		byte[] plainCredsBytes = plainCreds.getBytes();
		byte[] base64CredsBytes = Base64.encodeBase64(plainCredsBytes);
		String base64Creds = new String(base64CredsBytes);
		
		return "Basic " +base64Creds;
	}

}
