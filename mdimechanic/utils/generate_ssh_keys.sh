#!/bin/sh

if ! test -f "id_rsa.mpi"; then
  ssh-keygen -t rsa -b 4096 -C "" -f id_rsa.mpi -N ''
fi
