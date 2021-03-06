#!/bin/bash

# This is a Universal Setup
# Just update the settings under "Configurable parameters"

# Configurable parameters
TEST_NAME="vfs_stress"
SOURCE_DIR=/home/vastdata/venus/qa/$TEST_NAME
DESTINATION_DIR_DEFAULT=/qa/$TEST_NAME
# End of configurable parameters

DESTINATION_DIR=$1
SUCCESS=1
[ -z $1 ] && DESTINATION_DIR=$DESTINATION_DIR_DEFAULT

echo "Setting up the '$TEST_NAME' test under '$DESTINATION_DIR'"
\sudo mkdir -p -m777 $DESTINATION_DIR
echo "Copying files"
\cp -rf $SOURCE_DIR/* $DESTINATION_DIR || SUCCESS=0
\sudo mkdir -m755 $DESTINATION_DIR/logs || SUCCESS=0
\sudo chown vastdata:vastdata $DESTINATION_DIR/logs || SUCCESS=0

sudo yum install -y redis || SUCCESS=0

sudo yum -y install https://centos7.iuscommunity.org/ius-release.rpm || SUCCESS=0
sudo yum -y install python36u || SUCCESS=0
sudo yum -y install python36u-pip || SUCCESS=0

sudo pip3.6 install redis || SUCCESS=0
sudo pip3.6 install zmq || SUCCESS=0
sudo pip3.6 install treelib || SUCCESS=0
sudo pip3.6 install paramiko || SUCCESS=0
sudo pip3.6 install xxhash || SUCCESS=0
sudo pip3.6 install pexpect || SUCCESS=0

echo -n "$TEST_NAME setup "
if [ $SUCCESS = 1 ]
then
    echo "Completed successfully"
else
    echo "FAILED"
    exit 1
fi