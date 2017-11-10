#! /bin/bash 
###########################################
#
###########################################

# constants
baseDir=$(cd `dirname "$0"`;pwd)
TMP_DIR=$baseDir/../../tmp
originFile=$TMP_DIR/zhwiki-latest-pages-articles.extracted/AA/wiki_00
postFile=$TMP_DIR/zhwiki-latest-pages-articles.0620.chs
# functions

# main 
[ -z "${BASH_SOURCE[0]}" -o "${BASH_SOURCE[0]}" = "$0" ] || return
cd $TMP_DIR
opencc -i $originFile  \
    -o $postFile \
    -c $baseDir/../resources/t2s.json