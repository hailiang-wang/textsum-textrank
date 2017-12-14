#! /bin/bash 
###########################################
#
###########################################

# constants
baseDir=$(cd `dirname "$0"`;pwd)
TMP_DIR=$baseDir/../../tmp
originFile=$TMP_DIR/zhwiki-latest-pages-articles.0620.chs
postFile=$TMP_DIR/zhwiki-latest-pages-articles.0620.chs.normalized

# functions

# main 
[ -z "${BASH_SOURCE[0]}" -o "${BASH_SOURCE[0]}" = "$0" ] || return
cd $TMP_DIR
python $baseDir/../python/fix_special_symbols.py $originFile
echo Generated $postFile
du -h $postFile