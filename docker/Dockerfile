FROM common.artifactory.cc.bmwgroup.net/external-docker-io/nvidia/cuda:12.9.1-cudnn-devel-ubuntu24.04

###############################################################################
# Configure container user
ARG user=ubuntu
ARG uid=1000
ARG gid=1000

# # Enable non-interactive install for package installation
# ENV DEBIAN_FRONTEND=noninteractive

# # Use bash for the build
SHELL ["/bin/bash", "-e", "-u", "-o", "pipefail", "-c"]

# # # Remove Ubuntu default user (clashes with new container user)
# RUN userdel -r ubuntu

###############################################################################
# Use Codecraft Ubuntu mirror for apt
RUN rm -f /etc/apt/sources.list.d/ubuntu.sources
COPY cc-ubuntu.list /etc/apt/sources.list.d/

# Install CA certificates (unverified, as there are no certificates yet)
RUN apt-get -o "Acquire::https::Verify-Peer=false" update \
    && apt-get -o "Acquire::https::Verify-Peer=false" install -y \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install updates
RUN apt update \
    && apt upgrade -y

# Setup timezone
ENV TZ="Europe/Berlin"
RUN apt update \
    && apt install -y \
        tzdata

###############################################################################
# Install common tools
RUN apt-get update \
    && apt-get install -y \
        bash-completion \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        fzf \
        git \
        git-lfs \
        gnupg \
        graphviz \
        htop \
        iproute2 \
        jq \
        man-db \
        moreutils \
        net-tools \
        nvidia-utils-550 \
        python-is-python3 \
        python3 \
        python3-pip \
        python3-venv \
        rsync \
        ripgrep \
        sudo \
        tmux \
        unzip \
        vim \
        wget \
        zip

# Enable man pages and update the database
RUN yes | unminimize 2>/dev/null || true \
    && mandb

# Add user to sudoers with NOPASSWD
RUN echo "${user} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${user} \
    && chmod 0440 /etc/sudoers.d/${user}

# ###############################################################################
# # Use Codecraft pip mirror
COPY pip.conf /etc/xdg/pip/pip.conf

################################################################################
# Install developer tools
ARG COMMON_AF=https://common.artifactory.cc.bmwgroup.net/artifactory
ARG DDAD_AF=https://ddad.artifactory.cc.bmwgroup.net/artifactory
ARG GITHUB_MIRROR=${COMMON_AF}/external-github-com
ARG NODE_MIRROR="${DDAD_AF}/external-nodejs"

# Install uv (Python package manager and build tool.)
ARG UV_VERSION=0.8.12
RUN curl ${GITHUB_MIRROR}/astral-sh/uv/releases/download/${UV_VERSION}/uv-x86_64-unknown-linux-gnu.tar.gz \
  | tar -xzv -C /usr/local/bin/ --strip-components=1
ENV UV_PYTHON_INSTALL_MIRROR=${GITHUB_MIRROR}/astral-sh/python-build-standalone/releases/download
ENV UV_DEFAULT_INDEX=${COMMON_AF}/api/pypi/external-pypi-org/simple

# Node
ARG NODE_VERSION=22.17.0
RUN cd /tmp && \
    wget "${NODE_MIRROR}/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" && \
    tar -xf node-v${NODE_VERSION}-linux-x64.tar.xz -C /opt && \
    rm node-v${NODE_VERSION}-linux-x64.tar.xz && \
    ln -s /opt/node-v${NODE_VERSION}-linux-x64/bin/node /usr/local/bin/node && \
    ln -s /opt/node-v${NODE_VERSION}-linux-x64/bin/npm /usr/local/bin/npm && \
    ln -s /opt/node-v${NODE_VERSION}-linux-x64/bin/npx /usr/local/bin/npx

# fd
ARG FD_VERSION=10.2.0
RUN cd /tmp && \
    wget ${GITHUB_MIRROR}/sharkdp/fd/releases/download/v${FD_VERSION}/fd-musl_${FD_VERSION}_amd64.deb && \
    dpkg -i fd-musl_${FD_VERSION}_amd64.deb

# gh
ARG GH_VERSION=2.75.0
RUN cd /tmp && \
    wget ${GITHUB_MIRROR}/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_amd64.deb && \
    dpkg -i gh_${GH_VERSION}_linux_amd64.deb

# eza
ARG EZA_VERSION=0.22.0
RUN cd /tmp && \
    wget ${GITHUB_MIRROR}/eza-community/eza/releases/download/v${EZA_VERSION}/eza_x86_64-unknown-linux-gnu.tar.gz && \
    tar -xf eza_x86_64-unknown-linux-gnu.tar.gz -C /usr/local/bin/ && \
    rm eza_x86_64-unknown-linux-gnu.tar.gz

# ruff
RUN UV_TOOL_BIN_DIR=/usr/local/bin/ \
    UV_TOOL_DIR=/usr/local/share/uv/tools/ \
    uv tool install ruff==0.11.2

# llm
RUN UV_TOOL_BIN_DIR=/usr/local/bin/ \
    UV_TOOL_DIR=/usr/local/share/uv/tools/ \
    uv tool install llm==0.27.1

