# SPDX-FileCopyrightText: 2024 Infineon Technologies AG
# SPDX-License-Identifier: MIT
FROM python:latest

# Install dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
  bash \
  curl \
  git
ENV PIP_ROOT_USER_ACTION=ignore
RUN python -m pip install --upgrade --no-cache-dir pip setuptools
