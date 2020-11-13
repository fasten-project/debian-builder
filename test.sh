#!/bin/bash
# Copyright (c) 2018-2020 FASTEN.
#
# This file is part of FASTEN
# (see https://www.fasten-project.eu/).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

RED='\033[0;31m'
GREEN='\033[0;32m'
ORANGE='\033[0;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=====Cleanup====="
echo "sudo rm -rf tests/debian tests/debug tests/output"
sudo rm -rf tests/debian tests/debug tests/output

test_pkg() {
    echo ""
    local pkg_source=$1
    local pkg_input=$2
    local pkg_out=$3
    shift 3
    local pkgs=$@
    echo -e "=====Build ${CYAN}${pkg_source}${NC}====="
    sudo docker run -it --privileged -v $(pwd)/tests/debug:/home/builder/debug \
        -v $(pwd)/tests/debian:/mnt/fasten/debian schaliasos/kafka-cscout \
        --directory /mnt/fasten/debian --debug "$pkg_input"
    echo -e "=====Test ${ORANGE}${pkg_source}${NC}====="
    if f=$(grep "$pkg_source" tests/debug/log_topic.json | grep "success"); then
        echo -e "$pkg_source log_topic tests: ${GREEN}Passed${NC}"
    else
        echo -e "$pkg_source log_topic tests: ${RED}Failed${NC}"
    fi
    echo -e "=====Test ${ORANGE}$pkg_source${NC} Packages====="
    for pkg in ${pkgs[*]}; do
        IFS=,
        read pkg_name pkg_json pkg_expected_json pkg_diff <<< $pkg
        IFS=$' \t\n'
        echo -e "\t=====Test ${PURPLE}${pkg_name}${NC}====="
        if f=$(grep "$pkg_name" tests/debug/produce_topic.json); then
            echo -e "\t$pkg_name produce_topic tests: ${GREEN}Passed${NC}"
        else
            echo -e "\t$pkg_name produce_topic tests: ${RED}Failed${NC}"
        fi
        #if f=$(jq --argfile a $pkg_json --argfile b $pkg_expected_json -n '($a | (.. | arrays) |= sort) as $a | ($b | (.. | arrays) |= sort) as $b | $a == $b'); then
        # Slower but safer
        if f=$(jq --argfile a $pkg_json --argfile b $pkg_expected_json -n 'def post_recurse(f): def r: (f | select(. != null) | r), .; r; def post_recurse: post_recurse(.[]?); ($a | (post_recurse | arrays) |= sort) as $a | ($b | (post_recurse | arrays) |= sort) as $b | $a == $b'); then
            echo -e "\t$pkg_name call graph tests: ${GREEN}Passed${NC}"
        else
            local err=$(diff <(jq -S . $pkg_expected_json) <(jq -S . $pkg_json))
            printf "\t$pkg_name call graph test: ${RED}Failed${NC} (to see the results check $pkg_diff)\n"
            mkdir -p $pkg_out
            echo $err > $pkg_diff
        fi
    done
}

get_pkg_str() {
    local pkg_res=$1
    local pkg_out=$2
    local pkg_name=$3
    local pkg_json=$4
    local json_expected=$pkg_res/$pkg_name.json
    local diff=$pkg_out/${pkg_name}_out
    echo "$pkg_name,$pkg_json,$json_expected,$diff"
}

test_anna() {
    local pkg="anna"
    local pkg_input="{'package': 'anna', 'version': '1.71', 'arch': 'amd64', 'release': 'buster', 'source': 'anna', 'source_version': '1.71', 'date': ''}"
    local pkg_out=tests/output/anna/anna-buster-amd64-1.71
    local pkg_res=tests/results/anna/anna-buster-amd64-1.71
    local anna_json=tests/debian/callgraphs/a/anna/buster/1.71/amd64/file.json
    local anna_json_expected=$pkg_res/anna.json
    local anna_diff=$pkg_out/anna_out
    local pkgs=("$pkg,$anna_json,$anna_json_expected,$anna_diff")
    test_pkg $pkg "$pkg_input" $pkg_out "${pkgs[@]}"
}

test_debianutils() {
    local pkg="debianutils"
    local pkg_input="{'package': 'debianutils', 'version': '4.8.6.1', 'arch': 'amd64', 'release': 'buster', 'source': 'debianutils', 'source_version': '4.8.6.1', 'date': ''}"
    local pkg_out=tests/output/debianutils/debianutils-buster-amd64-4.8.6.1
    local pkg_res=tests/results/debianutils/debianutils-buster-amd64-4.8.6.1
    local debianutils_json_expected=$pkg_res/debianutils.json
    local debianutils_json=tests/debian/callgraphs/d/debianutils/buster/4.8.6.1/amd64/file.json
    local debianutils_diff=$pkg_out/debianutils_out
    local pkgs=("$pkg,$debianutils_json,$debianutils_json_expected,$debianutils_diff")
    test_pkg $pkg "$pkg_input" $pkg_out "${pkgs[@]}"
}

