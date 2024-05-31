# SPDX-FileCopyrightText: 2024 Infineon Technologies AG
# SPDX-License-Identifier: MIT

"""
Example implementation of a cryptographic one-time token server.

Builds on :class:`flask.Flask` to showcase how to implement backend service validating COTT data.
"""
__all__ = ["create_app"]

import typing

import flask
from flask_cors import CORS

import cott
from cott.server.cache import Cache
from cott.server.keystore import KeyStore


def create_app(keystore: typing.Optional[cott.IKeyStore] = None, cache: typing.Optional[cott.ICache] = None, debug: bool | None = None) -> flask.Flask:
    """
    Factory method creating main flask application providing COTT server API.

    :param keystore: Optional :class:`cott.IKeyStore` to be used. By default new :class:`cott.server.keystore.KeyStore` will be used.
    :param cache: Optional :class:`cott.ICache` to be used. By default new :class:`cott.server.cache.Cache` will be used.
    :param debug: Optional flag to enable debug mode, disabling CORS checks for local test server. If `None` given, :attr:`app.debug` will be used
    """
    app = flask.Flask(__name__)

    if debug is None:  # pragma: no cover
        debug = app.debug

    #: Keystore used for lookup from UID to matching AES key
    if not keystore:  # pragma: no cover
        keystore = KeyStore()

    #: Cache of previously used COTT values to avoid replay attacks
    if not cache:  # pragma: no cover
        cache = Cache()

    #: CORS utility to allow connections from e.g. OpenAPI client
    if debug:  # pragma: no cover
        CORS(app, origins="*", supports_credentials=False)

    # Add dummy key for OpenAPI to work out-of-the-box
    if debug:  # pragma: no cover
        keystore.set(cott.UID7(bytes.fromhex("02030405060708")), cott.Key(bytes.fromhex("000102030405060708090a0b0c0d0e0f")))

    @app.route("/", methods=["HEAD", "GET"])
    def validate_endpoint() -> flask.Response:
        """
        HTTP endpoint for validating COTT data.

        * Checks query string for encoded `cott` value.
        * Base64 decodes `cott` value.
        * Dissembles `cott` value for easier parsing.
        * Checks COTT MAC using AES key for COTT's UID.
        * Checks that COTT has not been used before.
        """
        # Parse COTT from query string
        if "cott" not in flask.request.args:
            app.logger.warning("Missing 'cott' query parameter")
            return flask.make_response(flask.render_template("index.html"), 400)
        try:
            to_validate = cott.COTT.decode(flask.request.args["cott"])
        except ValueError:
            app.logger.warning("Syntactically invalid COTT data")
            return flask.make_response(flask.render_template("index.html"), 400)

        # Validate COTT
        fresh = True
        status = 200
        key = keystore.get(to_validate.uid)
        if not key:
            app.logger.warning("No key found for UID %s", to_validate.uid.hex())
            status = 404
        elif cache.used(to_validate):
            app.logger.warning("COTT has been used before")
            fresh = False
            status = 429
        elif not to_validate.verify(key):
            app.logger.warning("COTT MAC not matching -> invalid AES key")
            status = 403
        else:
            # Mark COTT as used
            cache.use(to_validate)

        return flask.make_response(flask.render_template("index.html", cott=to_validate, fresh=fresh, key=key), status)

    @app.route("/healthcheck", methods=["HEAD", "GET"])
    def healthcheck_endpoint() -> flask.Response:
        """
        HTTP endpoint for checking current status of REST API.

        * Always returns 201
        """
        return flask.make_response(flask.jsonify({"status": "running"}))

    return app
