# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""ADB authentication using ``pycryptodome``.


.. rubric:: Contents

* :class:`PycryptodomeAuthSigner`

    * :meth:`PycryptodomeAuthSigner.GetPublicKey`
    * :meth:`PycryptodomeAuthSigner.Sign`

"""

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


class PycryptodomeAuthSigner(object):
    """AuthSigner using the pycryptodome package.

    Parameters
    ----------
    rsa_key_path : str, None
        The path to the private key

    Attributes
    ----------
    public_key : str
        The contents of the public key file
    rsa_key : Crypto.PublicKey.RSA.RsaKey
        The contents of theprivate key

    """
    def __init__(self, rsa_key_path=None):
        super(PycryptodomeAuthSigner, self).__init__()

        if rsa_key_path:
            with open(rsa_key_path + '.pub', 'rb') as rsa_pub_file:
                self.public_key = rsa_pub_file.read()

            with open(rsa_key_path, 'rb') as rsa_priv_file:
                self.rsa_key = RSA.import_key(rsa_priv_file.read())

    def Sign(self, data):
        """Signs given data using a private key.

        Parameters
        ----------
        data : bytes, bytearray
            The data to be signed

        Returns
        -------
        bytes
            The signed ``data``

        """
        h = SHA256.new(data)
        return pkcs1_15.new(self.rsa_key).sign(h)

    def GetPublicKey(self):
        """Returns the public key in PEM format without headers or newlines.

        Returns
        -------
        self.public_key : str
            The contents of the public key file

        """
        return self.public_key