test_diffutils() {
    local pkg="diffutils"
    local pkg_input="{'package': 'diffutils', 'version': '1:3.7-3', 'arch': 'amd64', 'release': 'buster', 'source': 'diffutils', 'source_version': '1:3.7-3', 'date': ''}"
    local pkg_out=tests/output/diffutils/diffutils-buster-amd64-1:3.7-3
    local pkg_res=tests/results/diffutils/diffutils-buster-amd64-1:3.7-3
    local p=$(get_pkg_str "$pkg_res" "$pkg_out" "diffutils" "tests/debian/callgraphs/d/diffutils/buster/1:3.7-3/amd64/file.json")
    local pkgs=("$p")
    test_pkg $pkg "$pkg_input" $pkg_out "${pkgs[@]}"
}

test_zlib() {
    local pkg="zlib"
    local pkg_input="{'package': 'zlib1g-udeb', 'version': '1:1.2.11.dfsg-1', 'arch': 'amd64', 'release': 'buster', 'source': 'zlib', 'source_version': '1:1.2.11.dfsg-1', 'date': ''}"
    local pkg_out=tests/output/zlib/zlib-buster-amd64-1:1.2.11.dsfg-1
    local pkg_res=tests/results/zlib/zlib-buster-amd64-1:1.2.11.dsfg-1
    local lib32z1=$(get_pkg_str "$pkg_res" "$pkg_out" "lib32z1" "tests/debian/callgraphs/l/lib32z1/buster/1:1.2.11.dfsg-1/amd64/file.json")
    local lib32z1_dev=$(get_pkg_str "$pkg_res" "$pkg_out" "lib32z1-dev" "tests/debian/callgraphs/l/lib32z1-dev/buster/1:1.2.11.dfsg-1/amd64/file.json")
    local zlib1g=$(get_pkg_str "$pkg_res" "$pkg_out" "zlib1g" "tests/debian/callgraphs/z/zlib1g/buster/1:1.2.11.dfsg-1/amd64/file.json")
    local zlib1g_dev=$(get_pkg_str "$pkg_res" "$pkg_out" "zlib1g-dev" "tests/debian/callgraphs/z/zlib1g-dev/buster/1:1.2.11.dfsg-1/amd64/file.json")
    local zlib1g_udeb=$(get_pkg_str "$pkg_res" "$pkg_out" "zlib1g-udeb" "tests/debian/callgraphs/z/zlib1g-udeb/buster/1:1.2.11.dfsg-1/amd64/file.json")
    local pkgs=("$lib32z1" "$lib32z1_dev" "$zlib1g" "$zlib1g_dev" "$zlib1g_udeb")
    test_pkg $pkg "$pkg_input" $pkg_out "${pkgs[@]}"
}

test_mutt() {
    local pkg="mutt"
    local pkg_input="{'package': 'mutt', 'version': '1.10.1-2.1', 'arch': 'amd64', 'release': 'buster', 'source': 'mutt', 'source_version': '1.10.1-2.1', 'date': ''}"
    local pkg_out=tests/output/mutt/mutt-buster-amd64-1.10.1-2.1
    local pkg_res=tests/results/mutt/mutt-buster-amd64-1.10.1-2.1
    local p=$(get_pkg_str "$pkg_res" "$pkg_out" "mutt" "tests/debian/callgraphs/m/mutt/buster/1.10.1-2.1/amd64/file.json")
    local pkgs=("$p")
    test_pkg $pkg "$pkg_input" $pkg_out "${pkgs[@]}"
}

test_fdupes() {
    local pkg="fdupes"
    local pkg_input="{'package': 'fdupes', 'version': '1:1.6.1-2', 'arch': 'amd64', 'release': 'buster', 'source': 'fdupes', 'source_version': '1:1.6.1-2', 'date': ''}"
    local pkg_out=tests/output/fdupes/fdupes-buster-amd64-1:1.6.1-2
    local pkg_res=tests/results/fdupes/fdupes-buster-amd64-1:1.6.1-2
    local p=$(get_pkg_str "$pkg_res" "$pkg_out" "fdupes" "tests/debian/callgraphs/f/fdupes/buster/1:1.6.1-2/amd64/file.json")
    local pkgs=("$p")
    test_pkg $pkg "$pkg_input" $pkg_out "${pkgs[@]}"
}

test_sed() {
    local pkg="sed"
    local pkg_input="{'package': 'sed', 'version': '4.7-1', 'arch': 'amd64', 'release': 'buster', 'source': 'sed', 'source_version': '4.7-1', 'date': ''}"
    local pkg_out=tests/output/sed/sed-buster-amd64-4.7-1
    local pkg_res=tests/results/sed/sed-buster-amd64-4.7-1
    local p=$(get_pkg_str "$pkg_res" "$pkg_out" "sed" "tests/debian/callgraphs/s/sed/buster/4.7-1/amd64/file.json")
    local pkgs=("$p")
    test_pkg $pkg "$pkg_input" $pkg_out "${pkgs[@]}"
}

