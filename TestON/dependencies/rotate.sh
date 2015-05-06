#!/bin/bash


# NOTE: Taken fnd modified from onos.sh
# pack-rotate-log [packname] "[log-filenames]" [max rotations]
# Note: [packname] and all the log-files specified by [log-filenames]
#       must reside in same dir
# Example:
#  pack="/foo/bar/testlogs"
#  logfiles="/foo/bar/test1.log /foo/bar/test*.log"
#  pack-rotate-log $pack "$logfiles" 5
#   => testlogs.tar.bz2 (will contain test1.log test2.log ...)
#      testlogs.tar.bz2 -> testlogs.1.tar.bz2
#      testlogs.1.tar.bz2 -> testlogs.2.tar.bz2
#      ...
function pack-rotate-log {
  local packname=$1
  local logfiles=$2
  local nr_max=${3:-10}
  local suffix=".tar.bz2"

  # rotate
  for i in `seq $(expr $nr_max - 1) -1 1`; do
    if [ -f ${packname}.${i}${suffix} ]; then
      mv -f -- ${packname}.${i}${suffix} ${packname}.`expr $i + 1`${suffix}
    fi
  done
  if [ -f ${packname}${suffix} ]; then
    mv -- ${packname}${suffix} ${packname}.1${suffix}
  fi

  # pack
  local existing_logfiles=$( ls -1 $logfiles  2>/dev/null | xargs -n1  basename 2>/dev/null)
  if [ ! -z "${existing_logfiles}" ]; then
    tar cjf ${packname}${suffix} -C `dirname ${packname}` -- ${existing_logfiles}
    for word in ${existing_logfiles}
    do
        rm -- `dirname ${packname}`/${word}
    done
   fi
}



#Begin script
#NOTE: This seems to break the TestON summary since it mentions the testname
#echo "Rotating logs for '${1}' test"
base_name=$1
root_dir="/home/admin/packet_captures"
timestamp=`date +%Y_%B_%d_%H_%M_%S`
#Maybe this should be an argument? pack-and-rotate supports that
nr_max=10

pack-rotate-log ${root_dir}'/'${base_name} "${root_dir}/${base_name}*.pcap ${root_dir}/${base_name}*.log*" ${nr_max}
