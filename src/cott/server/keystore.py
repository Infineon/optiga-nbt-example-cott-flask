# SPDX-FileCopyrightText: 2024 Infineon Technologies AG
# SPDX-License-Identifier: MIT

"""
Example implementation of :class:`cott.IKeyStore`.

Can be extended to support real implementation by storing device specific AES keys in a secured database.
"""
__all__ = ["KeyStore"]

import collections
import typing

import cott


class KeyStore(cott.IKeyStore):
    """
    Simple implementation of :class:`cott.IKeyStore` providing default AES keys for OPTIGA (tm) Authenticate NBT Development Kits/Shields

    In real implementation, the AES keys should be stored on a per-device basis in a secured database.
    """

    def __init__(self) -> None:
        super().__init__()
        self._lookup: typing.Dict[cott.UID7, cott.Key] = collections.defaultdict(lambda: cott.Key(bytes.fromhex("373F5060409BA014B69A627622F23B59")))

    def get(self, uid: cott.UID7 | bytes) -> typing.Optional[cott.Key]:
        return self._lookup[cott.UID7(uid)]

    def set(self, uid: cott.UID7 | bytes, key: cott.Key | bytes) -> None:
        self._lookup[cott.UID7(uid)] = cott.Key(key)
