"""
 # Copyright (c) 08 2016 | suryakencana
 # 8/14/16 nanang.ask@kubuskotak.com
 #  security
"""
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

backend = default_backend()

"""
    baka.secret_key = 'ryofly'
    baka.secret_session_key = 'ryofly.session'
    baka.salt = 'ryofly.security'
"""


def derive_key(key_material, salt, info, algorithm=None, length=None):
    if algorithm is None:
        algorithm = hashes.SHA512()
    if length is None:
        length = algorithm.digest_size
    hkdf = HKDF(algorithm, length, salt, info, backend)
    return hkdf.derive(key_material)
