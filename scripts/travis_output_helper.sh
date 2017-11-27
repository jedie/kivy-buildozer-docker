#!/bin/bash

# https://stackoverflow.com/a/26082445/185510

export PING_SLEEP=20s
export WORKDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export BUILD_OUTPUT=$WORKDIR/build.out

touch $BUILD_OUTPUT

dump_output() {
   echo Tailing the last 500 lines of output:
   tail -500 $BUILD_OUTPUT
}
error_handler() {
  echo ERROR: An error was encountered with the build.
  dump_output
  kill $PING_LOOP_PID
  exit 1
}
# if an error occurs, run our error handler to output a tail of the build
trap 'error_handler' ERR

ping_loop() {
  # set up a repeating loop to send some output to Travis.
  bash -c "while true; do echo \n\n\$(date) - building ...; tail -5 $BUILD_OUTPUT; sleep $PING_SLEEP; done" &
  PING_LOOP_PID=$!
}
