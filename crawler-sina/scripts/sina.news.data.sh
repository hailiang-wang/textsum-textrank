#! /bin/bash 
###########################################
#
###########################################

# constants
baseDir=$(cd `dirname "$0"`;pwd)
rootDir=$(cd `dirname "$baseDir"`;pwd)

# functions
function curtime() {
    echo `date '+%Y-%m-%d %H:%M:%S'` + " $1"
}

# main 
[ -z "${BASH_SOURCE[0]}" -o "${BASH_SOURCE[0]}" = "$0" ] || return
cd $rootDir/src
filepre=`date '+%Y-%m-%d-%H-%M'`

logfile=$rootDir/log/log.txt
filename="${filepre}.sina.news.utf8.json.txt"
filepath=$rootDir/data/
datafile="${filepath}""${filename}"

#curtime "正在备份上一次数据.."
#if [ -f "$logfile" ]; then
#    mv $logfile ${logfile}.bk
#fi
#
#if [ -f "$datafile" ]; then
#    mv $datafile ${datafile}.bk
#fi

curtime "开始本次爬取"

# curtime '国内[china]...'
# python sina.china.json.py >> $datafile
# echo 'china finish' >>$logfile
curtime '财经[finance]...'
python sina.finance.json.py >> $datafile
echo 'finance finish' >> $logfile
# curtime '军事[mil]...'
# python sina.mil.json.py >> $datafile
# echo 'mil finish' >> $logfile
# curtime '社会[social]...'
# python sina.social.json.py >> $datafile
# echo 'social finish' >> $logfile
# curtime '科技[tech]...'
# python sina.tech.json.py >> $datafile
# echo 'tech finish' >> $logfile
# curtime '视频[video]...'
# python sina.video.json.py >> $datafile
# echo 'video finish' >> $logfile
# curtime '娱乐[ent]...'
# python sina.ent.json.py >> $datafile
# echo 'ent finish' >> $logfile
# curtime '图片[image]...'
# python sina.image.json.py >> $datafile
# echo 'image finish' >> $logfile
# curtime '国际[national]...'
# python sina.national.json.py >> $datafile
# echo 'national finish' >> $logfile
# curtime '滚动[roll]...'
# python sina.roll.json.py >> $datafile
# echo 'roll finish' >> $logfile
# curtime '体育[sport]...'
# python sina.sport.json.py >> $datafile
# echo 'sport finish' >> $logfile
# curtime '排行[top]...'
# python sina.top.json.py >> $datafile
# echo 'top finish' >> $logfile

echo 'done' >> $logfile

curtime "***********************************************************************************"
curtime "                                  爬取完成                                         "
curtime "         数据文件地址：$datafile                                                   "
curtime "         日志文件地址：$logfile                                                    "
curtime "***********************************************************************************"
