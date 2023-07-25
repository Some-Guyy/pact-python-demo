#!/bin/bash
# Vars depending on local machine
set -efo pipefail

HOST_NAME=localhost
PORT=8080
PACT_DIR=tests/contract
LOG_DIR=$PACT_DIR/log

BROKER_HOST_NAME=localhost
BROKER_PORT=1234
BROKER_USERNAME=pactbroker
BROKER_PASSWORD=pactbroker

if [ ! -d $LOG_DIR ]
then
    mkdir $LOG_DIR
fi

# Environment for consumer test
export PROVIDER_VERIFICATION=0

# Run consumer testing
python -m pytest -vv -k test_frontend $PACT_DIR

# Pact creates their own logs in {root}/log/pact.log. This moves it to $LOG_DIR to ensure pact logs stay in $LOG_DIR
if [ -f log/pact.log ]
then
    cat log/pact.log >> $LOG_DIR/pact.log
    rm -rf log
fi