# install bmw certificates
RUN wget https://trustbundle.bmwgroup.net/BMW_Trusted_Certificates_Latest.pem \
    -O /usr/local/share/ca-certificates/BMW_Trusted_Certificates_Latest.crt \
    && update-ca-certificates --fresh

# coding assistant
ARG CA_VERSION=235965d7ad85a09683c6dacada1ef2f4157259ee
RUN cd /tmp && \
    mkdir /opt/coding_assistant && \
    wget ${GITHUB_MIRROR}/msc94/coding_assistant/archive/${CA_VERSION}.tar.gz && \
    tar -C /opt/coding_assistant --strip-components=1 -xf ${CA_VERSION}.tar.gz
RUN echo '#!/bin/bash' > /usr/local/bin/coding-assistant
RUN chmod +x /usr/local/bin/coding-assistant
RUN echo 'export SSL_CERT_FILE=/usr/local/share/ca-certificates/BMW_Trusted_Certificates_Latest.crt'\
    >> /usr/local/bin/coding-assistant
RUN echo 'uv run --project /opt/coding_assistant coding-assistant --no-sandbox --model openai/claude-sonnet-4 --expert-model openai/claude-sonnet-4 "$@"' \
    >> /usr/local/bin/coding-assistant
RUN mkdir -p /opt/coding_assistant && chown ${user}:${user} /opt/coding_assistant

# # Install Python dependencies
# ARG py_reqs="requirements.txt"
# COPY ${py_reqs} .
# RUN python3 -m pip install -r ${py_reqs} \
#     && rm ${py_reqs}

# ###############################################################################
# # Install JFrog CLI (e.g., to access Artifactory)
# ARG af_server="https://common.artifactory.cc.bmwgroup.net/artifactory"
# ARG jf_repo="external-releases-jfrog-io-debian-remote"
# RUN echo "deb [trusted=yes] ${af_server}/${jf_repo} focal contrib" \
#         > /etc/apt/sources.list.d/jfrog.list \
#     && apt-get update \
#     && apt-get install -y \
#         jfrog-cli-v2-jf

# ###############################################################################
# # Install GitHub CLI
# ARG gh_repo="external-cli-github-com-debian"
# RUN echo "deb [trusted=yes] ${af_server}/${gh_repo} focal contrib" \
#         > /etc/apt/sources.list.d/github.list \
#     && apt-get update \
#     && apt-get install -y \
#         gh

# ###############################################################################
# Setup Ollama
ARG ollama_version="0.11.5"
ARG ollama_url="${COMMON_AF}/external-github-com/ollama/ollama/releases/download/v${ollama_version}/ollama-linux-amd64.tgz"
RUN curl -L ${ollama_url} | tar -C /usr -xvz
# ENV OLLAMA_HOST="127.0.0.1:11434"

# # ###############################################################################
# # Setup Docker daemon

# COPY docker/daemon.json /etc/docker/daemon.json
# RUN jq ".proxies.\"http-proxy\" = \"$http_proxy\"" /etc/docker/daemon.json | \
#     sponge /etc/docker/daemon.json
# RUN jq ".proxies.\"https-proxy\" = \"$https_proxy\"" /etc/docker/daemon.json | \
#     sponge /etc/docker/daemon.json
# RUN jq ".proxies.\"no-proxy\" = \"$no_proxy\"" /etc/docker/daemon.json | \
#     sponge /etc/docker/daemon.json

###############################################################################
# # Create non-root user
# RUN groupadd --gid ${gid} ${user} \
#     && useradd --uid ${uid} --gid ${gid} -m ${user}

# Change default shell to bash for the user
RUN chsh -s /bin/bash ${user}

# Add user to sudoers
RUN echo "${user} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${user} \
    && chmod 0440 /etc/sudoers.d/${user}

# fzf bash integration.
RUN echo 'eval "$(fzf --bash)"' >> ${HOME}/.bashrc

# Add user to docker
# RUN usermod -aG docker ${user}

# Switch to user (-> running as non-root now)
USER ${user}
ENV HOME="/home/${user}"

# # Setup Docker client config
# COPY --chown=${uid}:${gid} docker/config.json ${HOME}/.docker/config.json
# RUN jq ".proxies.default.\"httpProxy\" = \"$http_proxy\"" \
#     ${HOME}/.docker/config.json | \
#     sponge ${HOME}/.docker/config.json
# RUN jq ".proxies.default.\"httpsProxy\" = \"$https_proxy\"" \
#     ${HOME}/.docker/config.json | \
#     sponge ${HOME}/.docker/config.json
# RUN jq ".proxies.default.\"noProxy\" = \"$no_proxy\"" \
#     ${HOME}/.docker/config.json | \
#     sponge ${HOME}/.docker/config.json

# llm config
COPY --chown=${uid}:${gid} extra-openai-models.yaml ${HOME}/.config/io.datasette.llm/extra-openai-models.yaml

# Backup the user's home directory before it gets mounted over
RUN sudo mkdir -p /home/${user}-bak \
    && sudo chown ${user}:${user} /home/${user}-bak \
    && cp -r /home/${user}/. /home/${user}-bak/

# Create working directory for the user
# ENV WORKDIR="${HOME}/workdir"
# RUN mkdir -p ${WORKDIR}

# # Set bash as entrypoint for the container
ENTRYPOINT ["/bin/bash"]
