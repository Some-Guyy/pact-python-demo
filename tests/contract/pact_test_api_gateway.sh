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
python -m pytest -vv -k test_api_gateway $PACT_DIR

# Environment for provider test
export PACT_DO_NOT_TRACK=true # This prevents Pact from tracking events anonymously for usage statistics
export PROVIDER_VERIFICATION=1 # To let service know that it is in verification

# Provider state settings
CONSUMER=frontend
PROVIDER=api_gateway
PROVIDER_STATE_MODULE=$(echo $PACT_DIR | tr / .).provider_state_api_gateway # If no provider state just use the provider itself
PROVIDER_STATE_PATH=_pact/provider_states

# Run the FastAPI server, using the pact_provider.py as the app to be able to
# inject the provider_states endpoint
uvicorn $PROVIDER_STATE_MODULE:app --port $PORT & &>/dev/null
FASTAPI_PID=$!

# Make sure the FastAPI server is stopped when finished to avoid blocking the port
function teardown {
  echo "Tearing down FastAPI server ${FASTAPI_PID}"
  kill -9 $FASTAPI_PID
}
trap teardown EXIT

# Wait a little in case FastAPI isn't quite ready
sleep 1

VERSION=$1
if [ -x $VERSION ];
then
    echo "Validating provider locally"

    pact-verifier --provider-base-url=http://$HOST_NAME:$PORT \
        --provider-states-setup-url=http://$HOST_NAME:$PORT/$PROVIDER_STATE_PATH \
        $PACT_DIR/pacts/$CONSUMER-$PROVIDER.json
else
    echo "Validating against Pact Broker"

    pact-verifier --provider-base-url=http://$HOST_NAME:$PORT \
        --provider-app-version $VERSION \
        --pact-url="http://$BROKER_HOST_NAME:$BROKER_PORT/pacts/provider/$PROVIDER/consumer/$CONSUMER/latest" \
        --pact-broker-username $BROKER_USERNAME \
        --pact-broker-password $BROKER_PASSWORD \
        --publish-verification-results \
        --provider-states-setup-url=http://$HOST_NAME:$PORT/$PROVIDER_STATE_PATH
fi

# Pact creates their own logs in {root}/log/pact.log. This moves it to $LOG_DIR to ensure pact logs stay in $LOG_DIR
if [ -f log/pact.log ]
then
    cat log/pact.log >> $LOG_DIR/pact.log
    rm -rf log
fi
