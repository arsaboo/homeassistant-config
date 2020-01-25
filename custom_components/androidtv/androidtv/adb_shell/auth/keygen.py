# Copyright (c) 2020 Jeff Irion and contributors
#
# This file is part of the adb-shell package.  It was originally written by
# @joeleong, and it was obtained from: https://github.com/google/python-adb/pull/144

"""This file implements encoding and decoding logic for Android's custom RSA
public key binary format. Public keys are stored as a sequence of
little-endian 32 bit words. Note that Android only supports little-endian
processors, so we don't do any byte order conversions when parsing the binary
struct.

Structure from:
https://github.com/aosp-mirror/platform_system_core/blob/c55fab4a59cfa461857c6a61d8a0f1ae4591900c/libcrypto_utils/android_pubkey.c

.. code-block:: c

   typedef struct RSAPublicKey {
       // Modulus length. This must be ANDROID_PUBKEY_MODULUS_SIZE_WORDS
       uint32_t modulus_size_words;

       // Precomputed montgomery parameter: -1 / n[0] mod 2^32
       uint32_t n0inv;

       // RSA modulus as a little-endian array
       uint8_t modulus[ANDROID_PUBKEY_MODULUS_SIZE];

       // Montgomery parameter R^2 as a little-endian array of little-endian words
       uint8_t rr[ANDROID_PUBKEY_MODULUS_SIZE];

       // RSA modulus: 3 or 65537
       uint32_t exponent;
   } RSAPublicKey;


.. rubric:: Contents

* :func:`_to_bytes`
* :func:`decode_pubkey`
* :func:`decode_pubkey_file`
* :func:`encode_pubkey`
* :func:`get_user_info`
* :func:`keygen`
* :func:`write_public_keyfile`

"""


import os
import base64
import logging
import socket
import struct
import sys

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


_LOGGER = logging.getLogger(__name__)

if sys.version_info[0] == 2:  # pragma: no cover
    FileNotFoundError = IOError  # pylint: disable=redefined-builtin


