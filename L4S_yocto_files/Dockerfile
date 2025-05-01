FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    gawk software-properties-common wget git-core diffstat unzip \
    gcc-multilib build-essential socat sudo passwd libsdl1.2-dev \
    cpio locales file lz4 zstd git python3 python3-pip nano chr-path \
    texinfo

RUN locale-gen en_US.UTF-8 && update-locale LC_ALL=en_US.UTF-8
ARG USERNAME=yocto
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd -g $USER_GID $USERNAME && \
    useradd -m -s /bin/bash -u $USER_UID -g $USER_GID $USERNAME && \
    echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN mkdir -p /workdir && chown $USERNAME:$USERNAME /workdir
WORKDIR /workdir

USER $USERNAME
CMD ["/bin/bash"]
