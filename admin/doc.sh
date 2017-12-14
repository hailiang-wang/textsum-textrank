#! /bin/bash 
###########################################
#
###########################################

# constants
baseDir=$(cd `dirname "$0"`;pwd)
ts=`date +%Y%m%d`
to=文本摘要API文档.$ts.docx

# functions

# main 
[ -z "${BASH_SOURCE[0]}" -o "${BASH_SOURCE[0]}" = "$0" ] || return
cd $baseDir/..
pandoc -f markdown -t docx README.md -o docs/$to
open docs/$to