#: Size of an RSA modulus such as an encrypted block or a signature.
ANDROID_PUBKEY_MODULUS_SIZE = (2048 // 8)

#: Python representation of "struct RSAPublicKey"
ANDROID_RSAPUBLICKEY_STRUCT = (
    '<'                 # Little-endian
    'L'                 # uint32_t modulus_size_words;
    'L'                 # uint32_t n0inv;
    '{modulus_size}s'   # uint8_t modulus[ANDROID_PUBKEY_MODULUS_SIZE];
    '{modulus_size}s'   # uint8_t rr[ANDROID_PUBKEY_MODULUS_SIZE];
    'L'                 # uint32_t exponent;
).format(modulus_size=ANDROID_PUBKEY_MODULUS_SIZE)


#: Size of the RSA modulus in words.
ANDROID_PUBKEY_MODULUS_SIZE_WORDS = (ANDROID_PUBKEY_MODULUS_SIZE // 4)


def _to_bytes(n, length, endianess='big'):
    """Partial python2 compatibility with int.to_bytes

    https://stackoverflow.com/a/20793663

    Parameters
    ----------
    n : TODO
        TODO
    length : TODO
        TODO
    endianess : str, TODO
        TODO

    Returns
    -------
    TODO
        TODO

    """
    if not hasattr(n, 'to_bytes'):
        h = '{:x}'.format(n)
        s = ('0' * (len(h) % 2) + h).zfill(length * 2).decode('hex')
        return s if endianess == 'big' else s[::-1]
    return n.to_bytes(length, endianess)


def decode_pubkey(public_key):
    """Decode a public RSA key stored in Android's custom binary format.

    Parameters
    ----------
    public_key : TODO
        TODO

    """
    binary_key_data = base64.b64decode(public_key)
    modulus_size_words, n0inv, modulus_bytes, rr_bytes, exponent = struct.unpack(ANDROID_RSAPUBLICKEY_STRUCT, binary_key_data)
    assert modulus_size_words == ANDROID_PUBKEY_MODULUS_SIZE_WORDS
    modulus = reversed(modulus_bytes)
    rr = reversed(rr_bytes)
    _LOGGER.debug('modulus_size_words: %s', hex(modulus_size_words))
    _LOGGER.debug('n0inv: %s', hex(n0inv))
    _LOGGER.debug('modulus: %s', ':'.join((hex(m) for m in modulus)))
    _LOGGER.debug('rr: %s', ':'.join((hex(r) for r in rr)))
    _LOGGER.debug('exponent: %s', hex(exponent))


def decode_pubkey_file(public_key_path):
    """TODO

    Parameters
    ----------
    public_key_path : str
        TODO

    """
    with open(public_key_path, 'rb') as fd:
        decode_pubkey(fd.read())


def encode_pubkey(private_key_path):
    """Encodes a public RSA key into Android's custom binary format.

    Parameters
    ----------
    private_key_path : str
        TODO

    Returns
    -------
    TODO
        TODO

    """
    with open(private_key_path, 'rb') as key_file:
        key = serialization.load_pem_private_key(key_file.read(), password=None, backend=default_backend()).private_numbers().public_numbers

    # Compute and store n0inv = -1 / N[0] mod 2^32.
    # BN_set_bit(r32, 32)
    r32 = 1 << 32
    # BN_mod(n0inv, key->n, r32, ctx)
    n0inv = key.n % r32
    # BN_mod_inverse(n0inv, n0inv, r32, ctx)
    n0inv = rsa._modinv(n0inv, r32)  # pylint: disable=protected-access
    # BN_sub(n0inv, r32, n0inv)
    n0inv = r32 - n0inv

    # Compute and store rr = (2^(rsa_size)) ^ 2 mod N.
    # BN_set_bit(rr, ANDROID_PUBKEY_MODULUS_SIZE * 8)
    rr = 1 << (ANDROID_PUBKEY_MODULUS_SIZE * 8)
    # BN_mod_sqr(rr, rr, key->n, ctx)
    rr = (rr ** 2) % key.n

    return struct.pack(
        ANDROID_RSAPUBLICKEY_STRUCT,
        ANDROID_PUBKEY_MODULUS_SIZE_WORDS,
        n0inv,
        _to_bytes(key.n, ANDROID_PUBKEY_MODULUS_SIZE, 'little'),
        _to_bytes(rr, ANDROID_PUBKEY_MODULUS_SIZE, 'little'),
        key.e
    )


def get_user_info():
    """TODO

    Returns
    -------
    str
        ``' <username>@<hostname>``

    """
    try:
        username = os.getlogin()
    except (FileNotFoundError, OSError):
        username = 'unknown'

    if not username:
        username = 'unknown'

    hostname = socket.gethostname()
    if not hostname:
        hostname = 'unknown'

    return ' ' + username + '@' + hostname


def write_public_keyfile(private_key_path, public_key_path):
    """Write a public keyfile to ``public_key_path`` in Android's custom
    RSA public key format given a path to a private keyfile.

    Parameters
    ----------
    private_key_path : TODO
        TODO
    public_key_path : TODO
        TODO

    """
    public_key = encode_pubkey(private_key_path)
    assert len(public_key) == struct.calcsize(ANDROID_RSAPUBLICKEY_STRUCT)

    with open(public_key_path, 'wb') as public_key_file:
        public_key_file.write(base64.b64encode(public_key))
        public_key_file.write(get_user_info().encode())


def keygen(filepath):
    """Generate an ADB public/private key pair.

    * The private key is stored in ``filepath``.
    * The public key is stored in ``filepath + '.pub'``

    (Existing files will be overwritten.)

    Parameters
    ----------
    filepath : str
        File path to write the private/public keypair

    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    with open(filepath, 'wb') as private_key_file:
        private_key_file.write(private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()))

    write_public_keyfile(filepath, filepath + '.pub')
