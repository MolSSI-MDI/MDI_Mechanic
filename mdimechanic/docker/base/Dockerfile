#------------------------------------------------------------#
# Base docker file for the MDI project
#------------------------------------------------------------#

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

ARG MPI_USER=mpiuser
ARG HOME_DIR=/home/${MPI_USER}
ARG SSH_DIR=${HOME_DIR}/.ssh

COPY docker-entrypoint.sh /bin/docker-entrypoint.sh

#------------------------------------------------------------#
# Build the image using a single RUN command
#------------------------------------------------------------#

RUN echo 'Acquire::Retries "30";' >> /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::http::Timeout "300";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::ftp::Timeout "300";' >> /etc/apt/apt.conf.d/99timeout && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        gfortran && \
    apt-get clean && \
    apt-get purge && \
    rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/*

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        libmpich-dev && \
    apt-get clean && \
    apt-get purge && \
    rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/*

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        make \
        openssh-server && \
    apt-get clean && \
    apt-get purge && \
    rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/*

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        python3-dev \
        python3-venv \
        python3-pip && \
    apt-get clean && \
    apt-get purge && \
    rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/*

# Create a python virtual environment
RUN python3 -m venv /opt/venv

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

    #
    #--------------------------------------------------------#
    # Ensure that Python 3 is used by default
    #--------------------------------------------------------#
    #
RUN cd /usr/local/bin && \
    ln -s /usr/bin/python3 python && \
    pip3 install --upgrade pip && \
    ln -s /usr/bin/pip3 pip && \
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
