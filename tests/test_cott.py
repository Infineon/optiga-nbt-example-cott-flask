# SPDX-FileCopyrightText: 2024 Infineon Technologies AG
# SPDX-License-Identifier: MIT

"""
Test cases for :mod:`cott` library.
"""

import pytest

import cott


def test_uid() -> None:
    """
    Tests that :class:`cott.UID7` allows syntactically valid UID values.
    """
    created = cott.UID7(bytes.fromhex("00010203040506"))
    assert created == bytes.fromhex("00010203040506")


@pytest.mark.parametrize("uid", [
    "",
    "000102030405",
    "0001020304050607"
])
def test_uid_invalid(uid: str | bytes) -> None:
    """
    Tests that :class:`cott.UID7` detects syntactically invalid UIDs.
    """
    uid = uid if isinstance(uid, bytes) else bytes.fromhex(uid)
    with pytest.raises(ValueError):
        cott.UID7(uid)


def test_mac() -> None:
    """
    Tests that :class:`cott.MAC` allows syntactically valid AES CMAC values.
    """
    created = cott.MAC(bytes.fromhex("000102030405060708090a0b0c0d0e0f"))
    assert created == bytes.fromhex("000102030405060708090a0b0c0d0e0f")


@pytest.mark.parametrize("mac", [
    "",
    "000102030405060708090a0b0c0d0e",
    "000102030405060708090a0b0c0d0e0f10"
])
def test_mac_invalid(mac: str | bytes) -> None:
    """
    Tests that :class:`cott.MAC` detects syntactically invalid AES CMAC values.
    """
    mac = mac if isinstance(mac, bytes) else bytes.fromhex(mac)
    with pytest.raises(ValueError):
        cott.MAC(mac)


@pytest.mark.parametrize("key", [
    "000102030405060708090a0b0c0d0e0f"
])
def test_key(key: str | bytes) -> None:
    """
    Tests that :class:`cott.Key` allows syntactically valid AES keys.
    """
    key = key if isinstance(key, bytes) else bytes.fromhex(key)
    created = cott.Key(key)
    assert created == key


@pytest.mark.parametrize("key", [
    "",
    "000102030405060708090a0b0c0d0e",
    "000102030405060708090a0b0c0d0e0f10"
])
def test_key_invalid(key: str | bytes) -> None:
    """
    Tests that :class:`cott.Key` detects syntactically invalid AES keys.
    """
    key = key if isinstance(key, bytes) else bytes.fromhex(key)
    with pytest.raises(ValueError):
        cott.Key(key)


