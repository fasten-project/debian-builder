#! /bin/bash
#
# usage: get_callgraphs.sh DIRECTORY DESTINATION
#

DIR=$1
DEST=$2

if [ $# -ne 2 ]; then
    echo "usage: get_callgraphs.sh DIRECTORY DESTINATION"
    exit 1
fi

mkdir -p $DEST

for d  in $DIR/*/ ; do
    if [[ -f "$d/can_cgraph.json" ]] && [[ -s "$d/can_cgraph.json" ]]; then
         cp $d/can_cgraph.json $DEST/$(basename $d).json
    fi
done

