#! /bin/sh
set -e

# cscout or svf
TOOL=$1

if [ $TOOL != "cscout" ] && [ $TOOL != "svf" ]; then
    echo "Error: please give svf or cscout"
    exit 1
fi

cd wanna-build
docker build -t wanna-build .
cd ../buildd
docker build -t buildd .
cd ..

if [ "$TOOL" == "cscout" ]; then
    cd cscout
    docker build -t cscout .
    docker-compose up -d
elif [ "$TOOL" == "svf" ]; then
    cd svf
    docker build -t svf .
    docker-compose up -d
fi
