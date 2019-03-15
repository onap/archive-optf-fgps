#
# -------------------------------------------------------------------------
#   Copyright (c) 2019 AT&T Intellectual Property
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#
from base64 import b64decode
from Crypto.Cipher import AES
from hashlib import md5


UNPAD = lambda s: s[:-ord(s[len(s) - 1:])]


def decrypt(_k1, _k2, _k3, _pw):
    code_list = ['g', 'E', 't', 'a', 'W', 'i', 'Y', 'H', '2', 'L']

    code = int(_k1) + int(_k2) * int(_k3)
    str_code = str(code)

    key = ""
    for i in range(0, len(str_code)):
        c_code = code_list[int(str_code[i])]
        key += c_code

    enc_key = md5(key.encode('utf8')).hexdigest()

    enc = b64decode(_pw)
    iv = enc[:16]
    cipher = AES.new(enc_key, AES.MODE_CBC, iv)

    return UNPAD(cipher.decrypt(enc[16:])).decode('utf8')
