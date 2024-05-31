# SPDX-FileCopyrightText: 2024 Infineon Technologies AG
# SPDX-License-Identifier: MIT

# Disable "redefinition" warning as naming convention follows standard flask patterns
# pylint: disable=redefined-outer-name

"""
Test cases for :mod:`cott.server` flask server.
"""

import typing

import flask
import flask.testing
import pytest

import cott
import cott.server
import cott.server.cache
import cott.server.keystore


class KeyStore(cott.IKeyStore):
    """
    Test implementation of :class:`cott.IKeyStore` used for UID lookup testing.
    """

    def __init__(self) -> None:
        super().__init__()
        self._lookup: typing.Dict[cott.UID7, cott.Key] = {
            cott.UID7(bytes.fromhex("02030405060708")): cott.Key(bytes.fromhex("000102030405060708090a0b0c0d0e0f"))
        }

    def get(self, uid: cott.UID7 | bytes) -> typing.Optional[cott.Key]:
        return self._lookup.get(cott.UID7(uid))

    def set(self, uid: cott.UID7 | bytes, key: cott.Key | bytes) -> None:
        self._lookup[cott.UID7(uid)] = cott.Key(key)


@pytest.fixture()
def app() -> typing.Generator[flask.Flask, None, None]:
    """
    Pytest fixture for always starting with a fresh COTT flask server.
    """
    keystore = KeyStore()
    app = cott.server.create_app(keystore=keystore)
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture()
def client(app: flask.Flask) -> flask.testing.FlaskClient:
    """
    Pytest fixture for a client to the COTT flask server
    """
    return app.test_client()


@pytest.fixture()
def runner(app: flask.Flask) -> flask.testing.FlaskCliRunner:
    """
    Pytest fixture required to run unittests on flask server.
    """
    return app.test_cli_runner()


def test_cott_valid(client: flask.testing.FlaskClient) -> None:
    """
    Tests that COTT validation endpoint allows fresh and valid tokens.
    """
    response = client.get("/", query_string={"cott": "AAECAwQFBgcICQoLDA0ODxDbq1lCP77Fp74yxIzhqA4z"})
    assert response.status_code == 200


def test_cott_missing(client: flask.testing.FlaskClient) -> None:
    """
    Tests that COTT validation endpoint detects missing `cott` value.
    """
    response = client.get("/")
    assert response.status_code == 400


def test_cott_syntax_invalid(client: flask.testing.FlaskClient) -> None:
    """
    Tests that COTT validation endpoint detects syntactically invalid `cott` value.
    """
    response = client.get("/", query_string={"cott": "MDA="})
    assert response.status_code == 400


def test_cott_used(client: flask.testing.FlaskClient) -> None:
    """
    Tests that COTT validation endpoint detects previously used COTT objects.
    """
    response = client.get("/", query_string={"cott": "AAECAwQFBgcICQoLDA0ODxDbq1lCP77Fp74yxIzhqA4z"})
    assert response.status_code == 200
    response = client.get("/", query_string={"cott": "AAECAwQFBgcICQoLDA0ODxDbq1lCP77Fp74yxIzhqA4z"})
    assert response.status_code == 429


def test_cott_uid_unknown(client: flask.testing.FlaskClient) -> None:
    """
    Tests that COTT validation endpoint detects COTT UIDs without known AES key.
    """
    response = client.get("/", query_string={"cott": "AAEAAAAAAAAACQoLDA0ODxDbq1lCP77Fp74yxIzhqA4z"})
    assert response.status_code == 404


def test_cott_wrong_key(client: flask.testing.FlaskClient) -> None:
    """
    Tests that COTT validation endpoint detects COTT that was created with invalid AES key.
    """
    response = client.get("/", query_string={"cott": "AAECAwQFBgcICQoLDA0ODxD_____________________"})
    assert response.status_code == 403


def test_keystore() -> None:
    """
    Sanity checks for default class:`cott.server.keystore.KeyStore` implementation.
    """
    keystore = cott.server.keystore.KeyStore()
    assert keystore.get(bytes.fromhex("01020304050607")) == bytes.fromhex("373F5060409BA014B69A627622F23B59")
    keystore.set(bytes.fromhex("01020304050607"), bytes.fromhex("101112131415161718191a1b1c1d1e1f"))
    assert keystore.get(bytes.fromhex("01020304050607")) == bytes.fromhex("101112131415161718191a1b1c1d1e1f")


def test_cache() -> None:
    """
    Sanity checks for default class:`cott.server.cache.Cache` implementation.
    """
    cache = cott.server.cache.Cache()
    token = cott.COTT(bytes.fromhex("0001"), bytes.fromhex("02030405060708"), bytes.fromhex("090a0b0c0d0e0f10"), bytes.fromhex("dbab59423fbec5a7be32c48ce1a80e33"))
    assert not cache.used(token)
    cache.use(token)
    assert cache.used(token)


def test_healthcheck(client: flask.testing.FlaskClient) -> None:
    """
    Tests that healthcheck API returns expected status.
    """
    response = client.get("/healthcheck")
    assert response.json == {"status": "running"}
    assert response.status_code == 200
