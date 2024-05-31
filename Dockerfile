# SPDX-FileCopyrightText: 2024 Infineon Technologies AG
# SPDX-License-Identifier: MIT

FROM python:3.12

# Install dependencies
ENV PIP_ROOT_USER_ACTION=ignore
RUN python3.12 -m pip install --upgrade --no-cache-dir pip setuptools
RUN python3.12 -m pip install --no-cache-dir gunicorn

# Copy code
RUN mkdir -p /usr/src/cott
WORKDIR /usr/src/cott
COPY .git/ .git/
COPY pyproject.toml .
COPY src/ src/
RUN python3.12 -m pip install --no-cache-dir .[server]

# Run server
EXPOSE 5000
ENV FLASK_ENV=productive
CMD exec python3.12 -m gunicorn -w 1 --bind 0.0.0.0:5000 "cott.server:create_app()"
