#! /bin/bash
# This is the master script to run all pact tests
set -eufo pipefail

SERVICE=frontend # The service you want to run pact tests for
# PROVIDER_VERSION="1.0.0" # If you wish to use with the pact broker server
PACT_DIR=tests/contract
LOG_DIR=$PACT_DIR/log
DOCKER_LOG_FILE=$LOG_DIR/pact-docker.log
PACT_TEST_IMAGE=pact-test-image
PACT_TEST_CONTAINER=pact-test-container

# We will use these variables to temporarily rename dockerignore because during testing, we want the contents of dockerignore to be built into the image
DOCKERIGNORE=.dockerignore
TEMP_DOCKERIGNORE=.disableddockerignore

# Whenever script exits, return everything back to original state
function cleanup {
    echo "Cleaning up..."

    if [ -f $TEMP_DOCKERIGNORE ]
    then
        echo "Renaming $TEMP_DOCKERIGNORE back to $DOCKERIGNORE" \
        && mv $TEMP_DOCKERIGNORE $DOCKERIGNORE
    fi

    echo "Saving logs to $LOG_DIR" \
    && echo "[$(date)] -- : Running tests in a container" >> $DOCKER_LOG_FILE \
    && docker logs $PACT_TEST_CONTAINER >> $DOCKER_LOG_FILE 2>&1

    echo "Removing container $PACT_TEST_CONTAINER and image $PACT_TEST_IMAGE" \
    && docker rm $PACT_TEST_CONTAINER && docker rmi $PACT_TEST_IMAGE
}
trap cleanup EXIT

# Rename dockerignore so its contents will be built into the image for testing
if [ -f $DOCKERIGNORE ]
then
    mv $DOCKERIGNORE $TEMP_DOCKERIGNORE
fi

docker build --build-arg SERVICE=$SERVICE --target test -t $PACT_TEST_IMAGE . \
&& docker run --platform linux/amd64 --name $PACT_TEST_CONTAINER --volume $(pwd)/$PACT_DIR:/app/$PACT_DIR $PACT_TEST_IMAGE
