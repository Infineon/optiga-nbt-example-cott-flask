# SPDX-FileCopyrightText: 2024 Infineon Technologies AG
# SPDX-License-Identifier: MIT

"""
Main entry point running COTT flask server.
"""
from cott.server import create_app


if __name__ == "__main__":
    app = create_app(debug=True)
    app.run(host="0.0.0.0", debug=True)
