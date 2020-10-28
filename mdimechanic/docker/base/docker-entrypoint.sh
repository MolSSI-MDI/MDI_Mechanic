#!/bin/sh

set -e

cp /MDI_Mechanic/mdimechanic/docker/ssh/config /home/mpiuser/.ssh/config
cp /MDI_Mechanic/mdimechanic/docker/ssh/id_rsa.mpi /home/mpiuser/.ssh/id_rsa
cp /MDI_Mechanic/mdimechanic/docker/ssh/id_rsa.mpi.pub /home/mpiuser/.ssh/id_rsa.pub
cp /MDI_Mechanic/mdimechanic/docker/ssh/id_rsa.mpi.pub /home/mpiuser/.ssh/authorized_keys

chmod 600 /home/mpiuser/.ssh/*
chown -R mpiuser:mpiuser /home/mpiuser/.ssh

exec "$@"
