#!/bin/sh

if ! brew ls --versions apache-arrow >/dev/null 2>&1; then
    brew install apache-arrow
fi

if ! brew ls --versions cmake >/dev/null 2>&1; then
    brew install cmake
fi

pip install -r requirements.txt
