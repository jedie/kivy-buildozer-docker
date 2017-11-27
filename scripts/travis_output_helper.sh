#!/bin/bash

# based on: https://stackoverflow.com/a/26082445/185510

export PING_SLEEP=20s
export WORKDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export BUILD_OUTPUT=$WORKDIR/build.out

touch $BUILD_OUTPUT

end_output_loop() {
    echo -e "\nTailing the last 500 lines of output:"
    tail -500 $BUILD_OUTPUT
    kill $PING_LOOP_PID
    exit 0
}

error_handler() {
    echo -e "\nERROR: An error was encountered with the build:"
    tail -500 $BUILD_OUTPUT
    kill $PING_LOOP_PID
    exit 1
}

# if an error occurs, run our error handler to output a tail of the build
trap 'error_handler' ERR

start_output_loop() {
    # set up a repeating loop to send some output to Travis.
    bash -c "while true; do echo -e \"\\n\$(date) - building ...\"; tail -5 $BUILD_OUTPUT; sleep $PING_SLEEP; done" &
    PING_LOOP_PID=$!
}