# SPDX-FileCopyrightText: 2024 Infineon Technologies AG
# SPDX-License-Identifier: MIT

"""
OPTIGA (tm) Authenticate NBT Cryptographic One-Time Token utilities.
"""

from __future__ import annotations

__all__ = ["COTT", "IKeyStore", "ICache"]

import base64
import typing

import Crypto.Hash.CMAC
import Crypto.Cipher.AES


class UID7(bytes):
    """
    Custom parameter validator for 7 byte NFC UID.
    """

    def __new__(cls, value: bytes) -> UID7:
        """
        Custom parameter validation for 7 byte NFC UID.

        :param value: Binary UID to be validated.
        :raises ValueError: If syntactically invalid UID given.
        """
        if len(value) != 7:
            raise ValueError(f"Invalid 7 byte NFC UID, must be 7 bytes long (is {len(value)})")
        return super().__new__(cls, value)


class MAC(bytes):
    """
    Custom parameter validator for a 16 byte AES CMAC.
    """

    def __new__(cls, value: bytes) -> MAC:
        """
        Custom parameter validator for a 16 byte AES CMAC.

        :param value: Binary MAC to be validated.
        :raises ValueError: If syntactically invalid MAC given.
        """
        if len(value) != 16:
            raise ValueError(f"Invalid AES-CMAC, must be 16 bytes long (is {len(value)})")
        return super().__new__(cls, value)


class Key(bytes):
    """
    Custom parameter validator for an AES key.

    Currently only 128-bit keys supported.
    """

    def __new__(cls, value: bytes) -> Key:
        """
        Custom parameter validator for an AES key.

        Currently only 128-bit keys supported.

        :param value: AES key to be validated.
        :raises ValueError: If syntactically invalid AES key given.
        """
        if len(value) != 16:
            raise ValueError(f"Invalid AES key, currently only 128 bit key supported (has {len(value) * 8})")
        return super().__new__(cls, value)


def _generate_cmac(data: bytes, key: Key) -> MAC:
    """
    Generates AES CMAC over given data.

    :param data: Data to generate AES CMAC over.
    :param key: AES key to use for CMAC generation.
    :returns: Generated CMAC over given data.
    """
    maccer = Crypto.Hash.CMAC.new(key, ciphermod=Crypto.Cipher.AES)
    maccer.update(data)
    return MAC(maccer.digest())


class COTT:
    """
    Cryptographic One-time Token abstraction.
    """

    def __init__(self, header: bytes, uid: UID7 | bytes, random: bytes, mac: MAC | bytes):
        """
        Constructor validates parameters and saves them to members.

        :param header: 2 byte header (`b"\x00\x01"` for the first generation T4Tplus applet).
        :param uid: 7 byte NFC UID.
        :param random: 8 byte random data.
        :param mac: 16 byte MAC over data.
        :raises ValueError: If syntactically invalid data given.
        """
        if len(header) != 2:
            raise ValueError(f"Invalid COTT header, must be 2 bytes long (is {len(header)})")
        if len(random) != 8:
            raise ValueError(f"Invalid COTT random data, must be 8 bytes long (is {len(random)})")
        self._header: bytes = header
        self._uid: UID7 = UID7(uid)
        self._random: bytes = random
        self._mac: MAC = MAC(mac)

    @classmethod
    def dissemble(cls, assembled: bytes) -> COTT:
        """
        Dissembles binary COTT data (NOT Base64 encoded) to :class:`COTT` object.

        COTT data is only checked for syntax, to verify COTT was created by a trusted device, use :meth:`COTT.verify`.

        :param assembled: Binary COTT data to be dissembled (NOT Base64 encoded).
        :returns: Dissembled COTT object.
        :raises ValueError: If COTT data syntactically invalid.
        :see: :meth:`COTT.decode`
        """
        if len(assembled) != 33:
            raise ValueError(f"Invalid COTT, must be 33 bytes long (is {len(assembled)})")
        return cls(assembled[0:2], assembled[2:9], assembled[9:17], assembled[17:])

    @classmethod
    def decode(cls, encoded: bytes | str) -> COTT:
        """
        Decodes Base64 encoded COTT data to :class:`COTT` object.

        COTT data is only checked for syntax, to verify COTT was created by a trusted device, use :meth:`COTT.verify`.

        :param encoded: Base64 encoded COTT data to be decoded.
        :returns: Decoded COTT object.
        :raises ValueError: If COTT data syntactically invalid.
        """
        return cls.dissemble(base64.urlsafe_b64decode(encoded))

    def assemble(self) -> bytes:
        """
        Assembles COTT data to binary representation (without Base64 encoding).

        :returns: Assembled COTT data.
        :see: :meth:`COTT.encode`
        """
        return self.header + self.uid + self.random + self.mac

    def encode(self) -> bytes:
        """
        Encodes COTT data to Base64 encoded binary representation.

        :returns: Encoded COTT data.
        """
        return base64.urlsafe_b64encode(self.assemble())

    def verify(self, key: Key | bytes) -> bool:
        """
        Verifies COTT by checking that its MAC was created using the given key.

        To handle mapping from UID to matching AES key, use :class:`IKeyStore`.

        Does not check if COTT has been used before, but this can be checked via :class:`ICache`.

        :param key: AES key to be used for MAC verification.
        :returns: `True` if COTT's MAC was created using given key, otherwise `False`.
        """
        mac = _generate_cmac(self.header + self.uid + self._random, Key(key))
        return mac == self.mac

    @property
    def header(self) -> bytes:
        """
        2 byte header (`b"\x00\x01"` for the first generation T4Tplus applet).
        """
        return self._header

    @property
    def uid(self) -> UID7:
        """
        7 byte NFC UID.
        """
        return self._uid

    @property
    def random(self) -> bytes:
        """
        8 byte random data.
        """
        return self._random

    @property
    def mac(self) -> MAC:
        """
        16 byte AES CMAC over data.
        """
        return self._mac

    def __eq__(self, other: object) -> bool:
        if isinstance(other, COTT):
            return self.header == other.header and self.uid == other.uid and self.random == other.random and self.mac == other.mac
        if isinstance(other, bytes):
            return self.assemble() == other
        return NotImplemented  # pragma: no cover

    def __hash__(self) -> int:
        return hash(self.assemble())


class IKeyStore(typing.Protocol):
    """
    Interface for a key store mapping :class:`UID7` to AES keys.
    """

    def get(self, uid: UID7 | bytes) -> typing.Optional[Key]:
        """
        Returns AES key for given :class:`UID7`.

        :param uid: 7 byte UID to get AES key for.
        :returns: AES key for given UID or `None` if no key found.
        """

    def set(self, uid: UID7 | bytes, key: Key | bytes) -> None:
        """
        Sets AES key to be used for given :class:`UID7`.

        :param uid: 7 byte UID to set AES key for.
        :param key: AES key to be used for UID.
        """


class ICache(typing.Protocol):
    """
    Interface for a :class:`COTT` cache, storing previously used COTT to prevent replay attacks.
    """

    def used(self, instance: COTT) -> bool:
        """
        Checks if given :class:`COTT` has been previously used.

        :param instance: COTT to be checked if previously used.
        :returns: `True` if COTT has been used before, otherwise `False`.
        """

    def use(self, instance: COTT) -> None:
        """
        Marks given :class:`COTT` as used.

        :param instance: COTT to be marked as used.
        """
