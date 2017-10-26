#!/bin/bash
cat $1 | while read line
do
    for word in $line
    do
#      python3 create_case_rail.py -t $word
      echo "RUN CASE: $word"
#     ~/samba/bin/smbtorture -t 600 -U admin%Nexenta1! '//192.168.79.227/kek_fs'  $word
	python3.5 create_case_rail.py -t $word

    done
done
