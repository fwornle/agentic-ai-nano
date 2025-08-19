# Use Ubuntu 24.04 as a base image
# FROM agentic-ai-nano
FROM 799634405166.dkr.ecr.eu-central-1.amazonaws.com/coder/agentic-ai-nano:latest

# ###############################################################################
# # Configure container user
# ARG user=developer
# ARG uid=1000
# ARG gid=1000

# # Enable non-interactive install for package installation
# ENV DEBIAN_FRONTEND=noninteractive

# Use bash for the build
# SHELL ["/bin/bash", "-e", "-u", "-o", "pipefail", "-c"]

# # Remove Ubuntu default user (clashes with new container user)
# RUN userdel -r ubuntu

# ###############################################################################
# # Use Codecraft Ubuntu mirror for apt
# RUN rm -f /etc/apt/sources.list.d/ubuntu.sources
# COPY cc-ubuntu.list /etc/apt/sources.list.d/

# # Install CA certificates (unverified, as there are no certificates yet)
# RUN apt-get -o "Acquire::https::Verify-Peer=false" update \
#     && apt-get -o "Acquire::https::Verify-Peer=false" install -y \
#         ca-certificates \
#     && rm -rf /var/lib/apt/lists/*

# # Install updates
# RUN apt update \
#     && apt upgrade -y

# # Setup timezone
# ENV TZ="Europe/Berlin"
# RUN apt update \
#     && apt install -y \
#         tzdata

# ###############################################################################
# # Install common tools
# RUN apt update \
#     && apt install -y \
#         bash-completion \
#         build-essential \
#         ca-certificates \
#         cmake \
#         curl \
#         git \
#         git-lfs \
#         gnupg \
#         graphviz \
#         htop \
#         jq \
#         moreutils \
#         python3 \
#         python3-pip \
#         python3-venv \
#         rsync \
#         sudo \
#         unzip \
#         vim \
#         wget \
#         zip

# ###############################################################################
# # Use Codecraft pip mirror
# COPY pip.conf /etc/xdg/pip/pip.conf

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

# # ###############################################################################
# # Setup Ollama
# ARG ollama_version="0.6.2"
# ARG ollama_url="${af_server}/external-github-com/ollama/ollama/releases/download/v${ollama_version}/ollama-linux-amd64.tgz"
# RUN curl -L ${ollama_url} | tar -C /usr -xvz
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

# ###############################################################################
# # Create non-root user
# RUN groupadd --gid ${gid} ${user} \
#     && useradd --uid ${uid} --gid ${gid} -m ${user}

# # Add user to sudoers
# RUN echo "${user} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${user} \
#     && chmod 0440 /etc/sudoers.d/${user}

# # Add user to docker
# # RUN usermod -aG docker ${user}

# # Switch to user (-> running as non-root now)
# USER ${user}
# ENV HOME="/home/${user}"

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

# # Create working directory for the user
# ENV WORKDIR="${HOME}/workdir"
# RUN mkdir -p ${WORKDIR}

# # Set bash as entrypoint for the container
# ENTRYPOINT ["/bin/bash"]
