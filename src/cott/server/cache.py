# SPDX-FileCopyrightText: 2024 Infineon Technologies AG
# SPDX-License-Identifier: MIT

"""
Example implementation of :class:`cott.ICache`.

Can be extended to support real implementation by previously used COTT values in a persistent database.
"""

__all__ = ["Cache"]

import typing

import cott
from cott.server.keystore import KeyStore


#: Example key store implementation
keystore: cott.IKeyStore = KeyStore()


class Cache(cott.ICache):
    """
    Simple memory-based implementation of :class:`cott.ICache` caching COTTs used since server started.

    In real implementation, this should be stored persistently in a secured database.
    """

    def __init__(self) -> None:
        super().__init__()
        self._cache: typing.Set[cott.COTT] = set()

    def used(self, instance: cott.COTT) -> bool:
        return instance in self._cache

    def use(self, instance: cott.COTT) -> None:
        self._cache.add(instance)
