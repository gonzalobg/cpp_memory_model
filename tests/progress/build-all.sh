#!/bin/bash

COMPILER="clang++"
CC_FLAGS="-Wall -Werror -std=c++2a -pthread"
TEST_DIR=`dirname $0`
TIMEOUT=timeout

# Workarounds for macOS. You'll need to do `brew install coreutils` and `brew install llvm`
if [ "$(uname)" == "Darwin" ]; then
    LDFLAGS+="-L/opt/homebrew/opt/llvm/lib"
    CC_FLAGS+=" -I/opt/homebrew/opt/llvm/include";
    PATH="/opt/homebrew/opt/llvm/bin:$PATH";
    TIMEOUT=gtimeout;
fi

for f in `ls $TEST_DIR/*.cc`; do
    echo -n $f
    $COMPILER $CC_FLAGS $f -o "${f%.*}";
    if [ "$1" == "run" ]; then
        $TIMEOUT 5 ./${f%.*};
        if [ $? -ne 0 ]; then
            echo -n ": Timeout.";
        fi
    fi
    echo ""
    rm -f "${f%.*}"
done
