#-------------------------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See https://go.microsoft.com/fwlink/?linkid=2090316 for license information.
#-------------------------------------------------------------------------------------------------------------

# To fully customize the contents of this image, use the following Dockerfile instead:
# https://github.com/microsoft/vscode-dev-containers/tree/v0.117.1/containers/ubuntu-18.04-git/.devcontainer/Dockerfile
FROM mcr.microsoft.com/vscode/devcontainers/base:0-ubuntu-18.04

# ** [Optional] Uncomment this section to install additional packages. **
#
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
   && apt-get -y install --no-install-recommends python3.8 python3-pip python3-setuptools
   #
   # Clean up
   # && apt-get autoremove -y \
   # && apt-get clean -y \
   # && rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=dialog

# Setup pipenv
ENV PIPENV_VENV_IN_PROJECT=1
RUN python3.8 -m pip install pipenv
