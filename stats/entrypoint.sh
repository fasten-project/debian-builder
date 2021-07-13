#!/bin/bash

if [ -z "$1" ]; then
    echo "usage: entrypoint.sh input_dir"
fi

INPUT_DIR=$1

echo "path,product,version,sourceFiles,functions,testFiles,testFunctions,autoTests"

for letter in $(ls $INPUT_DIR); do
    for project in $(ls $INPUT_DIR/$letter); do
        for version in $(ls $INPUT_DIR/$letter/$project); do
            target=$INPUT_DIR/$letter/$project/$version
            c_files=$(find $target -type f -name *.[hc])
            test_dirs=$(find $target -type d -name "*test*" -print)
            test_files=$(find $target -type f -name *test*.c -print)
            for test_dir in $test_dirs; do
                test_files="${test_files} $(find $test_dir -type f -name *.c)"
            done
            if [ -f $target/debian/tests/control ]; then
                autoTests="True"
            else
                autoTests="False"
            fi
            test_files=$(echo $test_files | tr ' ' '\n' | sort -u | xargs)
            sourceFiles=$(echo $c_files | wc -w)
            testFiles=$(echo $test_files | wc -w)
            if [ -z "$c_files" ]; then
                functions=0
            else
                functions=$(ctags -x --c-kinds=fp -R $c_files | sort | uniq | wc -l)
            fi
            if [ -z "$test_files" ]; then
                testFunctions=0
            else
                testFunctions=$(ctags -x --c-kinds=fp -R $test_files | sort | uniq | wc -l)
            fi
            echo "$target,$project,$version,$sourceFiles,$functions,$testFiles,$testFunctions,$autoTests"
        done
    done
done
