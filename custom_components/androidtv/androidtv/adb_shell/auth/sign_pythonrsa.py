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

"""ADB authentication using the ``rsa`` package.


.. rubric:: Contents

* :class:`_Accum`

    * :meth:`_Accum.digest`
    * :meth:`_Accum.update`

* :func:`_load_rsa_private_key`
* :class:`PythonRSASigner`

    * :meth:`PythonRSASigner.FromRSAKeyPath`
    * :meth:`PythonRSASigner.GetPublicKey`
    * :meth:`PythonRSASigner.Sign`

"""


from pyasn1.codec.der import decoder
from pyasn1.type import univ
import rsa
from rsa import pkcs1


class _Accum(object):
    """A fake hashing algorithm.

    The Python ``rsa`` lib hashes all messages it signs. ADB does it already, we just
    need to slap a signature on top of already hashed message.  Introduce a "fake"
    hashing algo for this.

    Attributes
    ----------
    _buf : bytes
        A buffer for storing data before it is signed

    """
    def __init__(self):
        self._buf = b''

    def update(self, msg):
        """Update this hash object's state with the provided ``msg``.

        Parameters
        ----------
        msg : bytes
            The message to be appended to ``self._buf``

        """
        self._buf += msg

    def digest(self):
        """Return the digest value as a string of binary data.

        Returns
        -------
        self._buf : bytes
            ``self._buf``

        """
        return self._buf


pkcs1.HASH_METHODS['SHA-1-PREHASHED'] = _Accum
pkcs1.HASH_ASN1['SHA-1-PREHASHED'] = pkcs1.HASH_ASN1['SHA-1']


def _load_rsa_private_key(pem):
    """PEM encoded PKCS#8 private key -> ``rsa.PrivateKey``.

    ADB uses private RSA keys in pkcs#8 format. The ``rsa`` library doesn't
    support them natively.  Do some ASN unwrapping to extract naked RSA key
    (in der-encoded form).

    See:

    * https://www.ietf.org/rfc/rfc2313.txt
    * http://superuser.com/a/606266

    Parameters
    ----------
    pem : str
        The private key to be loaded

    Returns
    -------
    rsa.key.PrivateKey
        The loaded private key

    """
    try:
        der = rsa.pem.load_pem(pem, 'PRIVATE KEY')
        keyinfo, _ = decoder.decode(der)

        if keyinfo[1][0] != univ.ObjectIdentifier('1.2.840.113549.1.1.1'):
            raise ValueError('Not a DER-encoded OpenSSL private RSA key')

        private_key_der = keyinfo[2].asOctets()

    except IndexError:
        raise ValueError('Not a DER-encoded OpenSSL private RSA key')

    return rsa.PrivateKey.load_pkcs1(private_key_der, format='DER')


class PythonRSASigner(object):
    """Implements :class:`adb_protocol.AuthSigner` using http://stuvel.eu/rsa.

    Parameters
    ----------
    pub : str, None
        The contents of the public key file
    priv : str, None
        The path to the private key

    Attributes
    ----------
    priv_key : rsa.key.PrivateKey
        The loaded private key
    pub_key : str, None
        The contents of the public key file

    """
    def __init__(self, pub=None, priv=None):
        self.priv_key = _load_rsa_private_key(priv)
        self.pub_key = pub

    @classmethod
    def FromRSAKeyPath(cls, rsa_key_path):
        """Create a :class:`PythonRSASigner` instance using the provided private key.

        Parameters
        ----------
        rsa_key_path : str
            The path to the private key; the public key must be ``rsa_key_path + '.pub'``.

        Returns
        -------
        PythonRSASigner
            A :class:`PythonRSASigner` with private key ``rsa_key_path`` and public key ``rsa_key_path + '.pub'``

        """
        with open(rsa_key_path + '.pub') as f:
            pub = f.read()
        with open(rsa_key_path) as f:
            priv = f.read()
        return cls(pub, priv)

    def Sign(self, data):
        """Signs given data using a private key.

        Parameters
        ----------
        data : bytes
            The data to be signed

        Returns
        -------
        bytes
            The signed ``data``

        """
        return rsa.sign(data, self.priv_key, 'SHA-1-PREHASHED')

    def GetPublicKey(self):
        """Returns the public key in PEM format without headers or newlines.

        Returns
        -------
        self.pub_key : str, None
            The contents of the public key file, or ``None`` if a public key was not provided.

        """
        return self.pub_key
