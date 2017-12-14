#! /bin/bash 
###########################################
#
###########################################

# constants
baseDir=$(cd `dirname "$0"`;pwd)
# functions

# main 
[ -z "${BASH_SOURCE[0]}" -o "${BASH_SOURCE[0]}" = "$0" ] || return
cd $baseDir/..
docker run \
    -m 2g \
    -d \
    -p 10030:10030 \
    --name text-summarize \
    hain/text-summarize:1.0.0 \
    # bash
