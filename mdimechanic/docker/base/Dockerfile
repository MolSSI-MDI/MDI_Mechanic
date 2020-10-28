#------------------------------------------------------------#
# Base docker file for the MDI project
#------------------------------------------------------------#

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

ARG MPI_USER=mpiuser
ARG HOME_DIR=/home/${MPI_USER}
ARG SSH_DIR=${HOME_DIR}/.ssh

COPY docker-entrypoint.sh /bin/docker-entrypoint.sh

#------------------------------------------------------------#
# Build the image using a single RUN command
#------------------------------------------------------------#

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        gfortran \
        libmpich-dev \
        make \
        openssh-server \
        python3-dev \
        python3-pip && \
    apt-get clean && \
    apt-get purge && \
    rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* && \
    #
    #--------------------------------------------------------#
    # Ensure that Python 3 is used by default
    #--------------------------------------------------------#
    #
    cd /usr/local/bin && \
    ln -s /usr/bin/python3 python && \
    pip3 install --upgrade pip && \
    rm pip && ln -s /usr/bin/pip3 pip && \
    #
    #--------------------------------------------------------#
    # Enable ssh access for "mpiuser"
    #--------------------------------------------------------#
    #
    adduser --disabled-password --gecos "" ${MPI_USER} && \
    echo "${MPI_USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    mkdir /var/run/sshd && \
    mkdir -p ${SSH_DIR} && \
    #
    #--------------------------------------------------------#
    # Make the entrypoint file executable
    #--------------------------------------------------------#
    #
    chmod +x /bin/docker-entrypoint.sh

#------------------------------------------------------------#
# Set the entrypoint and command
#------------------------------------------------------------#

ENTRYPOINT ["/bin/docker-entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-D"]
