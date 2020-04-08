#! /bin/bash

PROJECTS="anna cdebconf librsync"

sudo rm -rf results.txt callgraphs *.out *.report temp
for p in $PROJECTS; do
    echo "Testing project: $p"
    sudo docker run -it --rm --privileged -v $(pwd)/callgraphs:/callgraphs \
        sbuild-cscout sbuild --apt-update --no-apt-upgrade --no-apt-distupgrade \
        --batch --stats-dir=/var/log/sbuild/stats --dist=buster --arch=amd64 \
        $p 2>&1 | tee $p.out
    sed '/^time_elapsed/d' ./callgraphs/$p/*/*/*/report > $p.report
    if diff "$p.report" "results/$p"; then
        echo "Success: $p" | tee -a results.txt
    else
        echo "#############FAILED: $p#############" | tee -a results.txt
    fi
done
