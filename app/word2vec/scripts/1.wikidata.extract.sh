#! /bin/bash 
###########################################
#
###########################################

# constants
baseDir=$(cd `dirname "$0"`;pwd)
TMP_DIR=$baseDir/../../tmp
originFile=$TMP_DIR/zhwiki-latest-pages-articles.xml.bz2

# functions

# main 
[ -z "${BASH_SOURCE[0]}" -o "${BASH_SOURCE[0]}" = "$0" ] || return
cd $TMP_DIR
WikiExtractor.py -b 5000M \
    -o zhwiki-latest-pages-articles.extracted \
    $originFile
