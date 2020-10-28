#!/bin/sh

cleanup() {
  echo ""
  echo "Deleting generated keys."
  rm mdi_key mdi_key.pub
}

part2() {

  echo "The private key is as follows: "
  echo ""
  sed -e '1d;$d' < mdi_key | tr -d '\n'
  echo ""
  echo ""
}

part1() {

  echo ""
  echo "The public key is as follows: "

  echo ""
  cat mdi_key.pub
  echo ""

  echo "Next, this script will print the private key to the screen.  It is important that the private key is never seen by anyone you don't trust, as anyone who has the private key could make changes to this repo (<insert repo name here>).  After you complete the steps of this script, the private key will be deleted.  The private key will be used by Travis-CI for numerous purposes, but should never again be seen or used by a human.  If you ever suspect that the private key has become compromised, delete the deploy key from github.com and run this script again to generate a new public / private key pair."
  echo ""

  while true; do
    read -p "Are you confident that this terminal window cannot be seen by anyone you don't trust? [y or n]" yn
    case $yn in
        [Yy] ) part2; break;;
        [Nn] ) break;;
        * ) echo "Please answer \"y\" for yes or \"n\" for no.";;
    esac
  done
}

ssh-keygen -t rsa -b 4096 -C "" -f mdi_key -N ''

echo ""
echo ""
echo ""
echo "**************************************************"
echo "* Instructions for preparing GitHub deploy key   *"
echo "**************************************************"
echo ""
echo "This script will help you enable Travis CI to have push access to your GitHub repository."
echo "Doing so is a simple process, but failing to correctly follow the instructions could open security vulnerabilities to this repository."
echo ""



while true; do
    read -p "Are you unprepared to carefully follow these instructions? [y or n]" yn
    case $yn in
        [Yy] ) echo "\nPlease prepare to follow the instructions more carefully."; break;;
        [Nn] ) echo "\nThank you."; part1; break;;
        * ) echo "Please answer \"y\" for yes or \"n\" for no.";;
    esac
done

cleanup
