#! /bin/bash 
###########################################
#
###########################################

# constants
baseDir=$(cd `dirname "$0"`;pwd)
tmpDir=$baseDir/../../tmp
source $baseDir/env.sh
source $baseDir/localrc
vocab=$baseDir/../model/news.w2v.vocab
model=$baseDir/../model/news.w2v.bin
nearby=$baseDir/../model/news.w2v.nearby
# functions

# main 
[ -z "${BASH_SOURCE[0]}" -o "${BASH_SOURCE[0]}" = "$0" ] || return
cd $baseDir/../src
make clean
make
cd $baseDir/../model
cp $vocab words
if [ -f $nearby ]; then
    rm $nearby
fi
echo "build nearby ..."
checklist $model > $nearby