test_cdebconf() {
    local pkg="cdebconf"
    local pkg_input="{'package': 'libdebconfclient0-udeb', 'version': '0.249', 'arch': 'amd64', 'release': 'buster', 'source': 'cdebconf', 'source_version': '0.249', 'date': ''}"
    local pkg_out=tests/output/cdebconf/cdebconf-buster-amd64-0.249
    local pkg_res=tests/results/cdebconf/cdebconf-buster-amd64-0.249
    local cdebconf=$(get_pkg_str "$pkg_res" "$pkg_out" "cdebconf" "tests/debian/callgraphs/c/cdebconf/buster/0.249/amd64/file.json")
    local cdebconf_gtk=$(get_pkg_str "$pkg_res" "$pkg_out" "cdebconf-gtk" "tests/debian/callgraphs/c/cdebconf-gtk/buster/0.249/amd64/file.json")
    local cdebconf_gtk_udeb=$(get_pkg_str "$pkg_res" "$pkg_out" "cdebconf-gtk-udeb" "tests/debian/callgraphs/c/cdebconf-gtk-udeb/buster/0.249/amd64/file.json")
    local cdebconf_newt_udeb=$(get_pkg_str "$pkg_res" "$pkg_out" "cdebconf-newt-udeb" "tests/debian/callgraphs/c/cdebconf-newt-udeb/buster/0.249/amd64/file.json")
    local cdebconf_text_udeb=$(get_pkg_str "$pkg_res" "$pkg_out" "cdebconf-text-udeb" "tests/debian/callgraphs/c/cdebconf-text-udeb/buster/0.249/amd64/file.json")
    local cdebconf_udeb=$(get_pkg_str "$pkg_res" "$pkg_out" "cdebconf-udeb" "tests/debian/callgraphs/c/cdebconf-udeb/buster/0.249/amd64/file.json")
    local libdebconfclient0=$(get_pkg_str "$pkg_res" "$pkg_out" "libdebconfclient0" "tests/debian/callgraphs/l/libdebconfclient0/buster/0.249/amd64/file.json")
    local libdebconfclient0_dev=$(get_pkg_str "$pkg_res" "$pkg_out" "libdebconfclient0-dev" "tests/debian/callgraphs/l/libdebconfclient0-dev/buster/0.249/amd64/file.json")
    local libdebconfclient0_udeb=$(get_pkg_str "$pkg_res" "$pkg_out" "libdebconfclient0-udeb" "tests/debian/callgraphs/l/libdebconfclient0-udeb/buster/0.249/amd64/file.json")
    local pkgs=("$cdebconf" "$cdebconf_gtk" "$cdebconf_gtk_udeb" "$cdebconf_newt_udeb" "$cdebconf_text_udeb" "$cdebconf_udeb" "$libdebconfclient0"  "$libdebconfclient0_dev"  "$libdebconfclient0_udeb")
    test_pkg $pkg "$pkg_input" $pkg_out "${pkgs[@]}"
}

test_libdebian_installer() {
    local pkg="libdebian-installer"
    local pkg_input="{'package': 'libdebian-installer4-udeb', 'version': '0.119', 'arch': 'amd64', 'release': 'buster', 'source': 'libdebian-installer', 'source_version': '0.119', 'date': ''}"
    local pkg_out=tests/output/libdebian-installer/libdebian-installer-buster-amd64-0.119
    local pkg_res=tests/results/libdebian-installer/libdebian-installer-buster-amd64-0.119
    local libdebian_installer4=$(get_pkg_str "$pkg_res" "$pkg_out" "libdebian-installer4" "tests/debian/callgraphs/l/libdebian-installer4/buster/0.119/amd64/file.json")
    local libdebian_installer4_dev=$(get_pkg_str "$pkg_res" "$pkg_out" "libdebian-installer4-dev" "tests/debian/callgraphs/l/libdebian-installer4-dev/buster/0.119/amd64/file.json")
    local libdebian_installer4_udeb=$(get_pkg_str "$pkg_res" "$pkg_out" "libdebian-installer4-udeb" "tests/debian/callgraphs/l/libdebian-installer4-udeb/buster/0.119/amd64/file.json")
    local libdebian_installer_extra4_udeb=$(get_pkg_str "$pkg_res" "$pkg_out" "libdebian-installer-extra4-udeb" "tests/debian/callgraphs/l/libdebian-installer-extra4-udeb/buster/0.119/amd64/file.json")
    local pkgs=("$libdebian_installer4" "$libdebian_installer4_dev" "$libdebian_installer4_udeb" "$libdebian_installer_extra4_udeb")
    test_pkg $pkg "$pkg_input" $pkg_out "${pkgs[@]}"
}

test_time() {
    local pkg_name=$1
    eval test_${pkg_name}
    TOTAL=$(($SECONDS-$P))
    printf "${YELLOW}|----- $pkg_name time elapsed: $TOTAL -----|${NC}\n"
    P=$SECONDS
}

SECONDS=0
P=0
test_time "anna"
test_time "debianutils"
test_time "diffutils"
test_time "zlib"
test_time "mutt"
test_time "fdupes"
test_time "sed"
test_time "cdebconf"
test_time "libdebian_installer"