def test_cott() -> None:
    """
    Tests that :class:`cott.COTT` correctly stores parameters to members.
    """
    created = cott.COTT(bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20"))
    assert created.header == bytes.fromhex("0001")
    assert created.uid == bytes.fromhex("02030405060708")
    assert created.random == bytes.fromhex("090a0b0c0d0e0f10")
    assert created.mac == bytes.fromhex("1112131415161718191a1b1c1d1e1f20")


@pytest.mark.parametrize(["header", "uid", "random", "mac"], [
    [b"", bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20")],
    [b"\x00", bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20")],
    [bytes.fromhex("0001"), bytes.fromhex("020304050607"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20")],
    [bytes.fromhex("0001"), bytes.fromhex("0203040506070809"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20")],
    [bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20")],
    [bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f1011"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20")],
    [bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f")],
    [bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f2021")],
])
def test_cott_invalid(header: str | bytes, uid: str | bytes, random: str | bytes, mac: str | bytes) -> None:
    """
    Tests that :class:`cott.COTT` detects syntactically invalid COTT information.
    """
    header = header if isinstance(header, bytes) else bytes.fromhex(header)
    uid = uid if isinstance(uid, bytes) else bytes.fromhex(uid)
    random = random if isinstance(random, bytes) else bytes.fromhex(random)
    mac = mac if isinstance(mac, bytes) else bytes.fromhex(mac)
    with pytest.raises(ValueError):
        cott.COTT(header, uid, random, mac)


def test_cott_dissemble() -> None:
    """
    Tests that :meth:`cott.COTT.dissemble` correctly parses COTT data.
    """
    dissembled = cott.COTT.dissemble(bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20"))
    assert dissembled.header == bytes.fromhex("0001")
    assert dissembled.uid == bytes.fromhex("02030405060708")
    assert dissembled.random == bytes.fromhex("090a0b0c0d0e0f10")
    assert dissembled.mac == bytes.fromhex("1112131415161718191a1b1c1d1e1f20")


@pytest.mark.parametrize("assembled", [
    "",
    "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f",
    "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f2021"
])
def test_cott_dissemble_invalid(assembled: str | bytes) -> None:
    """
    Tests that :meth:`cott.COTT.dissemble` detects syntactically invalid COTT data.
    """
    assembled = assembled if isinstance(assembled, bytes) else bytes.fromhex(assembled)
    with pytest.raises(ValueError):
        cott.COTT.dissemble(assembled)


def test_cott_decode() -> None:
    """
    Tests that :meth:`cott.COTT.decode` correctly parses COTT data.
    """
    decoded = cott.COTT.decode(b"AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8g")
    assert decoded.header == bytes.fromhex("0001")
    assert decoded.uid == bytes.fromhex("02030405060708")
    assert decoded.random == bytes.fromhex("090a0b0c0d0e0f10")
    assert decoded.mac == bytes.fromhex("1112131415161718191a1b1c1d1e1f20")


@pytest.mark.parametrize("encoded", [
    b"A",
    b"AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8=",
    b"AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gIQ=="
])
def test_cott_decode_invalid(encoded: str | bytes) -> None:
    """
    Tests that :meth:`cott.COTT.decode` detects syntactically invalid COTT data.
    """
    encoded = encoded if isinstance(encoded, bytes) else bytes.fromhex(encoded)
    with pytest.raises(ValueError):
        cott.COTT.decode(encoded)


def test_cott_assemble() -> None:
    """
    Tests that :meth:`cott.COTT.assemble` correctly assembles COTT data.
    """
    created = cott.COTT(bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20"))
    assembled = created.assemble()
    assert assembled == bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20")


def test_cott_encode() -> None:
    """
    Tests that :meth:`cott.COTT.test_cott_encode` correctly encodes COTT data.
    """
    created = cott.COTT(bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20"))
    encoded = created.encode()
    assert encoded == b"AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8g"


def test_cott_verify() -> None:
    """
    Tests that :meth:`cott.COTT.verify` can detect authenticity of COTT by checking AES CMAC.
    """
    created = cott.COTT(bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("dbab59423fbec5a7be32c48ce1a80e33"))
    assert created.verify(bytes.fromhex("000102030405060708090a0b0c0d0e0f"))


def test_cott_verify_wrong_key() -> None:
    """
    Tests that :meth:`cott.COTT.verify` can detect authenticity of COTT by checking AES CMAC.
    """
    created = cott.COTT(bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("dbab59423fbec5a7be32c48ce1a80e33"))
    assert not created.verify(bytes.fromhex("000102030405060708090a0b0c0d0eff"))


@pytest.mark.parametrize(["first", "second"], [
    [cott.COTT(bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20")),
     cott.COTT(bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20"))],
    [cott.COTT(bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20")),
     bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20")],
    [bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20"),
     cott.COTT(bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20"))]
])
def test_cott_eq(first: cott.COTT | bytes, second: cott.COTT | bytes) -> None:
    """
    Tests that :meth:`cott.COTT.__eq__` can detect equivalent COTT values.
    """
    assert first == second


@pytest.mark.parametrize(["first", "second"], [
    [cott.COTT(bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20")),
     cott.COTT(bytes.fromhex("FF01"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20"))],
    [cott.COTT(bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20")),
     bytes.fromhex("FF0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20")],
    [bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20"),
     cott.COTT(bytes.fromhex("FF01"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("1112131415161718191a1b1c1d1e1f20"))],
])
def test_cott_neq(first: cott.COTT | bytes, second: cott.COTT | bytes) -> None:
    """
    Tests that :meth:`cott.COTT.__eq__` can detect different COTT values.
    """
    assert first != second
